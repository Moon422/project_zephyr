from django.db import models
from .choices import CommentStatus


class Comment(models.Model):
    """Video comments with threading support"""

    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments")

    # Threading (2-level: parent + replies)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    text = models.TextField(max_length=2000)

    status = models.CharField(
        max_length=20, choices=CommentStatus.choices, default=CommentStatus.ACTIVE
    )

    # Stats (denormalized)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)

    # Moderation
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["video", "status", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"{self.user.username} on {self.video.title}"

    @property
    def is_reply(self):
        return self.parent is not None


class CommentReaction(models.Model):
    """Like/Dislike on comments"""

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="comment_reactions"
    )

    is_like = models.BooleanField()  # True = like, False = dislike

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment_reactions"
        unique_together = [["comment", "user"]]
        indexes = [
            models.Index(fields=["comment", "is_like"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        reaction = "liked" if self.is_like else "disliked"
        return f"{self.user.username} {reaction} comment"
