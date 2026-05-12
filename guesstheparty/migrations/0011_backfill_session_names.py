import random

from django.db import migrations


def _generate_random_name():
    from coolname import generate_slug

    slug = generate_slug(2)
    name = "".join(part.capitalize() for part in slug.split("-"))
    number = random.randint(1000, 9999)
    return f"{name}:{number}"


def backfill_session_names(apps, schema_editor):
    UserSession = apps.get_model("guesstheparty", "UserSession")

    session_keys = (
        UserSession.objects.filter(name="")
        .values_list("session_key", flat=True)
        .distinct()
    )

    for session_key in session_keys:
        existing_name = (
            UserSession.objects.filter(session_key=session_key)
            .exclude(name="")
            .values_list("name", flat=True)
            .first()
        )
        name = existing_name or _generate_random_name()
        UserSession.objects.filter(session_key=session_key, name="").update(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("guesstheparty", "0010_usersession_name"),
    ]

    operations = [
        migrations.RunPython(backfill_session_names, migrations.RunPython.noop),
    ]
