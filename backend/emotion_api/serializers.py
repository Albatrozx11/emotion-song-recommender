from rest_framework import serializers
from .models import SongRecommendation

class SongSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    album_cover = serializers.URLField(required=False)
    preview_url = serializers.URLField(required=False)