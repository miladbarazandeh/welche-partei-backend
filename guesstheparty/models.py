from django.db import models
from django.utils.text import slugify

COUNTRY_CHOICES = [
    ("DE", "Germany"),
    ("US", "United States"),
]


class Politician(models.Model):
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="DE")
    source_identifier = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    source_dataset = models.CharField(max_length=100, blank=True)
    abgeordnetenwatch_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=100)
    parliament = models.CharField(max_length=200)
    image_url = models.URLField(max_length=1000, blank=True)
    thumbline_url = models.URLField(max_length=1000, blank=True)
    image_local = models.CharField(max_length=500, blank=True)
    image_page_url = models.URLField(max_length=1000, blank=True)
    license_short_name = models.CharField(max_length=200, blank=True)
    license_url = models.URLField(max_length=1000, blank=True)
    attribution_text = models.TextField(blank=True)
    author_name = models.CharField(max_length=5000, blank=True)
    author_url = models.URLField(max_length=1000, blank=True)
    credit_text = models.TextField(blank=True)
    credit_url = models.URLField(max_length=1000, blank=True)
    reference = models.SlugField(max_length=250, unique=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["country", "party"], name="guessthepar_country_party_idx"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        candidates = [
            slugify(self.name),
            f"{slugify(self.name)}-{slugify(self.party)}",
            f"{slugify(self.name)}-{self.country.lower()}",
            f"{slugify(self.name)}-{slugify(self.party)}-{self.country.lower()}",
            (
                f"{slugify(self.name)}-{slugify(self.parliament)}-"
                f"{self.country.lower()}"
            ),
        ]
        for candidate in candidates:
            if not candidate:
                continue
            conflict = Politician.objects.filter(reference=candidate)
            if self.pk:
                conflict = conflict.exclude(pk=self.pk)
            if not conflict.exists():
                return candidate
        raise ValueError(
            f"Could not generate unique reference for '{self.name}' in {self.country}"
        )

    def __str__(self):
        return f"{self.name} ({self.country}, {self.party})"


class UserSession(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="DE")
    best_streak = models.IntegerField(default=0)
    pending_politician = models.ForeignKey(
        "Politician", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_key", "country"], name="unique_session_per_country"
            )
        ]


class Answer(models.Model):
    politician = models.ForeignKey(
        Politician, on_delete=models.CASCADE, related_name="answers"
    )
    session_key = models.CharField(max_length=40, db_index=True)
    guessed_party = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    is_spectrum_correct = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
