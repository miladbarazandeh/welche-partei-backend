from rest_framework import serializers

from .models import Issue, Party, Position


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ["id", "name", "short_name", "color_hex", "spectrum_order"]


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "label_de",
            "label_en",
            "question_key",
            "question_text_de",
            "question_text_en",
            "yes_label_de",
            "yes_label_en",
            "no_label_de",
            "no_label_en",
            "neutral_label_de",
            "neutral_label_en",
            "display_order",
        ]


class PositionSerializer(serializers.ModelSerializer):
    party_id = serializers.CharField(source="party.id")
    issue_id = serializers.CharField(source="issue.id")

    class Meta:
        model = Position
        fields = [
            "party_id",
            "issue_id",
            "answer_value",
            "answer_slot",
            "source_quote",
            "source_quote_en",
            "party_rationale",
            "party_rationale_en",
            "source_url",
        ]
