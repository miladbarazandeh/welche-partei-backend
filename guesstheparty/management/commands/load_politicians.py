import json
from pathlib import Path

from django.core.management.base import BaseCommand

from guesstheparty.models import Politician

# Normalize raw party labels from abgeordnetenwatch to canonical game parties.
# The soft-hyphen (­) appears in "BÜNDNIS 90/­DIE GRÜNEN" from the API.
PARTY_MAP = {
    'SPD': 'SPD',
    'CDU': 'CDU/CSU',
    'CSU': 'CDU/CSU',
    'CDU/CSU': 'CDU/CSU',
    'BÜNDNIS 90/­DIE GRÜNEN': 'Grüne',
    'GRÜNE': 'Grüne',
    'AfD': 'AfD',
    'Die Linke': 'Die Linke',
    'DIE LINKE': 'Die Linke',
    'FDP': 'FDP',
}

JSON_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'politician_data' / 'politicians.json'


class Command(BaseCommand):
    help = 'Load politicians from politician_data/politicians.json into the database'

    def handle(self, *args, **options):
        if not JSON_PATH.exists():
            self.stderr.write(f'File not found: {JSON_PATH}')
            return

        with open(JSON_PATH, encoding='utf-8') as f:
            data = json.load(f)

        created = updated = skipped = 0

        for p in data:
            party = PARTY_MAP.get(p.get('party', ''))
            if not party:
                skipped += 1
                continue
            if not p.get('image_local'):
                skipped += 1
                continue

            _, was_created = Politician.objects.update_or_create(
                abgeordnetenwatch_id=p['id'],
                defaults={
                    'name': p['name'],
                    'party': party,
                    'parliament': p.get('parliament', ''),
                    'image_url': p.get('image_url', ''),
                    'image_local': p.get('image_local', ''),
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        total = Politician.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Created: {created}, Updated: {updated}, Skipped: {skipped}, Total in DB: {total}'
            )
        )
