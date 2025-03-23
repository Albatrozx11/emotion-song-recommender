from django.db import models

class SongRecommendation(models.Model):
    emotion = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album_cover = models.URLField(null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emotion}: {self.title} by {self.artist}"