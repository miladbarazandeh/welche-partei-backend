from django.db import migrations, models

PARTY_LEANING = {
    'SPD': 'left',
    'Grüne': 'left',
    'Die Linke': 'left',
    'CDU/CSU': 'right',
    'FDP': 'right',
    'AfD': 'right',
}


def backfill_spectrum_correct(apps, schema_editor):
    Answer = apps.get_model('guesstheparty', 'Answer')
    answers = Answer.objects.select_related('politician').filter(is_spectrum_correct__isnull=True)
    bulk = []
    for answer in answers.iterator():
        actual_leaning = PARTY_LEANING.get(answer.politician.party)
        guessed_leaning = PARTY_LEANING.get(answer.guessed_party)
        answer.is_spectrum_correct = actual_leaning == guessed_leaning and actual_leaning is not None
        bulk.append(answer)
        if len(bulk) == 500:
            Answer.objects.bulk_update(bulk, ['is_spectrum_correct'])
            bulk = []
    if bulk:
        Answer.objects.bulk_update(bulk, ['is_spectrum_correct'])


class Migration(migrations.Migration):

    dependencies = [
        ('guesstheparty', '0003_alter_politician_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='is_spectrum_correct',
            field=models.BooleanField(null=True),
        ),
        migrations.RunPython(backfill_spectrum_correct, migrations.RunPython.noop),
    ]
