from rest_framework import serializers

from .game_config import get_game_party
from .models import Answer, Politician


class PoliticianSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Politician
        # party is intentionally omitted — it's what the user must guess
        fields = [
            "id",
            "name",
            "parliament",
            "image_path",
            "attribution_text",
            "credit_text",
            "credit_url",
            "image_page_url",
            "license_short_name",
            "license_url",
            "author_name",
        ]

    def get_image_path(self, obj):
        request = self.context.get("request")
        if obj.image_local:
            url = f"/media/{obj.image_local}"
            if request:
                return request.build_absolute_uri(url)
            return url
        return obj.image_url + "?width=600" or None


class AnswerSerializer(serializers.ModelSerializer):
    politician_name = serializers.CharField(source="politician.name", read_only=True)
    correct_party = serializers.SerializerMethodField()

    def get_correct_party(self, obj):
        return get_game_party(obj.politician.country, obj.politician.party)

    class Meta:
        model = Answer
        fields = [
            "id",
            "politician_name",
            "guessed_party",
            "correct_party",
            "is_correct",
            "created_at",
        ]
