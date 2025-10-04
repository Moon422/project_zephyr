from django.db import models
from django.utils import timezone


class PublishedVideoManager(models.Manager):
    """Manager for published videos only"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                status="PUBLISHED",
                visibility="PUBLIC",
                published_at__lte=timezone.now(),
            )
        )


class ActiveChannelManager(models.Manager):
    """Manager for active channels only"""

    def get_queryset(self):
        return super().get_queryset().filter(status="ACTIVE", deleted_at__isnull=True)


class UnreadNotificationManager(models.Manager):
    """Manager for unread notifications"""

    def get_queryset(self):
        return super().get_queryset().filter(read=False)
