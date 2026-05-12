# Generated manually for multi-country support.

from django.db import migrations, models


def backfill_politicians(apps, schema_editor):
    Politician = apps.get_model("guesstheparty", "Politician")

    batch = []
    for politician in Politician.objects.all().iterator():
        politician.country = politician.country or "DE"
        politician.source_identifier = (
            f"abgeordnetenwatch:{politician.abgeordnetenwatch_id}"
            if politician.abgeordnetenwatch_id is not None
            else politician.source_identifier
        )
        if not politician.source_dataset:
            politician.source_dataset = "abgeordnetenwatch"
        batch.append(politician)
        if len(batch) == 500:
            Politician.objects.bulk_update(
                batch,
                ["country", "source_identifier", "source_dataset"],
            )
            batch = []

    if batch:
        Politician.objects.bulk_update(
            batch,
            ["country", "source_identifier", "source_dataset"],
        )


def backfill_user_sessions(apps, schema_editor):
    UserSession = apps.get_model("guesstheparty", "UserSession")
    UserSession.objects.filter(country="").update(country="DE")
    UserSession.objects.filter(country__isnull=True).update(country="DE")


class Migration(migrations.Migration):

    dependencies = [
        ("guesstheparty", "0006_politician_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="politician",
            name="country",
            field=models.CharField(
                choices=[("DE", "Germany"), ("US", "United States")],
                default="DE",
                max_length=2,
            ),
        ),
        migrations.AddField(
            model_name="politician",
            name="source_identifier",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="politician",
            name="source_dataset",
            field=models.CharField(blank=True, default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="image_page_url",
            field=models.URLField(blank=True, default="", max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="license_short_name",
            field=models.CharField(blank=True, default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="license_url",
            field=models.URLField(blank=True, default="", max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="attribution_text",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="author_name",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="author_url",
            field=models.URLField(blank=True, default="", max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="credit_text",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="politician",
            name="credit_url",
            field=models.URLField(blank=True, default="", max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="usersession",
            name="country",
            field=models.CharField(
                choices=[("DE", "Germany"), ("US", "United States")],
                default="DE",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="guessed_party",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="politician",
            name="abgeordnetenwatch_id",
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="politician",
            name="image_url",
            field=models.URLField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name="politician",
            name="parliament",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="politician",
            name="party",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="politician",
            name="reference",
            field=models.SlugField(blank=True, max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="usersession",
            name="session_key",
            field=models.CharField(db_index=True, max_length=40),
        ),
        migrations.RunPython(backfill_politicians, migrations.RunPython.noop),
        migrations.RunPython(backfill_user_sessions, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name="politician",
            index=models.Index(fields=["country", "party"], name="guessthepar_country_party_idx"),
        ),
        migrations.AddConstraint(
            model_name="usersession",
            constraint=models.UniqueConstraint(
                fields=("session_key", "country"),
                name="unique_session_per_country",
            ),
        ),
    ]
