from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guesstheparty", "0009_alter_politician_author_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersession",
            name="name",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
