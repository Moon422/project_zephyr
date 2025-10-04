from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .choices import (
    VideoStatus,
    VideoVisibility,
    VideoResolution,
    TranscodingStatus,
)


class Video(models.Model):
    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="videos"
    )

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=10000, blank=True)

    # Status & Visibility
    status = models.CharField(
        max_length=20,
        choices=VideoStatus.choices,
        default=VideoStatus.DRAFT,
        db_index=True,
    )
    visibility = models.CharField(
        max_length=20, choices=VideoVisibility.choices, default=VideoVisibility.PUBLIC
    )

    # Restrictions
    age_restricted = models.BooleanField(default=False)
    geo_restrictions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of country codes where video is blocked",
    )

    # Versioning
    active_version = models.ForeignKey(
        "VideoVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_for_video",
    )

    # Thumbnails
    thumbnail_url = models.URLField(max_length=500, blank=True)
    thumbnail_auto_generated = models.BooleanField(default=True)

    # Stats (denormalized)
    view_count = models.BigIntegerField(default=0, db_index=True)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)

    # Engagement metrics
    average_watch_time_seconds = models.IntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # Metadata
    duration_seconds = models.IntegerField(default=0)
    language = models.CharField(max_length=5, default="en")

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)  # For archival

    class Meta:
        db_table = "videos"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["status", "visibility", "published_at"]),
            models.Index(fields=["view_count"]),
            models.Index(fields=["-published_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.channel.name}"

    def publish(self):
        if self.status == VideoStatus.PROCESSING and self.active_version:
            self.status = VideoStatus.PUBLISHED
            self.published_at = timezone.now()
            self.save()

    def increment_view_count(self):
        self.view_count = models.F("view_count") + 1
        self.last_activity_at = timezone.now()
        self.save()
        self.refresh_from_db()

    @property
    def is_published(self):
        return self.status == VideoStatus.PUBLISHED and self.published_at is not None


class VideoVersion(models.Model):
    """Versioning system for video re-uploads"""

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="versions")

    version_number = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Source file info
    source_object_key = models.CharField(
        max_length=500, help_text="S3 object key for original upload"
    )
    source_file_size_bytes = models.BigIntegerField(default=0)
    source_duration_seconds = models.IntegerField(default=0)
    source_resolution = models.CharField(max_length=20, blank=True)
    source_codec = models.CharField(max_length=50, blank=True)

    # Transcoding
    transcoding_profile_set = models.CharField(
        max_length=50, default="standard", help_text="ABR ladder profile used"
    )
    transcoding_status = models.CharField(
        max_length=20,
        choices=TranscodingStatus.choices,
        default=TranscodingStatus.PENDING,
    )
    transcoding_started_at = models.DateTimeField(null=True, blank=True)
    transcoding_completed_at = models.DateTimeField(null=True, blank=True)
    transcoding_error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_versions"
        ordering = ["-version_number"]
        unique_together = [["video", "version_number"]]
        indexes = [
            models.Index(fields=["video", "is_active"]),
        ]

    def __str__(self):
        return f"{self.video.title} - v{self.version_number}"


class VideoAsset(models.Model):
    """Transcoded video assets (ABR ladder)"""

    video_version = models.ForeignKey(
        VideoVersion, on_delete=models.CASCADE, related_name="assets"
    )

    resolution = models.CharField(max_length=10, choices=VideoResolution.choices)
    bitrate_kbps = models.IntegerField()

    # HLS paths
    playlist_url = models.URLField(
        max_length=500, help_text="Master or variant playlist URL"
    )
    segment_path_prefix = models.CharField(
        max_length=500, help_text="S3 prefix for segment files"
    )

    # File info
    file_size_bytes = models.BigIntegerField(default=0)
    codec = models.CharField(max_length=50, default="H.264")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_assets"
        ordering = ["-bitrate_kbps"]
        unique_together = [["video_version", "resolution"]]
        indexes = [
            models.Index(fields=["video_version", "resolution"]),
        ]

    def __str__(self):
        return f"{self.video_version.video.title} - {self.resolution}"


class VideoTag(models.Model):
    """Tags for video categorization"""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True)

    usage_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_tags"
        ordering = ["-usage_count", "name"]

    def __str__(self):
        return self.name


class VideoTagRelation(models.Model):
    """Many-to-many relationship between videos and tags"""

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="tag_relations"
    )
    tag = models.ForeignKey(
        VideoTag, on_delete=models.CASCADE, related_name="video_relations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_tag_relations"
        unique_together = [["video", "tag"]]
        indexes = [
            models.Index(fields=["video"]),
            models.Index(fields=["tag"]),
        ]


class Subtitle(models.Model):
    """Video subtitles/captions"""

    video_version = models.ForeignKey(
        VideoVersion, on_delete=models.CASCADE, related_name="subtitles"
    )

    language_code = models.CharField(max_length=5)
    language_name = models.CharField(max_length=50)

    file_key = models.CharField(max_length=500, help_text="S3 key for WebVTT file")
    file_url = models.URLField(max_length=500)

    is_published = models.BooleanField(default=True)
    is_auto_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subtitles"
        unique_together = [["video_version", "language_code"]]
        indexes = [
            models.Index(fields=["video_version", "language_code"]),
        ]

    def __str__(self):
        return f"{self.video_version.video.title} - {self.language_name}"
