from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guesstheparty", "0007_multicountry_support"),
    ]

    operations = [
        migrations.AddField(
            model_name="politician",
            name="thumbline_url",
            field=models.URLField(blank=True, default="", max_length=1000),
            preserve_default=False,
        ),
    ]
