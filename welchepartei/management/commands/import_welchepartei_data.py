import json
from pathlib import Path

from django.core.cache import cache
from django.core.management.base import BaseCommand

from welchepartei.models import Issue, Party, Position

DEFAULT_FIXTURE = str(
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "welchepartei_data.json"
)

ANSWER_SLOT = {
    "support": 0, "yes": 0, "agree": 0,
    "oppose": 1, "no": 1, "disagree": 1,
}


class Command(BaseCommand):
    help = "Import party positions from the bundled JSON fixture into PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=DEFAULT_FIXTURE,
            help="Path to fixture JSON (default: %(default)s)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing positions before importing",
        )

    def handle(self, *args, **options):
        fixture_path = Path(options["fixture"]).resolve()

        if not fixture_path.exists():
            self.stderr.write(self.style.ERROR(f"Fixture not found: {fixture_path}"))
            return

        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        parties   = data["parties"]
        issues    = data["issues"]
        positions = data["positions"]

        if options["clear"]:
            count, _ = Position.objects.all().delete()
            self.stdout.write(f"  Cleared {count} existing positions")

        # ── Parties ───────────────────────────────────────────────────────────
        for p in parties:
            Party.objects.update_or_create(
                id=p["id"],
                defaults={k: v for k, v in p.items() if k != "id"},
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(parties)} parties upserted"))

        # Remove parties no longer in the fixture (e.g. HEIMAT, dropped because
        # it runs district-only lists). Cascades to their positions.
        stale_parties, _ = Party.objects.exclude(id__in=[p["id"] for p in parties]).delete()
        if stale_parties:
            self.stdout.write(self.style.WARNING(f"  Removed {stale_parties} stale party/position rows no longer in the fixture"))

        # ── Issues ────────────────────────────────────────────────────────────
        for iss in issues:
            Issue.objects.update_or_create(
                id=iss["id"],
                defaults={k: v for k, v in iss.items() if k != "id"},
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(issues)} issues upserted"))

        # Remove issues no longer in the fixture (e.g. the old federal-flavored
        # questions, kita-provider-model, hospital-ownership). Cascades to
        # their positions — a plain update_or_create loop never deletes rows
        # that were removed from the fixture, so without this, retired issues
        # and their stale positions linger in the DB forever.
        stale_issues, _ = Issue.objects.exclude(id__in=[i["id"] for i in issues]).delete()
        if stale_issues:
            self.stdout.write(self.style.WARNING(f"  Removed {stale_issues} stale issue/position rows no longer in the fixture"))

        # ── Positions ─────────────────────────────────────────────────────────
        valid_party_ids = {p["id"] for p in parties}
        valid_issue_ids = {i["id"] for i in issues}

        imported = skipped = 0
        for pos in positions:
            party_id = pos["party_id"]
            issue_id = pos["issue_id"]
            if party_id not in valid_party_ids or issue_id not in valid_issue_ids:
                skipped += 1
                continue
            slot = ANSWER_SLOT.get(pos.get("answer_value", "").lower(), 2)
            Position.objects.update_or_create(
                party_id=party_id,
                issue_id=issue_id,
                defaults={
                    "answer_value":      pos.get("answer_value", ""),
                    "answer_slot":       slot,
                    "source_quote":      pos.get("source_quote", ""),
                    "source_quote_en":   pos.get("source_quote_en", ""),
                    "party_rationale":   pos.get("party_rationale", ""),
                    "party_rationale_en":pos.get("party_rationale_en", ""),
                    "source_url":        pos.get("source_url", ""),
                    "source_locator":    pos.get("source_locator", ""),
                },
            )
            imported += 1

        self.stdout.write(self.style.SUCCESS(
            f"  {imported} positions imported, {skipped} skipped (unknown party/issue)"
        ))

        # Remove positions whose (party, issue) pair is no longer in the
        # fixture, even though the party and issue themselves still exist
        # (e.g. a sourced quote was retracted/replaced rather than the whole
        # issue being dropped). Without this, a stale position for an
        # otherwise-valid party/issue pair would never get cleaned up.
        valid_pairs = {(pos["party_id"], pos["issue_id"]) for pos in positions}
        stale_positions = 0
        for row in Position.objects.select_related("party", "issue").all():
            if (row.party_id, row.issue_id) not in valid_pairs:
                row.delete()
                stale_positions += 1
        if stale_positions:
            self.stdout.write(self.style.WARNING(f"  Removed {stale_positions} stale position rows no longer in the fixture"))

        cache.delete("welchepartei:data")
        self.stdout.write(self.style.SUCCESS("  Cache cleared."))
        self.stdout.write(self.style.SUCCESS("Done."))
