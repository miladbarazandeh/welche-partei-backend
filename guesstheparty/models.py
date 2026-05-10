import uuid

from django.db import models
from django.utils.text import slugify

CANONICAL_PARTIES = [
    ("SPD", "SPD"),
    ("CDU/CSU", "CDU/CSU"),
    ("Grüne", "Grüne"),
    ("AfD", "AfD"),
    ("Die Linke", "Die Linke"),
    ("FDP", "FDP"),
]

PARTY_LEANING = {
    "SPD": "left",
    "Grüne": "left",
    "Die Linke": "left",
    "CDU/CSU": "right",
    "FDP": "right",
    "AfD": "right",
}


class Politician(models.Model):
    abgeordnetenwatch_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=50, choices=CANONICAL_PARTIES)
    parliament = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, blank=True)
    image_local = models.CharField(max_length=500, blank=True)
    reference = models.SlugField(max_length=250, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)

    def _generate_slug(self):
        base = slugify(self.name)
        if not Politician.objects.filter(slug=base).exists():
            return base
        with_party = f"{base}-{slugify(self.party)}"
        if not Politician.objects.filter(slug=with_party).exists():
            return with_party
        raise ValueError(
            f"Could not generate unique slug for '{self.name}' ({self.party})"
        )

    def __str__(self):
        return f"{self.name} ({self.party})"


class UserSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    best_streak = models.IntegerField(default=0)
    pending_politician = models.ForeignKey(
        "Politician", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Answer(models.Model):
    politician = models.ForeignKey(
        Politician, on_delete=models.CASCADE, related_name="answers"
    )
    session_key = models.CharField(max_length=40, db_index=True)
    guessed_party = models.CharField(max_length=50)
    is_correct = models.BooleanField()
    is_spectrum_correct = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
