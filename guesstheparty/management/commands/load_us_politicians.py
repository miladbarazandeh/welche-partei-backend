import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from guesstheparty.game_config import get_country_config, get_game_party
from guesstheparty.models import Politician

DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "out"
    / "full_optimized"
    / "politicians_verified_free.csv"
)
US_CONFIG = get_country_config("us")


def build_parliament_label(row):
    chamber = row.get("chamber", "")
    jurisdiction_name = row.get("jurisdiction_name", "").strip()
    district = (row.get("district") or "").strip()

    if chamber == "federal-senate":
        return "U.S. Senate"
    if chamber == "federal-house":
        return "U.S. House of Representatives"
    if chamber == "state-senate":
        base = f"{jurisdiction_name} State Senate"
    elif chamber == "state-house":
        base = f"{jurisdiction_name} State House"
    else:
        base = f"{jurisdiction_name} Legislature"

    if district:
        return f"{base} · District {district}"
    return base


class Command(BaseCommand):
    help = "Load US politicians from the verified CSV generated in out/full_optimized"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default=str(DEFAULT_CSV_PATH),
            help="Path to politicians_verified_free.csv",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"]).resolve()
        if not csv_path.exists():
            self.stderr.write(f"File not found: {csv_path}")
            return

        created = updated = skipped = 0

        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source_identifier = (row.get("person_id") or "").strip()
                raw_party = (row.get("party") or "").strip()
                game_party = get_game_party(US_CONFIG, raw_party)
                image_url = (row.get("image_url") or "").strip()
                if not source_identifier or not raw_party or not game_party or not image_url:
                    skipped += 1
                    continue

                _, was_created = Politician.objects.update_or_create(
                    source_identifier=source_identifier,
                    defaults={
                        "country": "US",
                        "source_dataset": (row.get("source_dataset") or "").strip(),
                        "name": (row.get("name") or "").strip(),
                        "party": raw_party,
                        "parliament": build_parliament_label(row),
                        "image_url": image_url,
                        "image_page_url": (row.get("image_page_url") or "").strip(),
                        "license_short_name": (row.get("license_short_name") or "").strip(),
                        "license_url": (row.get("license_url") or "").strip(),
                        "attribution_text": (row.get("attribution_text") or "").strip(),
                        "author_name": (row.get("author_name") or "").strip(),
                        "author_url": (row.get("author_url") or "").strip(),
                        "credit_text": (row.get("credit_text") or "").strip(),
                        "credit_url": (row.get("credit_url") or "").strip(),
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        total = Politician.objects.filter(country="US").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, "
                f"Skipped: {skipped}, Total US politicians in DB: {total}"
            )
        )
