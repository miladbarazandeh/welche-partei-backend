from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welchepartei', '0003_issue_en_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizsession',
            name='pre_quiz_party',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='quizsession',
            name='post_quiz_party',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
