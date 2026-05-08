from django.db import models

CANONICAL_PARTIES = [
    ('SPD', 'SPD'),
    ('CDU/CSU', 'CDU/CSU'),
    ('Grüne', 'Grüne'),
    ('AfD', 'AfD'),
    ('Die Linke', 'Die Linke'),
    ('FDP', 'FDP'),
]


class Politician(models.Model):
    abgeordnetenwatch_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=50, choices=CANONICAL_PARTIES)
    parliament = models.CharField(max_length=100)
    image_url = models.URLField(blank=True)
    image_local = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.name} ({self.party})"


class UserSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    best_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Answer(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name='answers')
    session_key = models.CharField(max_length=40, db_index=True)
    guessed_party = models.CharField(max_length=50)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
