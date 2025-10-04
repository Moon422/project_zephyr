from django.db import models


class UserRole(models.TextChoices):
    GUEST = "GUEST", "Guest Viewer"
    VIEWER = "VIEWER", "Authenticated Viewer"
    CREATOR = "CREATOR", "Creator"
    MODERATOR = "MODERATOR", "Moderator"
    ADMIN = "ADMIN", "Admin"
    PREMIUM = "PREMIUM", "Premium Subscriber"


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    SUSPENDED = "SUSPENDED", "Suspended"
    BANNED = "BANNED", "Banned"
    PENDING_VERIFICATION = "PENDING_VERIFICATION", "Pending Verification"
    DELETED = "DELETED", "Deleted"


class ChannelStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    SUSPENDED = "SUSPENDED", "Suspended"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    DELETED = "DELETED", "Deleted"


class VideoStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    UPLOADING = "UPLOADING", "Uploading"
    PROCESSING = "PROCESSING", "Processing"
    TRANSCODING = "TRANSCODING", "Transcoding"
    PUBLISHED = "PUBLISHED", "Published"
    FLAGGED = "FLAGGED", "Flagged"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    REMOVED = "REMOVED", "Removed"
    ARCHIVED = "ARCHIVED", "Archived"


class VideoVisibility(models.TextChoices):
    PUBLIC = "PUBLIC", "Public"
    UNLISTED = "UNLISTED", "Unlisted"
    PREMIUM = "PREMIUM", "Premium Only"
    PRIVATE = "PRIVATE", "Private"


class VideoResolution(models.TextChoices):
    RES_240P = "240p", "240p (426x240)"
    RES_360P = "360p", "360p (640x360)"
    RES_480P = "480p", "480p (854x480)"
    RES_720P = "720p", "720p (1280x720)"
    RES_1080P = "1080p", "1080p (1920x1080)"
    RES_1440P = "1440p", "1440p (2560x1440)"


class InteractionType(models.TextChoices):
    LIKE = "LIKE", "Like"
    DISLIKE = "DISLIKE", "Dislike"
    VIEW = "VIEW", "View"
    NOT_INTERESTED = "NOT_INTERESTED", "Not Interested"
    WATCH_TIME = "WATCH_TIME", "Watch Time"


class CommentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    FLAGGED = "FLAGGED", "Flagged"
    HIDDEN = "HIDDEN", "Hidden"
    REMOVED = "REMOVED", "Removed"


class FlagReason(models.TextChoices):
    SPAM = "SPAM", "Spam"
    HATE_SPEECH = "HATE_SPEECH", "Hate Speech"
    SEXUAL_CONTENT = "SEXUAL_CONTENT", "Sexual Content"
    VIOLENCE = "VIOLENCE", "Violence"
    COPYRIGHT = "COPYRIGHT", "Copyright Violation"
    MISINFORMATION = "MISINFORMATION", "Misinformation"
    CHILD_ABUSE = "CHILD_ABUSE", "Child Abuse"
    OTHER = "OTHER", "Other"


class FlagStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Review"
    REVIEWING = "REVIEWING", "Under Review"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"
    ESCALATED = "ESCALATED", "Escalated"


class ModerationAction(models.TextChoices):
    WARNING = "WARNING", "Warning"
    DEMONETIZE = "DEMONETIZE", "Demonetize"
    TEMP_SUSPENSION = "TEMP_SUSPENSION", "Temporary Suspension"
    PERMANENT_BAN = "PERMANENT_BAN", "Permanent Ban"
    CONTENT_REMOVAL = "CONTENT_REMOVAL", "Content Removal"
    NO_ACTION = "NO_ACTION", "No Action"


class SubscriptionPlanType(models.TextChoices):
    FREE = "FREE", "Free"
    PREMIUM_MONTHLY = "PREMIUM_MONTHLY", "Premium Monthly"
    PREMIUM_ANNUAL = "PREMIUM_ANNUAL", "Premium Annual"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CANCELLED = "CANCELLED", "Cancelled"
    EXPIRED = "EXPIRED", "Expired"
    GRACE_PERIOD = "GRACE_PERIOD", "Grace Period"
    SUSPENDED = "SUSPENDED", "Suspended"


class PayoutStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentGateway(models.TextChoices):
    SSLCOMMERZ = "SSLCOMMERZ", "SSLCommerz"
    TWO_CHECKOUT = "2CHECKOUT", "2Checkout"


class TranscodingStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class NotificationType(models.TextChoices):
    CHANNEL = "CHANNEL", "Channel Update"
    SYSTEM = "SYSTEM", "System Notification"
    MONETIZATION = "MONETIZATION", "Monetization"
    MODERATION = "MODERATION", "Moderation"


class LanguageCode(models.TextChoices):
    ENGLISH = "en", "English"
    BANGLA = "bn", "Bangla"
