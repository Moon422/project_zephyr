from django.db import models
from django.core.validators import MinValueValidator
from .choices import InteractionType


class Interaction(models.Model):
    """User interactions with videos (likes, views, watch time)"""

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="interactions",
        null=True,
        blank=True,  # Allow anonymous views
    )
    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="interactions"
    )

    type = models.CharField(max_length=20, choices=InteractionType.choices)

    # For WATCH_TIME type
    value = models.IntegerField(
        default=0,
        help_text="Watch time in seconds or binary flag (1/0) for like/dislike",
    )

    # Session tracking
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "interactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["video", "type", "timestamp"]),
            models.Index(fields=["user", "video", "type"]),
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.type} - {self.video.title}"


class WatchSession(models.Model):
    """Detailed watch session tracking for analytics"""

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="watch_sessions",
        null=True,
        blank=True,
    )
    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="watch_sessions"
    )

    session_id = models.CharField(max_length=100, db_index=True)

    # Watch metrics
    watch_time_seconds = models.IntegerField(default=0)
    completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0)]
    )

    # Quality metrics
    rebuffer_count = models.IntegerField(default=0)
    rebuffer_duration_seconds = models.IntegerField(default=0)
    startup_time_ms = models.IntegerField(default=0)
    average_bitrate_kbps = models.IntegerField(default=0)

    # Device & Network
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country_code = models.CharField(max_length=2, blank=True)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "watch_sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["video", "started_at"]),
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.video.title} - {self.watch_time_seconds}s"


class Playlist(models.Model):
    """User-created playlists"""

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="playlists")

    title = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, blank=True)

    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playlists"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_public"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class PlaylistItem(models.Model):
    """Videos in a playlist"""

    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="items"
    )
    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="playlist_items"
    )

    position = models.IntegerField(default=0)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "playlist_items"
        ordering = ["position", "added_at"]
        unique_together = [["playlist", "video"]]
        indexes = [
            models.Index(fields=["playlist", "position"]),
        ]

    def __str__(self):
        return f"{self.playlist.title} - {self.video.title}"
