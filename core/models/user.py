from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from core.choices import UserRole, UserStatus, LanguageCode


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    username = models.CharField(
        max_length=50, unique=True, db_index=True, validators=[MinLengthValidator(3)]
    )

    # Profile
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    # Role & Status
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.VIEWER
    )
    status = models.CharField(
        max_length=30, choices=UserStatus.choices, default=UserStatus.ACTIVE
    )

    # Security
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Preferences
    preferred_language = models.CharField(
        max_length=5, choices=LanguageCode.choices, default=LanguageCode.ENGLISH
    )
    email_notifications_enabled = models.BooleanField(default=True)

    # Metadata
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "status"]),
            models.Index(fields=["username"]),
            models.Index(fields=["role", "status"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_creator(self):
        return self.role in [UserRole.CREATOR, UserRole.ADMIN]

    @property
    def is_premium(self):
        return (
            hasattr(self, "active_subscription") and self.active_subscription.is_active
        )

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = UserStatus.DELETED
        self.is_active = False
        self.save()


class SocialAuth(models.Model):
    """OAuth social login connections"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_auths"
    )

    provider = models.CharField(max_length=50)  # google, facebook, apple
    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_auths"
        unique_together = [["provider", "provider_user_id"]]
        indexes = [
            models.Index(fields=["user", "provider"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


class RefreshToken(models.Model):
    """JWT Refresh Token Management"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refresh_tokens"
    )

    token = models.CharField(max_length=500, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    device_info = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refresh_tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "revoked"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"Token for {self.user.username}"

    @property
    def is_valid(self):
        return not self.revoked and self.expires_at > timezone.now()

    def revoke(self):
        self.revoked = True
        self.revoked_at = timezone.now()
        self.save()


class PasswordResetToken(models.Model):
    """Password reset token management"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )

    token = models.CharField(max_length=100, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]

    @property
    def is_valid(self):
        return not self.used and self.expires_at > timezone.now()
