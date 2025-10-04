from django.db import models
from django.contrib.postgres.fields import ArrayField


class TrendingVideo(models.Model):
    """Cached trending videos"""

    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="trending_entries"
    )

    # Ranking
    rank = models.IntegerField()
    score = models.FloatField(
        help_text="Trending score based on views, velocity, engagement"
    )

    # Category/Region specific trending
    category = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=2, default="BD")

    # Snapshot date
    date = models.DateField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trending_videos"
        ordering = ["date", "rank"]
        unique_together = [["video", "date", "region"]]
        indexes = [
            models.Index(fields=["date", "region", "rank"]),
        ]

    def __str__(self):
        return f"#{self.rank} - {self.video.title} - {self.date}"


class RecommendationCache(models.Model):
    """Cached recommendations per user"""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="recommendation_caches"
    )

    # Recommended video IDs (stored as array for quick retrieval)
    video_ids = ArrayField(models.IntegerField(), default=list, size=50)

    # Recommendation context
    context = models.CharField(
        max_length=50, default="home", help_text="home, watch_next, subscriptions, etc."
    )

    # Metadata
    algorithm_version = models.CharField(max_length=20, default="v1")
    score_threshold = models.FloatField(default=0.0)

    # Cache validity
    expires_at = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recommendation_caches"
        ordering = ["-updated_at"]
        unique_together = [["user", "context"]]
        indexes = [
            models.Index(fields=["user", "context"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.context}"


class SearchQuery(models.Model):
    """Track search queries for analytics and autocomplete"""

    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_queries",
    )

    query = models.CharField(max_length=255, db_index=True)
    normalized_query = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Lowercase, trimmed version for grouping",
    )

    # Results
    result_count = models.IntegerField(default=0)
    clicked_video = models.ForeignKey(
        "Video",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_clicks",
    )
    click_position = models.IntegerField(null=True, blank=True)

    # Context
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "search_queries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["normalized_query", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.query} - {self.created_at}"


class PopularSearch(models.Model):
    """Aggregated popular searches for autocomplete"""

    query = models.CharField(max_length=255, unique=True, db_index=True)

    search_count = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0.0)

    # Time-based popularity
    daily_count = models.IntegerField(default=0)
    weekly_count = models.IntegerField(default=0)
    monthly_count = models.IntegerField(default=0)

    last_searched_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "popular_searches"
        ordering = ["-search_count"]
        indexes = [
            models.Index(fields=["-search_count"]),
            models.Index(fields=["query"]),
        ]

    def __str__(self):
        return f"{self.query} ({self.search_count})"


class ChannelAnalytics(models.Model):
    """Daily aggregated channel analytics"""

    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="analytics"
    )

    date = models.DateField(db_index=True)

    # Views
    total_views = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)

    # Engagement
    total_watch_time_seconds = models.BigIntegerField(default=0)
    average_view_duration_seconds = models.IntegerField(default=0)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    # Subscribers
    new_subscribers = models.IntegerField(default=0)
    unsubscribers = models.IntegerField(default=0)
    net_subscriber_change = models.IntegerField(default=0)

    # Revenue (in cents)
    estimated_revenue_cents = models.IntegerField(default=0)

    # Traffic sources
    traffic_source_data = models.JSONField(
        default=dict, help_text="Breakdown of traffic sources"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "channel_analytics"
        ordering = ["-date"]
        unique_together = [["channel", "date"]]
        indexes = [
            models.Index(fields=["channel", "date"]),
        ]

    def __str__(self):
        return f"{self.channel.name} - {self.date}"


class VideoAnalytics(models.Model):
    """Daily aggregated video analytics"""

    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="analytics"
    )

    date = models.DateField(db_index=True)

    # Views
    views = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)

    # Engagement
    watch_time_seconds = models.BigIntegerField(default=0)
    average_view_duration_seconds = models.IntegerField(default=0)
    average_percentage_viewed = models.FloatField(default=0.0)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    # Audience retention (stored as JSON array of percentages)
    retention_curve = models.JSONField(
        default=list, help_text="Audience retention at each 5% interval"
    )

    # Demographics
    demographics_data = models.JSONField(
        default=dict, help_text="Age, gender, location breakdown"
    )

    # Traffic sources
    traffic_sources = models.JSONField(
        default=dict, help_text="Where viewers came from"
    )

    # Revenue (in cents)
    estimated_revenue_cents = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_analytics"
        ordering = ["-date"]
        unique_together = [["video", "date"]]
        indexes = [
            models.Index(fields=["video", "date"]),
        ]

    def __str__(self):
        return f"{self.video.title} - {self.date}"


class UserWatchHistory(models.Model):
    """User watch history for recommendations"""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="watch_history"
    )
    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="watch_history_entries"
    )

    # Watch details
    watch_percentage = models.FloatField(default=0.0)
    watch_duration_seconds = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    # Last position for resume
    last_position_seconds = models.IntegerField(default=0)

    watched_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_watch_history"
        ordering = ["-watched_at"]
        unique_together = [["user", "video"]]
        indexes = [
            models.Index(fields=["user", "-watched_at"]),
            models.Index(fields=["video", "watched_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"
