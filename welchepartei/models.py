from django.db import models


class Party(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50)
    color_hex = models.CharField(max_length=7, blank=True)
    spectrum_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["spectrum_order", "id"]

    def __str__(self):
        return self.name


class Issue(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    label_de = models.CharField(max_length=200)
    label_en = models.CharField(max_length=200, blank=True)
    question_key = models.CharField(max_length=50, unique=True)
    question_text_de = models.TextField(blank=True)
    question_text_en = models.TextField(blank=True)
    yes_label_de = models.CharField(max_length=100, blank=True)
    yes_label_en = models.CharField(max_length=100, blank=True)
    no_label_de = models.CharField(max_length=100, blank=True)
    no_label_en = models.CharField(max_length=100, blank=True)
    neutral_label_de = models.CharField(max_length=100, blank=True)
    neutral_label_en = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.label_de


class Position(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="positions")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="positions")
    answer_value = models.CharField(max_length=20)
    answer_slot = models.IntegerField()  # 0=yes/support, 1=no/oppose, 2=neutral
    source_quote = models.TextField(blank=True)
    source_quote_en = models.TextField(blank=True)
    party_rationale = models.TextField(blank=True)
    party_rationale_en = models.TextField(blank=True)
    source_url = models.URLField(max_length=2000, blank=True)
    source_locator = models.TextField(blank=True)

    class Meta:
        unique_together = [["party", "issue"]]

    def __str__(self):
        return f"{self.party_id} / {self.issue_id}: {self.answer_value}"


class QuizSession(models.Model):
    session_key = models.CharField(max_length=40, db_index=True, unique=True)
    answers = models.JSONField(default=dict)
    weights = models.JSONField(default=dict)
    values_answers = models.JSONField(default=dict)
    pre_quiz_party = models.CharField(max_length=50, blank=True)
    post_quiz_party = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QuizSession({self.session_key})"
