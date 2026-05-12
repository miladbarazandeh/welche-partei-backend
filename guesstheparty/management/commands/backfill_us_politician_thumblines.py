import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from guesstheparty.models import Politician

DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "out"
    / "full_optimized"
    / "politicians_verified_free.csv"
)


class Command(BaseCommand):
    help = "Backfill thumbline_url for existing US politicians from the verified CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default=str(DEFAULT_CSV_PATH),
            help="Path to politicians_verified_free.csv",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of politicians to update per bulk_update call.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace existing non-empty thumbline_url values.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"]).resolve()
        if not csv_path.exists():
            self.stderr.write(f"File not found: {csv_path}")
            return

        batch_size = max(1, options["batch_size"])
        overwrite = options["overwrite"]

        thumbline_by_source_identifier = {}
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source_identifier = (row.get("person_id") or "").strip()
                thumbline_url = (row.get("image_url") or "").strip()
                if source_identifier and thumbline_url:
                    thumbline_by_source_identifier[source_identifier] = thumbline_url

        if not thumbline_by_source_identifier:
            self.stderr.write("No usable thumbnail rows found in CSV.")
            return

        matched = updated = unchanged = 0
        seen_identifiers = set()
        batch = []

        queryset = Politician.objects.filter(
            country="US",
            source_identifier__in=thumbline_by_source_identifier,
        ).only("id", "source_identifier", "thumbline_url")

        for politician in queryset.iterator():
            source_identifier = politician.source_identifier or ""
            seen_identifiers.add(source_identifier)
            matched += 1

            thumbline_url = thumbline_by_source_identifier[source_identifier]
            if politician.thumbline_url == thumbline_url:
                unchanged += 1
                continue
            if politician.thumbline_url and not overwrite:
                unchanged += 1
                continue

            politician.thumbline_url = thumbline_url
            batch.append(politician)
            if len(batch) == batch_size:
                Politician.objects.bulk_update(batch, ["thumbline_url"])
                updated += len(batch)
                batch = []

        if batch:
            Politician.objects.bulk_update(batch, ["thumbline_url"])
            updated += len(batch)

        missing_in_db = len(thumbline_by_source_identifier) - len(seen_identifiers)
        total_us = Politician.objects.filter(country="US").count()

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Done. Matched: {matched}, Updated: {updated}, "
                    f"Unchanged: {unchanged}, Missing in DB: {missing_in_db}, "
                    f"Total US politicians in DB: {total_us}"
                )
            )
        )
