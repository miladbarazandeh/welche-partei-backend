from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("welchepartei", "0002_position_en_fields")]

    operations = [
        migrations.AddField(model_name="issue", name="label_en",         field=models.CharField(max_length=200, blank=True)),
        migrations.AddField(model_name="issue", name="question_text_en", field=models.TextField(blank=True)),
        migrations.AddField(model_name="issue", name="yes_label_en",     field=models.CharField(max_length=100, blank=True)),
        migrations.AddField(model_name="issue", name="no_label_en",      field=models.CharField(max_length=100, blank=True)),
        migrations.AddField(model_name="issue", name="neutral_label_en", field=models.CharField(max_length=100, blank=True)),
    ]
