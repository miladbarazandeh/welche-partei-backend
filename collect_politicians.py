#!/usr/bin/env python3
"""
Collect German politician data from abgeordnetenwatch.de API.

Output:
  politician_data/politicians.json   — metadata for all unique politicians
  politician_data/images/<id>.jpg    — downloaded profile photos

Usage:
  pip install requests
  python collect_politicians.py
"""

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE_URL = "https://www.abgeordnetenwatch.de/api/v2"
SITE_BASE = "https://www.abgeordnetenwatch.de"
OUTPUT_DIR = Path("politician_data")
IMAGES_DIR = OUTPUT_DIR / "images"
OUTPUT_JSON = OUTPUT_DIR / "politicians.json"

CONCURRENT_WORKERS = 8
REQUEST_DELAY = 0.15   # seconds between requests per thread

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; guesstheparty-data-collector/1.0)"
})

EU_PARLIAMENT_ID = 1
OG_IMAGE_RE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE)
FRACTION_SUFFIX_RE = re.compile(r'\s*\([^)]+\)\s*$')


def get(path, params=None):
    resp = SESSION.get(f"{BASE_URL}/{path}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def clean_party(fraction_label):
    """'SPD (Bundestag 2025 - 2029)' → 'SPD'"""
    if not fraction_label:
        return None
    return FRACTION_SUFFIX_RE.sub("", fraction_label).strip()


def fetch_current_period_ids():
    """Return {parliament_label: period_id} for all German parliaments."""
    data = get("parliaments")
    periods = {}
    for parliament in data["data"]:
        if parliament["id"] == EU_PARLIAMENT_ID:
            continue
        current = parliament.get("current_project")
        if current:
            periods[parliament["label"]] = current["id"]
    print(f"Found {len(periods)} German parliaments")
    return periods


def fetch_mandates_for_period(parliament_label, period_id):
    """Fetch all mandates for one parliament period, return unique politicians."""
    politicians = {}
    page = 0
    while True:
        data = get("candidacies-mandates", {"parliament_period": period_id, "page": page})
        items = data.get("data") or []
        if not items:
            break

        for item in items:
            pol = item.get("politician") or {}
            pid = pol.get("id")
            if not pid or pid in politicians:
                continue

            fraction = None
            fm = item.get("fraction_membership") or []
            if fm:
                raw = (fm[0].get("fraction") or {}).get("label")
                fraction = clean_party(raw)

            profile_url = pol.get("abgeordnetenwatch_url")

            politicians[pid] = {
                "id": pid,
                "name": pol.get("label"),
                "party": fraction,
                "parliament": parliament_label,
                "profile_url": profile_url,
                "image_url": None,
                "image_local": None,
            }

        meta = data.get("meta", {}).get("result", {})
        if meta.get("range_end", 0) >= meta.get("total", 0) or len(items) < 100:
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    return politicians


def scrape_image_url(profile_url):
    """Fetch a politician's profile page and extract the og:image URL."""
    if not profile_url:
        return None
    try:
        resp = SESSION.get(profile_url, timeout=15)
        resp.raise_for_status()
        match = OG_IMAGE_RE.search(resp.text)
        if match:
            url = match.group(1)
            if "politicians-profile-pictures" in url:
                return url
    except Exception:
        pass
    return None


def download_image(url, dest_path):
    try:
        resp = SESSION.get(url, timeout=20, stream=True)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as exc:
        print(f"  [warn] download failed: {exc}", file=sys.stderr)
        return False


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)

    # Step 1: parliament → current period IDs
    period_ids = fetch_current_period_ids()

    # Step 2: collect all unique politicians across all parliaments
    all_politicians = {}
    for parl_label, period_id in period_ids.items():
        print(f"  [{parl_label}] period {period_id} ...", end=" ", flush=True)
        pols = fetch_mandates_for_period(parl_label, period_id)
        new = {pid: p for pid, p in pols.items() if pid not in all_politicians}
        all_politicians.update(new)
        print(f"{len(pols)} politicians ({len(new)} new, {len(all_politicians)} total)")
        time.sleep(REQUEST_DELAY)

    politicians = list(all_politicians.values())
    print(f"\n{len(politicians)} unique politicians collected")

    # Step 3: scrape og:image from profile pages (concurrent)
    with_url = [p for p in politicians if p["profile_url"]]
    print(f"Scraping profile pages for photos ({len(with_url)} politicians, {CONCURRENT_WORKERS} threads)...")

    def scrape_one(pol):
        time.sleep(REQUEST_DELAY)
        return pol["id"], scrape_image_url(pol["profile_url"])

    id_to_pol = {p["id"]: p for p in politicians}
    done = 0
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = {executor.submit(scrape_one, p): p["id"] for p in with_url}
        for future in as_completed(futures):
            pid, image_url = future.result()
            if image_url:
                id_to_pol[pid]["image_url"] = image_url
            done += 1
            if done % 100 == 0:
                found = sum(1 for p in politicians if p["image_url"])
                print(f"  {done}/{len(with_url)} scraped, {found} photos found")

    with_photo = [p for p in politicians if p["image_url"]]
    print(f"Photos found: {len(with_photo)}/{len(politicians)}")

    # Step 4: download images
    print(f"\nDownloading {len(with_photo)} photos...")
    for i, pol in enumerate(with_photo, 1):
        url = pol["image_url"]
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
        if ext not in ("jpg", "jpeg", "png", "webp"):
            ext = "jpg"
        dest = IMAGES_DIR / f"{pol['id']}.{ext}"

        if dest.exists():
            pol["image_local"] = str(dest)
            continue

        if i % 100 == 0:
            print(f"  {i}/{len(with_photo)}")

        if download_image(url, dest):
            pol["image_local"] = str(dest)
        time.sleep(0.1)

    # Step 5: save JSON (drop profile_url, it's not needed downstream)
    for p in politicians:
        p.pop("profile_url", None)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(politicians, f, ensure_ascii=False, indent=2)

    downloaded = sum(1 for p in politicians if p["image_local"])
    print(f"\nDone.")
    print(f"  {len(politicians)} politicians")
    print(f"  {len(with_photo)} with photo URL, {downloaded} downloaded")
    print(f"  {OUTPUT_JSON}")
    print(f"  {IMAGES_DIR}/")


if __name__ == "__main__":
    main()
