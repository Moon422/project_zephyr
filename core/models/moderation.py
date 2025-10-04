from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.choices import FlagReason, FlagStatus, ModerationAction


class Flag(models.Model):
    """Content flagging system (videos, comments, users)"""

    # Generic relation to flag any content type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Flagger
    user = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="flags_created"
    )

    reason = models.CharField(max_length=30, choices=FlagReason.choices)
    reason_detail = models.TextField(max_length=1000, blank=True)

    status = models.CharField(
        max_length=20, choices=FlagStatus.choices, default=FlagStatus.PENDING
    )

    # Review
    reviewed_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flags_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "flags"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Flag: {self.reason} on {self.content_type}"


class ModerationLog(models.Model):
    """Log of all moderation actions"""

    moderator = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="moderation_actions"
    )

    # Target (video, comment, user, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    action = models.CharField(max_length=30, choices=ModerationAction.choices)

    reason = models.TextField(max_length=2000)

    # Related flag if action was taken from a flag
    related_flag = models.ForeignKey(
        Flag, on_delete=models.SET_NULL, null=True, blank=True, related_name="actions"
    )

    # Duration for temporary actions
    duration_days = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "moderation_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["moderator", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.moderator.username if self.moderator else 'System'}"


class UserSuspension(models.Model):
    """Track user suspensions"""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="suspensions"
    )

    reason = models.TextField(max_length=2000)

    suspended_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="suspensions_issued"
    )

    is_permanent = models.BooleanField(default=False)

    suspended_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    lifted_at = models.DateTimeField(null=True, blank=True)

    lifted_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suspensions_lifted",
    )

    class Meta:
        db_table = "user_suspensions"
        ordering = ["-suspended_at"]
        indexes = [
            models.Index(fields=["user", "suspended_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} suspended"

    @property
    def is_active(self):
        if self.lifted_at:
            return False
        if self.is_permanent:
            return True
        if self.expires_at:
            from django.utils import timezone

            return timezone.now() < self.expires_at
        return True
