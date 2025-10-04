from django.db import models
from django.core.validators import MinLengthValidator
from .choices import ChannelStatus


class Channel(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="channel"
    )

    # Channel Info
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    handle = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique channel handle (e.g., @channelname)",
    )
    description = models.TextField(max_length=5000, blank=True)

    # Branding
    avatar_url = models.URLField(max_length=500, blank=True)
    banner_url = models.URLField(max_length=500, blank=True)

    # Status
    status = models.CharField(
        max_length=20, choices=ChannelStatus.choices, default=ChannelStatus.ACTIVE
    )
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Stats (denormalized for performance)
    subscriber_count = models.IntegerField(default=0, db_index=True)
    total_views = models.BigIntegerField(default=0)
    total_videos = models.IntegerField(default=0)

    # Monetization
    monetization_enabled = models.BooleanField(default=False)
    monetization_enabled_at = models.DateTimeField(null=True, blank=True)

    # Quotas (based on subscriber count)
    max_videos_per_week = models.IntegerField(default=10)
    max_video_duration_minutes = models.IntegerField(default=15)
    max_file_size_gb = models.IntegerField(default=2)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "channels"
        ordering = ["-subscriber_count", "-created_at"]
        indexes = [
            models.Index(fields=["handle"]),
            models.Index(fields=["status", "verified"]),
            models.Index(fields=["subscriber_count"]),
        ]

    def __str__(self):
        return f"{self.name} (@{self.handle})"

    def update_quotas(self):
        """Update upload quotas based on subscriber count"""
        if self.subscriber_count >= 1000:
            self.max_videos_per_week = 999999  # Unlimited
            self.max_video_duration_minutes = 720  # 12 hours
            self.max_file_size_gb = 50
        else:
            self.max_videos_per_week = 10
            self.max_video_duration_minutes = 15
            self.max_file_size_gb = 2
        self.save()

    def increment_subscriber_count(self):
        self.subscriber_count = models.F("subscriber_count") + 1
        self.save()
        self.refresh_from_db()
        self.update_quotas()

    def decrement_subscriber_count(self):
        self.subscriber_count = models.F("subscriber_count") - 1
        self.save()
        self.refresh_from_db()


class Subscription(models.Model):
    """User subscribes to Channel"""

    subscriber = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="subscriptions"
    )
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="subscribers"
    )

    # Notification preferences
    notifications_enabled = models.BooleanField(default=True)

    subscribed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "channel_subscriptions"
        unique_together = [["subscriber", "channel"]]
        ordering = ["-subscribed_at"]
        indexes = [
            models.Index(fields=["subscriber", "channel"]),
            models.Index(fields=["channel", "subscribed_at"]),
        ]

    def __str__(self):
        return f"{self.subscriber.username} -> {self.channel.name}"
