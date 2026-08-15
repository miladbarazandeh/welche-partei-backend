from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("welchepartei", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="position",
            name="source_quote_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="position",
            name="party_rationale_en",
            field=models.TextField(blank=True),
        ),
    ]
