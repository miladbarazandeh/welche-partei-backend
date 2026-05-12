import json
from pathlib import Path

from django.core.management.base import BaseCommand

from guesstheparty.game_config import get_country_config, get_game_party
from guesstheparty.models import Politician

JSON_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'politician_data' / 'politicians.json'
DE_CONFIG = get_country_config("de")


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
            raw_party = (p.get('party') or '').strip()
            if not get_game_party(DE_CONFIG, raw_party):
                skipped += 1
                continue
            if not p.get('image_local'):
                skipped += 1
                continue

            _, was_created = Politician.objects.update_or_create(
                abgeordnetenwatch_id=p['id'],
                defaults={
                    'country': 'DE',
                    'source_identifier': f"abgeordnetenwatch:{p['id']}",
                    'source_dataset': 'abgeordnetenwatch',
                    'name': p['name'],
                    'party': raw_party,
                    'parliament': p.get('parliament', ''),
                    'image_url': p.get('image_url', ''),
                    'image_local': p.get('image_local', ''),
                    'image_page_url': p.get('image_page_url', ''),
                    'license_short_name': p.get('license_short_name', ''),
                    'license_url': p.get('license_url', ''),
                    'attribution_text': p.get('attribution_text', ''),
                    'author_name': p.get('author_name', ''),
                    'author_url': p.get('author_url', ''),
                    'credit_text': p.get('credit_text', ''),
                    'credit_url': p.get('credit_url', ''),
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
