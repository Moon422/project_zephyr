from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import (
    User,
    Channel,
    Video,
    Comment,
    SubscriptionPlan,
    UserSubscription,
    Flag,
    ModerationLog,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "status", "created_at"]
    list_filter = ["role", "status", "email_verified"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "birthdate", "bio", "avatar_url")},
        ),
        (
            "Permissions",
            {"fields": ("role", "status", "is_staff", "is_superuser", "is_active")},
        ),
        ("Security", {"fields": ("mfa_enabled", "email_verified", "last_login_ip")}),
        ("Dates", {"fields": ("created_at", "updated_at", "last_login")}),
    )

    readonly_fields = ["created_at", "updated_at", "last_login"]


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "handle",
        "user",
        "subscriber_count",
        "verified",
        "status",
        "created_at",
    ]
    list_filter = ["status", "verified", "monetization_enabled"]
    search_fields = ["name", "handle", "user__username"]
    ordering = ["-subscriber_count"]
    readonly_fields = [
        "subscriber_count",
        "total_views",
        "total_videos",
        "created_at",
        "updated_at",
    ]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "channel",
        "status",
        "visibility",
        "view_count",
        "published_at",
    ]
    list_filter = ["status", "visibility", "age_restricted"]
    search_fields = ["title", "channel__name"]
    ordering = ["-published_at"]
    readonly_fields = [
        "view_count",
        "like_count",
        "dislike_count",
        "comment_count",
        "created_at",
        "updated_at",
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "video",
        "text_preview",
        "status",
        "like_count",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = ["text", "user__username", "video__title"]
    ordering = ["-created_at"]

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Comment"


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "plan_type", "price_display", "is_active"]
    list_filter = ["is_active", "plan_type"]

    def price_display(self, obj):
        return f"${obj.price_monthly_cents / 100:.2f}/month"

    price_display.short_description = "Price"


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "start_date", "renewal_date"]
    list_filter = ["status", "plan"]
    search_fields = ["user__username", "user__email"]
    ordering = ["-created_at"]


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = [
        "content_type",
        "object_id",
        "reason",
        "status",
        "user",
        "created_at",
    ]
    list_filter = ["status", "reason"]
    search_fields = ["user__username", "reason_detail"]
    ordering = ["-created_at"]


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ["moderator", "action", "content_type", "object_id", "created_at"]
    list_filter = ["action"]
    search_fields = ["moderator__username", "reason"]
    ordering = ["-created_at"]
