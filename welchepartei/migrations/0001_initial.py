from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Party",
            fields=[
                ("id", models.CharField(max_length=50, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("short_name", models.CharField(max_length=50)),
                ("color_hex", models.CharField(blank=True, max_length=7)),
                ("spectrum_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["spectrum_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.CharField(max_length=50, primary_key=True, serialize=False)),
                ("label_de", models.CharField(max_length=200)),
                ("question_key", models.CharField(max_length=50, unique=True)),
                ("question_text_de", models.TextField(blank=True)),
                ("yes_label_de", models.CharField(blank=True, max_length=100)),
                ("no_label_de", models.CharField(blank=True, max_length=100)),
                ("neutral_label_de", models.CharField(blank=True, max_length=100)),
                ("display_order", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["display_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_value", models.CharField(max_length=20)),
                ("answer_slot", models.IntegerField()),
                ("source_quote", models.TextField(blank=True)),
                ("party_rationale", models.TextField(blank=True)),
                ("source_url", models.URLField(blank=True, max_length=2000)),
                ("source_locator", models.TextField(blank=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="welchepartei.party",
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="welchepartei.issue",
                    ),
                ),
            ],
            options={
                "unique_together": {("party", "issue")},
            },
        ),
        migrations.CreateModel(
            name="QuizSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(db_index=True, max_length=40, unique=True)),
                ("answers", models.JSONField(default=dict)),
                ("weights", models.JSONField(default=dict)),
                ("values_answers", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
