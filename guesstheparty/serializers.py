from rest_framework import serializers

from .models import Answer, Politician


class PoliticianSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Politician
        # party is intentionally omitted — it's what the user must guess
        fields = ['id', 'name', 'parliament', 'image_path']

    def get_image_path(self, obj):
        if not obj.image_local:
            return None
        request = self.context.get('request')
        url = f'/media/{obj.image_local}'
        if request:
            return request.build_absolute_uri(url)
        return url


class AnswerSerializer(serializers.ModelSerializer):
    politician_name = serializers.CharField(source='politician.name', read_only=True)
    correct_party = serializers.CharField(source='politician.party', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'politician_name', 'guessed_party', 'correct_party', 'is_correct', 'created_at']
