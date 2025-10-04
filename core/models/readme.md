# User Authentication Models Documentation

## Overview
This module contains the core authentication and user management models for the video streaming application. It implements a custom user model with extended functionality including social authentication, JWT token management, and password reset capabilities.

---

## Table of Contents
- [CustomUserManager](#customusermanager)
- [User](#user)
- [SocialAuth](#socialauth)
- [RefreshToken](#refreshtoken)
- [PasswordResetToken](#passwordresettoken)
- [Channel](#channel)
- [Subscription](#subscription)
- [Video](#video)
- [VideoVersion](#videoversion)
- [VideoAsset](#videoasset)
- [VideoTag](#videotag)
- [VideoTagRelation](#videotagrelation)
- [Subtitle](#subtitle)
- [Interaction](#interaction)
- [WatchSession](#watchsession)
- [Playlist](#playlist)
- [PlaylistItem](#playlistitem)
- [Comment](#comment)
- [CommentReaction](#commentreaction)
- [SubscriptionPlan](#subscriptionplan)
- [UserSubscription](#usersubscription)
- [PaymentTransaction](#paymenttransaction)
- [PromotionalCode](#promotionalcode)
- [PromoCodeUsage](#promocodeusage)
- [Overview](#overview)
- [Models](#models)
   - [Flag](#1-flag)
   - [ModerationLog](#2-moderationlog)
   - [UserSuspension](#3-usersuspension)
- [Dependencies](#dependencies)
   - [Required Imports](#required-imports)
   - [External Choice Classes](#external-choice-classes)
   - [Related Models](#related-models)
- [Model Relationships](#model-relationships)
- [Use Cases](#use-cases)
- [Key Features](#key-features)
- [Overview](#overview)
- [Models](#models)
   - [TrendingVideo](#1-trendingvideo)
   - [RecommendationCache](#2-recommendationcache)
   - [SearchQuery](#3-searchquery)
   - [PopularSearch](#4-popularsearch)
   - [ChannelAnalytics](#5-channelanalytics)
   - [VideoAnalytics](#6-videoanalytics)
   - [UserWatchHistory](#7-userwatchhistory)
- [Dependencies](#dependencies)
- [Model Relationships](#model-relationships)
- [Overview](#overview)
- [Models](#models)
   - [CreatorPayout](#1-creatorpayout)
   - [RevenueShare](#2-revenueshare)
   - [PayoutMethod](#3-payoutmethod)
- [Dependencies](#dependencies)
- [Model Relationships](#model-relationships)

---

## CustomUserManager

### Purpose
Custom manager class for the User model that handles user creation with email-based authentication instead of Django's default username-based system.

### Class Definition
```python
class CustomUserManager(BaseUserManager)
```

### Methods

#### `create_user(email, username, password=None, **extra_fields)`
Creates and saves a regular user with the given email and username.

**Parameters:**
- `email` (str, required): User's email address
- `username` (str, required): Unique username
- `password` (str, optional): User password
- `**extra_fields`: Additional user fields

**Returns:** User instance

**Raises:**
- `ValueError`: If email or username is not provided

**Example:**
```python
user = User.objects.create_user(
    email='user@example.com',
    username='johndoe',
    password='secure_password123'
)
```

#### `create_superuser(email, username, password=None, **extra_fields)`
Creates and saves a superuser with admin privileges.

**Parameters:**
- `email` (str, required): Admin email address
- `username` (str, required): Admin username
- `password` (str, optional): Admin password
- `**extra_fields`: Additional user fields

**Returns:** User instance with admin privileges

**Default Values Set:**
- `role`: `UserRole.ADMIN`
- `is_staff`: `True`
- `is_superuser`: `True`
- `status`: `UserStatus.ACTIVE`

---

## User

### Purpose
Core user model extending Django's `AbstractBaseUser` and `PermissionsMixin`. Manages user accounts, authentication, profiles, security settings, and preferences for the video streaming platform.

### Class Definition
```python
class User(AbstractBaseUser, PermissionsMixin)
```

### Fields

#### **Authentication Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `email` | EmailField | unique, max_length=255, indexed | Primary authentication identifier |
| `username` | CharField | unique, max_length=50, min_length=3, indexed | Display name and alternative identifier |

#### **Profile Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `first_name` | CharField | max_length=100, optional | User's first name |
| `last_name` | CharField | max_length=100, optional | User's last name |
| `birthdate` | DateField | optional | User's date of birth |
| `avatar_url` | URLField | max_length=500, optional | Profile picture URL |
| `bio` | TextField | max_length=500, optional | User biography/description |

#### **Role & Status Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `role` | CharField | `UserRole.VIEWER` | User role (VIEWER, CREATOR, ADMIN) |
| `status` | CharField | `UserStatus.ACTIVE` | Account status |

#### **Security Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mfa_enabled` | BooleanField | False | Multi-factor authentication status |
| `mfa_secret` | CharField | '' | MFA secret key |
| `failed_login_attempts` | IntegerField | 0 | Counter for failed login attempts |
| `locked_until` | DateTimeField | null | Account lock expiration timestamp |
| `last_login_ip` | GenericIPAddressField | null | Last successful login IP address |

#### **Preference Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `preferred_language` | CharField | `LanguageCode.ENGLISH` | User's preferred interface language |
| `email_notifications_enabled` | BooleanField | True | Email notification preference |

#### **Metadata Fields**
| Field | Type | Description |
|-------|------|-------------|
| `is_staff` | BooleanField | Django admin access flag |
| `is_active` | BooleanField | Account active status |
| `email_verified` | BooleanField | Email verification status |
| `email_verified_at` | DateTimeField | Email verification timestamp |
| `created_at` | DateTimeField | Account creation timestamp (auto) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |
| `deleted_at` | DateTimeField | Soft delete timestamp |

### Configuration

**Manager:** `CustomUserManager`

**Authentication:**
- `USERNAME_FIELD`: `"email"`
- `REQUIRED_FIELDS`: `["username"]`

**Meta Options:**
- **Database Table:** `users`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(email, status)`
  - `(username)`
  - `(role, status)`

### Properties

#### `full_name`
Returns the user's full name or username as fallback.

**Returns:** str

**Example:**
```python
user.full_name  # "John Doe" or "johndoe" if names not set
```

#### `is_creator`
Checks if user has creator or admin privileges.

**Returns:** bool

#### `is_premium`
Checks if user has an active subscription.

**Returns:** bool

**Note:** Requires `active_subscription` relationship to be defined.

### Methods

#### `soft_delete()`
Performs a soft delete by setting deletion timestamp and deactivating the account without removing from database.

**Side Effects:**
- Sets `deleted_at` to current timestamp
- Changes `status` to `UserStatus.DELETED`
- Sets `is_active` to `False`

**Example:**
```python
user.soft_delete()
```

#### `__str__()`
String representation of the user.

**Returns:** `"{username} ({email})"`

---

## SocialAuth

### Purpose
Manages OAuth social login connections (Google, Facebook, Apple, etc.) for users, storing provider credentials and tokens.

### Class Definition
```python
class SocialAuth(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='social_auths' | Associated user account |
| `provider` | CharField | max_length=50 | OAuth provider name (google, facebook, apple) |
| `provider_user_id` | CharField | max_length=255 | User ID from the OAuth provider |
| `access_token` | TextField | optional | OAuth access token |
| `refresh_token` | TextField | optional | OAuth refresh token |
| `expires_at` | DateTimeField | optional | Token expiration timestamp |
| `created_at` | DateTimeField | auto | Connection creation timestamp |
| `updated_at` | DateTimeField | auto | Last update timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `social_auths`
- **Unique Together:** `(provider, provider_user_id)`
- **Indexes:**
  - `(user, provider)`

### Methods

#### `__str__()`
**Returns:** `"{username} - {provider}"`

### Usage Example
```python
social_auth = SocialAuth.objects.create(
    user=user,
    provider='google',
    provider_user_id='123456789',
    access_token='ya29.a0...',
    expires_at=timezone.now() + timedelta(hours=1)
)
```

---

## RefreshToken

### Purpose
Manages JWT refresh tokens for maintaining user sessions. Tracks token validity, device information, and provides token revocation functionality.

### Class Definition
```python
class RefreshToken(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='refresh_tokens' | Token owner |
| `token` | CharField | unique, max_length=500, indexed | JWT refresh token string |
| `expires_at` | DateTimeField | required | Token expiration timestamp |
| `revoked` | BooleanField | default=False | Token revocation status |
| `revoked_at` | DateTimeField | optional | Revocation timestamp |
| `device_info` | CharField | max_length=255, optional | Device/browser information |
| `ip_address` | GenericIPAddressField | optional | IP address of token creation |
| `created_at` | DateTimeField | auto | Token creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `refresh_tokens`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(user, revoked)`
  - `(token)`

### Properties

#### `is_valid`
Checks if token is valid (not revoked and not expired).

**Returns:** bool

**Example:**
```python
if refresh_token.is_valid:
    # Issue new access token
    pass
```

### Methods

#### `revoke()`
Revokes the refresh token, preventing further use.

**Side Effects:**
- Sets `revoked` to `True`
- Sets `revoked_at` to current timestamp

**Example:**
```python
refresh_token.revoke()  # User logged out or token compromised
```

#### `__str__()`
**Returns:** `"Token for {username}"`

### Usage Example
```python
refresh_token = RefreshToken.objects.create(
    user=user,
    token='eyJhbGciOiJIUzI1NiIs...',
    expires_at=timezone.now() + timedelta(days=7),
    device_info='Chrome 120.0 / Windows 10',
    ip_address='192.168.1.1'
)
```

---

## PasswordResetToken

### Purpose
Manages one-time use tokens for password reset functionality. Ensures secure password recovery with expiration and usage tracking.

### Class Definition
```python
class PasswordResetToken(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='password_reset_tokens' | User requesting password reset |
| `token` | CharField | unique, max_length=100, indexed | Reset token string |
| `expires_at` | DateTimeField | required | Token expiration timestamp |
| `used` | BooleanField | default=False | Token usage status |
| `used_at` | DateTimeField | optional | Token usage timestamp |
| `created_at` | DateTimeField | auto | Token creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `password_reset_tokens`
- **Default Ordering:** `-created_at` (newest first)

### Properties

#### `is_valid`
Checks if token is valid (not used and not expired).

**Returns:** bool

**Example:**
```python
if reset_token.is_valid:
    # Allow password reset
    user.set_password(new_password)
    reset_token.used = True
    reset_token.used_at = timezone.now()
    reset_token.save()
```

### Usage Example
```python
import secrets

reset_token = PasswordResetToken.objects.create(
    user=user,
    token=secrets.token_urlsafe(32),
    expires_at=timezone.now() + timedelta(hours=1)
)

# Send email with reset link
send_password_reset_email(user.email, reset_token.token)
```

---

## Dependencies

### Required Imports
```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from .choices import UserRole, UserStatus, LanguageCode
```

### External Choice Classes
The following choice classes must be defined in `choices.py`:
- **UserRole**: User role options (VIEWER, CREATOR, ADMIN)
- **UserStatus**: Account status options (ACTIVE, INACTIVE, SUSPENDED, DELETED)
- **LanguageCode**: Supported language codes (ENGLISH, etc.)

---

## Security Considerations

1. **Password Storage**: Passwords are hashed using Django's `set_password()` method
2. **Token Security**: All tokens should be generated using cryptographically secure methods
3. **Soft Delete**: User data is preserved for audit purposes using soft delete
4. **MFA Support**: Built-in multi-factor authentication capability
5. **Account Locking**: Automatic account locking after failed login attempts
6. **Token Revocation**: Refresh tokens can be revoked for security

---

## Best Practices

1. Always use `soft_delete()` instead of deleting user records
2. Revoke all refresh tokens when user changes password
3. Set appropriate token expiration times (e.g., 7 days for refresh tokens, 1 hour for password reset)
4. Clean up expired and used tokens periodically
5. Log IP addresses for security auditing
6. Verify email addresses before allowing full account access

---

# Channel Management Models Documentation

## Overview
This module contains models for managing content creator channels and user subscriptions in the video streaming platform. It handles channel profiles, branding, statistics, monetization settings, upload quotas, and subscriber relationships.

---

## Channel

### Purpose
Represents a content creator's channel on the platform. Each channel is owned by a user with creator privileges and serves as the primary container for organizing videos, managing branding, tracking statistics, and controlling monetization settings. The model implements dynamic quota systems based on subscriber milestones.

### Class Definition
```python
class Channel(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | OneToOneField | CASCADE, related_name='channel' | Channel owner (one channel per user) |

#### **Channel Information**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | CharField | max_length=100, min_length=3 | Display name of the channel |
| `handle` | SlugField | unique, max_length=50, indexed | Unique channel identifier (e.g., @channelname) |
| `description` | TextField | max_length=5000, optional | Channel description/about section |

#### **Branding Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `avatar_url` | URLField | max_length=500, optional | Channel profile picture URL |
| `banner_url` | URLField | max_length=500, optional | Channel banner/cover image URL |

#### **Status Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | CharField | `ChannelStatus.ACTIVE` | Channel status (ACTIVE, SUSPENDED, etc.) |
| `verified` | BooleanField | False | Verification badge status |
| `verified_at` | DateTimeField | null | Verification timestamp |

#### **Statistics Fields (Denormalized)**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `subscriber_count` | IntegerField | 0, indexed | Total number of subscribers |
| `total_views` | BigIntegerField | 0 | Cumulative view count across all videos |
| `total_videos` | IntegerField | 0 | Total number of published videos |

> **Note:** These statistics are denormalized for performance optimization and should be kept in sync with actual data.

#### **Monetization Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `monetization_enabled` | BooleanField | False | Monetization eligibility status |
| `monetization_enabled_at` | DateTimeField | null | Monetization activation timestamp |

#### **Quota Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_videos_per_week` | IntegerField | 10 | Weekly video upload limit |
| `max_video_duration_minutes` | IntegerField | 15 | Maximum video duration in minutes |
| `max_file_size_gb` | IntegerField | 2 | Maximum file size in gigabytes |

> **Quota Tiers:**
> - **Standard** (< 1,000 subscribers): 10 videos/week, 15 min duration, 2 GB file size
> - **Premium** (≥ 1,000 subscribers): Unlimited videos, 720 min (12 hours) duration, 50 GB file size

#### **Metadata Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Channel creation timestamp (auto, indexed) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |
| `deleted_at` | DateTimeField | Soft delete timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `channels`
- **Default Ordering:** 
  - `-subscriber_count` (most subscribers first)
  - `-created_at` (newest first as secondary)
- **Indexes:**
  - `(handle)` - Fast channel lookup by handle
  - `(status, verified)` - Filter verified/active channels
  - `(subscriber_count)` - Sort by popularity

### Methods

#### `update_quotas()`
Dynamically updates upload quotas based on subscriber count milestones.

**Logic:**
- **≥ 1,000 subscribers:** Unlocks premium tier quotas
- **< 1,000 subscribers:** Standard tier quotas

**Side Effects:**
- Updates `max_videos_per_week`, `max_video_duration_minutes`, `max_file_size_gb`
- Saves the model instance

**Example:**
```python
channel.subscriber_count = 1500
channel.update_quotas()
# Now: unlimited videos, 720 min duration, 50 GB file size
```

#### `increment_subscriber_count()`
Atomically increments subscriber count and updates quotas if milestone reached.

**Features:**
- Uses `F()` expression for atomic database-level increment (prevents race conditions)
- Refreshes model from database after update
- Automatically triggers quota update

**Example:**
```python
# User subscribes to channel
subscription = Subscription.objects.create(
    subscriber=user,
    channel=channel
)
channel.increment_subscriber_count()
```

**Thread-Safe:** ✅ Yes (uses database-level atomic operations)

#### `decrement_subscriber_count()`
Atomically decrements subscriber count when user unsubscribes.

**Features:**
- Uses `F()` expression for atomic database-level decrement
- Refreshes model from database after update

**Example:**
```python
# User unsubscribes
subscription.delete()
channel.decrement_subscriber_count()
```

**Thread-Safe:** ✅ Yes (uses database-level atomic operations)

> **⚠️ Note:** Decrement does not automatically downgrade quotas. Consider implementing quota checks on milestone drops if needed.

#### `__str__()`
String representation of the channel.

**Returns:** `"{name} (@{handle})"`

**Example:**
```python
str(channel)  # "Tech Reviews (@techreviews)"
```

### Usage Examples

#### Creating a New Channel
```python
from django.utils.text import slugify

channel = Channel.objects.create(
    user=creator_user,
    name="Tech Reviews",
    handle=slugify("techreviews"),
    description="Daily tech product reviews and tutorials",
    avatar_url="https://cdn.example.com/avatars/techreviews.jpg",
    banner_url="https://cdn.example.com/banners/techreviews.jpg"
)
```

#### Verifying a Channel
```python
from django.utils import timezone

channel.verified = True
channel.verified_at = timezone.now()
channel.save()
```

#### Enabling Monetization
```python
from django.utils import timezone

if channel.subscriber_count >= 1000 and channel.total_views >= 4000:
    channel.monetization_enabled = True
    channel.monetization_enabled_at = timezone.now()
    channel.save()
```

#### Checking Upload Quotas
```python
# Check if creator can upload
if channel.total_videos_this_week < channel.max_videos_per_week:
    if video_duration <= channel.max_video_duration_minutes:
        if file_size_gb <= channel.max_file_size_gb:
            # Allow upload
            pass
```

---

## Subscription

### Purpose
Manages the many-to-many relationship between users (subscribers) and channels. Tracks subscription timestamps and notification preferences for personalized content delivery.

### Class Definition
```python
class Subscription(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `subscriber` | ForeignKey | CASCADE, related_name='subscriptions' | User who subscribed |
| `channel` | ForeignKey | CASCADE, related_name='subscribers' | Channel being subscribed to |
| `notifications_enabled` | BooleanField | default=True | Push/email notification preference |
| `subscribed_at` | DateTimeField | auto, indexed | Subscription creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `channel_subscriptions`
- **Unique Together:** `(subscriber, channel)` - Prevents duplicate subscriptions
- **Default Ordering:** `-subscribed_at` (newest first)
- **Indexes:**
  - `(subscriber, channel)` - Fast subscription lookup
  - `(channel, subscribed_at)` - Chronological subscriber list

### Methods

#### `__str__()`
String representation of the subscription relationship.

**Returns:** `"{subscriber_username} -> {channel_name}"`

**Example:**
```python
str(subscription)  # "johndoe -> Tech Reviews"
```

### Usage Examples

#### Creating a Subscription
```python
# User subscribes to a channel
subscription = Subscription.objects.create(
    subscriber=user,
    channel=channel
)

# Update channel's subscriber count
channel.increment_subscriber_count()
```

#### Unsubscribing
```python
# Find and delete subscription
subscription = Subscription.objects.get(
    subscriber=user,
    channel=channel
)
subscription.delete()

# Update channel's subscriber count
channel.decrement_subscriber_count()
```

#### Toggling Notifications
```python
subscription = user.subscriptions.get(channel=channel)
subscription.notifications_enabled = False
subscription.save()
```

#### Querying User's Subscriptions
```python
# Get all channels user is subscribed to
subscribed_channels = Channel.objects.filter(
    subscribers__subscriber=user
).order_by('-subscribers__subscribed_at')

# Get subscription count
subscription_count = user.subscriptions.count()

# Check if user is subscribed to specific channel
is_subscribed = user.subscriptions.filter(channel=channel).exists()
```

#### Querying Channel's Subscribers
```python
# Get all subscribers of a channel
subscribers = User.objects.filter(
    subscriptions__channel=channel
).order_by('-subscriptions__subscribed_at')

# Get recent subscribers (last 30 days)
from django.utils import timezone
from datetime import timedelta

recent_subscribers = channel.subscribers.filter(
    subscribed_at__gte=timezone.now() - timedelta(days=30)
)

# Get subscribers with notifications enabled
notified_subscribers = channel.subscribers.filter(
    notifications_enabled=True
)
```

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.core.validators import MinLengthValidator
from .choices import ChannelStatus
```

### External Choice Classes
The following choice class must be defined in `choices.py`:
- **ChannelStatus**: Channel status options (ACTIVE, SUSPENDED, DELETED, etc.)

### Related Models
- **User**: From authentication models (OneToOne relationship with Channel)

---

## Business Logic & Rules

### Channel Creation Rules
1. Only users with `CREATOR` or `ADMIN` role can create channels
2. Each user can have only **one** channel (enforced by OneToOneField)
3. Channel handle must be unique across the platform
4. Handle should follow slug format (lowercase, alphanumeric, hyphens)

### Subscription Rules
1. Users cannot subscribe to their own channel
2. Each user-channel pair can only have one active subscription
3. Deleting a channel cascades to delete all subscriptions
4. Deleting a user cascades to delete all their subscriptions

### Quota System Rules
1. **Standard Tier** (< 1,000 subscribers):
   - 10 videos per week
   - 15 minutes max duration
   - 2 GB max file size

2. **Premium Tier** (≥ 1,000 subscribers):
   - Unlimited videos per week
   - 720 minutes (12 hours) max duration
   - 50 GB max file size

3. Quota upgrades happen automatically when reaching 1,000 subscribers
4. Consider implementing quota downgrade logic if subscriber count drops

### Monetization Eligibility
Typical requirements (implement in business logic):
- Minimum 1,000 subscribers
- Minimum 4,000 watch hours in past 12 months
- Channel in good standing (no strikes)
- Adherence to platform policies

---

## Performance Considerations

### Denormalized Statistics
The `subscriber_count`, `total_views`, and `total_videos` fields are denormalized for query performance. Ensure these are kept in sync:

```python
# When video is published
channel.total_videos = models.F('total_videos') + 1
channel.save()

# When video receives views
channel.total_views = models.F('total_views') + view_count
channel.save()
```

### Atomic Operations
Always use `F()` expressions for counter updates to prevent race conditions:

```python
# ✅ Good - Atomic
channel.subscriber_count = models.F('subscriber_count') + 1
channel.save()

# ❌ Bad - Race condition possible
channel.subscriber_count += 1
channel.save()
```

### Index Usage
Queries are optimized with indexes on:
- `handle` - Channel lookups by URL
- `subscriber_count` - Popular channels sorting
- `(status, verified)` - Filtering active/verified channels
- `(subscriber, channel)` - Subscription lookups

---

## Best Practices

1. **Always update subscriber counts atomically** using `increment_subscriber_count()` and `decrement_subscriber_count()`
2. **Validate handle format** before creating channels (use `slugify()`)
3. **Check quotas before allowing uploads** to prevent exceeding limits
4. **Keep denormalized stats in sync** with actual data
5. **Use soft delete** for channels (set `deleted_at`) to preserve historical data
6. **Implement periodic cleanup** of orphaned subscriptions
7. **Cache popular channel data** to reduce database load
8. **Send notifications** to subscribers when new content is published (if `notifications_enabled=True`)

---

## Security Considerations

1. **Validate channel ownership** before allowing modifications
2. **Rate limit subscription actions** to prevent spam
3. **Sanitize channel descriptions** to prevent XSS attacks
4. **Verify URLs** for avatar and banner to prevent malicious content
5. **Implement abuse reporting** for channels violating policies
6. **Log quota changes** for audit purposes

---

# Video Management Models Documentation

## Overview
This module contains comprehensive models for managing video content, including video metadata, versioning, transcoding assets, tagging, and subtitles. It implements an adaptive bitrate (ABR) streaming system with HLS support, video versioning for re-uploads, and denormalized statistics for performance optimization.

---

## Video

### Purpose
Core model representing a video entity on the platform. Manages video metadata, visibility settings, engagement statistics, and relationships with channels. Supports versioning for video re-uploads and maintains denormalized statistics for performance.

### Class Definition
```python
class Video(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `channel` | ForeignKey | CASCADE, related_name='videos' | Channel that owns this video |
| `active_version` | ForeignKey | SET_NULL, related_name='active_for_video' | Currently active video version |

#### **Content Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `title` | CharField | max_length=200 | Video title |
| `description` | TextField | max_length=10000, optional | Video description/details |

#### **Status & Visibility Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | CharField | `VideoStatus.DRAFT`, indexed | Video processing/publishing status |
| `visibility` | CharField | `VideoVisibility.PUBLIC` | Who can view the video |

#### **Restriction Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `age_restricted` | BooleanField | False | Age restriction flag (18+) |
| `geo_restrictions` | JSONField | [] | List of country codes where video is blocked |

**Example geo_restrictions:**
```json
["US", "CN", "RU"]  // Blocked in USA, China, Russia
```

#### **Thumbnail Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `thumbnail_url` | URLField | '' | Custom or auto-generated thumbnail URL |
| `thumbnail_auto_generated` | BooleanField | True | Whether thumbnail was auto-generated |

#### **Statistics Fields (Denormalized)**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `view_count` | BigIntegerField | 0, indexed | Total view count |
| `like_count` | IntegerField | 0 | Total likes |
| `dislike_count` | IntegerField | 0 | Total dislikes |
| `comment_count` | IntegerField | 0 | Total comments |
| `share_count` | IntegerField | 0 | Total shares |

#### **Engagement Metrics**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `average_watch_time_seconds` | IntegerField | default=0 | Average watch duration |
| `completion_rate` | DecimalField | 0-100%, 2 decimals | Percentage of users who watched to end |

#### **Metadata Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `duration_seconds` | IntegerField | 0 | Video duration in seconds |
| `language` | CharField | 'en' | Primary language code (ISO 639-1) |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `published_at` | DateTimeField | Publication timestamp (indexed) |
| `created_at` | DateTimeField | Creation timestamp (auto, indexed) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |
| `deleted_at` | DateTimeField | Soft delete timestamp |
| `last_activity_at` | DateTimeField | Last engagement activity (for archival) |

### Configuration

**Meta Options:**
- **Database Table:** `videos`
- **Default Ordering:** 
  - `-published_at` (newest published first)
  - `-created_at` (newest created as secondary)
- **Indexes:**
  - `(channel, status)` - Channel's videos by status
  - `(status, visibility, published_at)` - Public video discovery
  - `(view_count)` - Popular videos sorting
  - `(-published_at)` - Chronological ordering

### Properties

#### `is_published`
Checks if video is published and publicly available.

**Returns:** bool

**Logic:** `status == PUBLISHED AND published_at IS NOT NULL`

**Example:**
```python
if video.is_published:
    # Show video to public
    pass
```

### Methods

#### `publish()`
Publishes a video that has completed processing.

**Preconditions:**
- `status` must be `VideoStatus.PROCESSING`
- `active_version` must be set

**Side Effects:**
- Sets `status` to `VideoStatus.PUBLISHED`
- Sets `published_at` to current timestamp
- Saves the model

**Example:**
```python
# After transcoding completes
if video.active_version and video.active_version.transcoding_status == TranscodingStatus.COMPLETED:
    video.publish()
```

#### `increment_view_count(increment_by=1)`
Atomically increments view count and updates last activity timestamp.

**Parameters:**
- `increment_by` (int, default=1): Number to increment by

**Features:**
- Uses `F()` expression for atomic database-level increment
- Updates `last_activity_at` to current timestamp
- Refreshes model from database after update

**Example:**
```python
# User watches video
video.increment_view_count()

# Batch view count update
video.increment_view_count(increment_by=100)
```

**Thread-Safe:** ✅ Yes (uses database-level atomic operations)

#### `__str__()`
**Returns:** `"{title} - {channel_name}"`

### Usage Examples

#### Creating a Draft Video
```python
video = Video.objects.create(
    channel=channel,
    title="How to Build a REST API",
    description="Complete tutorial on building REST APIs with Django",
    language="en",
    age_restricted=False
)
```

#### Setting Geo-Restrictions
```python
video.geo_restrictions = ["CN", "KP"]  # Block in China and North Korea
video.save()
```

#### Publishing After Transcoding
```python
# After transcoding job completes
video_version = video.versions.first()
video_version.transcoding_status = TranscodingStatus.COMPLETED
video_version.transcoding_completed_at = timezone.now()
video_version.save()

video.active_version = video_version
video.duration_seconds = video_version.source_duration_seconds
video.publish()
```

#### Updating Engagement Metrics
```python
# Update completion rate based on analytics
total_views = 10000
completed_views = 6500
video.completion_rate = (completed_views / total_views) * 100
video.save()
```

---

## VideoVersion

### Purpose
Implements versioning system for video re-uploads. Allows creators to replace video content while preserving view counts, comments, and other metadata. Tracks transcoding status and manages source file information.

### Class Definition
```python
class VideoVersion(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `video` | ForeignKey | CASCADE, related_name='versions' | Parent video entity |

#### **Version Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version_number` | IntegerField | 1 | Sequential version number |
| `is_active` | BooleanField | True | Whether this is the active version |

#### **Source File Fields**
| Field | Type | Description |
|-------|------|-------------|
| `source_object_key` | CharField | S3 object key for original upload |
| `source_file_size_bytes` | BigIntegerField | Original file size in bytes |
| `source_duration_seconds` | IntegerField | Video duration in seconds |
| `source_resolution` | CharField | Original resolution (e.g., "1920x1080") |
| `source_codec` | CharField | Video codec (e.g., "H.264", "VP9") |

#### **Transcoding Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `transcoding_profile_set` | CharField | 'standard' | ABR ladder profile (standard, premium, etc.) |
| `transcoding_status` | CharField | `TranscodingStatus.PENDING` | Current transcoding status |
| `transcoding_started_at` | DateTimeField | null | Transcoding start timestamp |
| `transcoding_completed_at` | DateTimeField | null | Transcoding completion timestamp |
| `transcoding_error_message` | TextField | '' | Error details if transcoding failed |

#### **Metadata Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Version creation timestamp (auto) |

### Configuration

**Meta Options:**
- **Database Table:** `video_versions`
- **Default Ordering:** `-version_number` (newest version first)
- **Unique Together:** `(video, version_number)` - Prevents duplicate version numbers
- **Indexes:**
  - `(video, is_active)` - Fast active version lookup

### Methods

#### `__str__()`
**Returns:** `"{video_title} - v{version_number}"`

### Usage Examples

#### Creating First Version
```python
video_version = VideoVersion.objects.create(
    video=video,
    version_number=1,
    source_object_key="uploads/2025/01/video_abc123.mp4",
    source_file_size_bytes=524288000,  # 500 MB
    source_duration_seconds=600,  # 10 minutes
    source_resolution="1920x1080",
    source_codec="H.264"
)
```

#### Re-uploading Video (New Version)
```python
# Deactivate old version
old_version = video.active_version
old_version.is_active = False
old_version.save()

# Create new version
new_version = VideoVersion.objects.create(
    video=video,
    version_number=old_version.version_number + 1,
    source_object_key="uploads/2025/01/video_xyz789.mp4",
    source_file_size_bytes=629145600,  # 600 MB
    source_duration_seconds=720,  # 12 minutes
    source_resolution="3840x2160",  # 4K
    source_codec="H.265"
)

# Set as active after transcoding completes
video.active_version = new_version
video.save()
```

#### Tracking Transcoding Progress
```python
# Start transcoding
video_version.transcoding_status = TranscodingStatus.IN_PROGRESS
video_version.transcoding_started_at = timezone.now()
video_version.save()

# On completion
video_version.transcoding_status = TranscodingStatus.COMPLETED
video_version.transcoding_completed_at = timezone.now()
video_version.save()

# On failure
video_version.transcoding_status = TranscodingStatus.FAILED
video_version.transcoding_error_message = "Invalid codec configuration"
video_version.save()
```

---

## VideoAsset

### Purpose
Represents individual transcoded video assets in the ABR (Adaptive Bitrate) ladder. Each asset corresponds to a specific resolution and bitrate for HLS streaming. Stores playlist URLs and segment paths for video delivery.

### Class Definition
```python
class VideoAsset(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `video_version` | ForeignKey | CASCADE, related_name='assets' | Parent video version |
| `resolution` | CharField | choices=VideoResolution | Video resolution (360p, 720p, 1080p, etc.) |
| `bitrate_kbps` | IntegerField | required | Bitrate in kilobits per second |
| `playlist_url` | URLField | max_length=500 | HLS master or variant playlist URL |
| `segment_path_prefix` | CharField | max_length=500 | S3 prefix for segment files |
| `file_size_bytes` | BigIntegerField | default=0 | Total size of all segments |
| `codec` | CharField | default='H.264' | Video codec used |
| `created_at` | DateTimeField | auto | Asset creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `video_assets`
- **Default Ordering:** `-bitrate_kbps` (highest quality first)
- **Unique Together:** `(video_version, resolution)` - One asset per resolution
- **Indexes:**
  - `(video_version, resolution)` - Fast asset lookup

### Methods

#### `__str__()`
**Returns:** `"{video_title} - {resolution}"`

### Usage Examples

#### Creating ABR Ladder
```python
# After transcoding, create assets for each quality level
assets_config = [
    {'resolution': '360p', 'bitrate': 800, 'file_size': 150000000},
    {'resolution': '480p', 'bitrate': 1400, 'file_size': 250000000},
    {'resolution': '720p', 'bitrate': 2800, 'file_size': 450000000},
    {'resolution': '1080p', 'bitrate': 5000, 'file_size': 750000000},
]

for config in assets_config:
    VideoAsset.objects.create(
        video_version=video_version,
        resolution=config['resolution'],
        bitrate_kbps=config['bitrate'],
        playlist_url=f"https://cdn.example.com/videos/{video.id}/{config['resolution']}/playlist.m3u8",
        segment_path_prefix=f"videos/{video.id}/{config['resolution']}/",
        file_size_bytes=config['file_size'],
        codec="H.264"
    )
```

#### Generating Master Playlist
```python
# Get all assets for a video version
assets = video_version.assets.all()

master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"
for asset in assets:
    master_playlist += f'#EXT-X-STREAM-INF:BANDWIDTH={asset.bitrate_kbps * 1000},RESOLUTION={asset.resolution}\n'
    master_playlist += f'{asset.playlist_url}\n'
```

---

## VideoTag

### Purpose
Manages video tags for categorization and discovery. Tracks tag usage count for trending tags and search optimization.

### Class Definition
```python
class VideoTag(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | CharField | unique, max_length=50, indexed | Tag display name |
| `slug` | SlugField | unique, max_length=50 | URL-friendly tag identifier |
| `usage_count` | IntegerField | default=0 | Number of videos using this tag |
| `created_at` | DateTimeField | auto | Tag creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `video_tags`
- **Default Ordering:** 
  - `-usage_count` (most used first)
  - `name` (alphabetical as secondary)

### Methods

#### `__str__()`
**Returns:** `name`

### Usage Examples

#### Creating Tags
```python
from django.utils.text import slugify

tag = VideoTag.objects.create(
    name="Machine Learning",
    slug=slugify("Machine Learning")
)
```

#### Getting Popular Tags
```python
popular_tags = VideoTag.objects.order_by('-usage_count')[:10]
```

---

## VideoTagRelation

### Purpose
Many-to-many relationship between videos and tags. Allows videos to have multiple tags and tags to be associated with multiple videos.

### Class Definition
```python
class VideoTagRelation(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `video` | ForeignKey | CASCADE, related_name='tag_relations' | Tagged video |
| `tag` | ForeignKey | CASCADE, related_name='video_relations' | Applied tag |
| `created_at` | DateTimeField | auto | Relationship creation timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `video_tag_relations`
- **Unique Together:** `(video, tag)` - Prevents duplicate tags
- **Indexes:**
  - `(video)` - Video's tags lookup
  - `(tag)` - Tag's videos lookup

### Usage Examples

#### Adding Tags to Video
```python
tags = ['python', 'django', 'tutorial']

for tag_name in tags:
    tag, created = VideoTag.objects.get_or_create(
        name=tag_name,
        defaults={'slug': slugify(tag_name)}
    )
    
    VideoTagRelation.objects.create(video=video, tag=tag)
    
    # Increment usage count
    tag.usage_count = models.F('usage_count') + 1
    tag.save()
```

#### Querying Videos by Tag
```python
# Get all videos with 'python' tag
python_videos = Video.objects.filter(
    tag_relations__tag__slug='python',
    status=VideoStatus.PUBLISHED
).distinct()
```

#### Getting Video's Tags
```python
video_tags = VideoTag.objects.filter(
    video_relations__video=video
)
```

---

## Subtitle

### Purpose
Manages video subtitles and captions in multiple languages. Supports both manually uploaded and auto-generated subtitles in WebVTT format.

### Class Definition
```python
class Subtitle(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `video_version` | ForeignKey | CASCADE, related_name='subtitles' | Parent video version |
| `language_code` | CharField | max_length=5 | ISO 639-1 language code |
| `language_name` | CharField | max_length=50 | Human-readable language name |
| `file_key` | CharField | max_length=500 | S3 key for WebVTT file |
| `file_url` | URLField | max_length=500 | Public URL for subtitle file |
| `is_published` | BooleanField | default=True | Visibility status |
| `is_auto_generated` | BooleanField | default=False | Whether generated by AI/speech recognition |
| `created_at` | DateTimeField | auto | Subtitle creation timestamp |
| `updated_at` | DateTimeField | auto | Last update timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `subtitles`
- **Unique Together:** `(video_version, language_code)` - One subtitle per language
- **Indexes:**
  - `(video_version, language_code)` - Fast subtitle lookup

### Methods

#### `__str__()`
**Returns:** `"{video_title} - {language_name}"`

### Usage Examples

#### Adding Manual Subtitles
```python
subtitle = Subtitle.objects.create(
    video_version=video_version,
    language_code="en",
    language_name="English",
    file_key="subtitles/video_123/en.vtt",
    file_url="https://cdn.example.com/subtitles/video_123/en.vtt",
    is_auto_generated=False
)
```

#### Adding Auto-Generated Subtitles
```python
subtitle = Subtitle.objects.create(
    video_version=video_version,
    language_code="es",
    language_name="Spanish",
    file_key="subtitles/video_123/es_auto.vtt",
    file_url="https://cdn.example.com/subtitles/video_123/es_auto.vtt",
    is_auto_generated=True
)
```

#### Getting Available Subtitles
```python
available_subtitles = video_version.subtitles.filter(
    is_published=True
).values('language_code', 'language_name', 'file_url')
```

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .choices import (
    VideoStatus,
    VideoVisibility,
    VideoResolution,
    TranscodingStatus,
)
```

### External Choice Classes
The following choice classes must be defined in `choices.py`:
- **VideoStatus**: DRAFT, PROCESSING, PUBLISHED, ARCHIVED, DELETED
- **VideoVisibility**: PUBLIC, UNLISTED, PRIVATE
- **VideoResolution**: 360p, 480p, 720p, 1080p, 1440p, 2160p (4K)
- **TranscodingStatus**: PENDING, IN_PROGRESS, COMPLETED, FAILED

### Related Models
- **Channel**: From channel models (ForeignKey relationship)

---

## Best Practices

1. **Always use atomic operations** for counter updates (`F()` expressions)
2. **Keep denormalized stats in sync** with actual data
3. **Use soft delete** (`deleted_at`) to preserve video history
4. **Validate video quotas** before allowing uploads
5. **Generate thumbnails** at multiple timestamps for user selection
6. **Implement CDN caching** for video assets and thumbnails
7. **Clean up old video versions** after retention period
8. **Monitor transcoding failures** and implement retry logic
9. **Use HLS for adaptive streaming** to optimize bandwidth
10. **Index geo_restrictions** if frequently queried

---

## Performance Considerations

1. **Denormalized Statistics**: Keep view counts, likes, etc. in sync
2. **Lazy Loading**: Use `select_related()` and `prefetch_related()` for queries
3. **CDN Integration**: Serve video assets and thumbnails via CDN
4. **Batch Updates**: Update engagement metrics in batches, not per view
5. **Archive Old Videos**: Move inactive videos to cold storage after 1+ years

---

# Interaction & Engagement Models Documentation

## Overview
This module contains models for tracking user interactions, watch sessions, and playlist management. It provides comprehensive analytics capabilities including view tracking, engagement metrics, quality of experience (QoE) measurements, and user-generated content organization through playlists.

---

## Interaction

### Purpose
Tracks all user interactions with videos including views, likes, dislikes, and watch time. Supports both authenticated and anonymous users through session tracking. Provides granular interaction data for analytics and recommendation systems.

### Class Definition
```python
class Interaction(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='interactions', nullable | User who performed interaction (null for anonymous) |
| `video` | ForeignKey | CASCADE, related_name='interactions' | Video being interacted with |

#### **Interaction Data**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `type` | CharField | max_length=20, choices=InteractionType | Type of interaction (VIEW, LIKE, DISLIKE, WATCH_TIME) |
| `value` | IntegerField | default=0 | Watch time in seconds OR binary flag (1/0) for like/dislike |

**Value Field Usage:**
- **LIKE/DISLIKE**: `1` (active) or `0` (removed)
- **WATCH_TIME**: Duration in seconds
- **VIEW**: Typically `1` to indicate view occurred

#### **Session Tracking Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | CharField | max_length=100, indexed | Unique session identifier for anonymous tracking |
| `ip_address` | GenericIPAddressField | nullable | User's IP address (IPv4 or IPv6) |
| `user_agent` | CharField | max_length=500 | Browser user agent string |

#### **Metadata Fields**
| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | DateTimeField | Interaction timestamp (auto, indexed) |

### Configuration

**Meta Options:**
- **Database Table:** `interactions`
- **Default Ordering:** `-timestamp` (newest first)
- **Indexes:**
  - `(video, type, timestamp)` - Video interaction analytics
  - `(user, video, type)` - User-video interaction lookup
  - `(session_id)` - Anonymous session tracking

### Methods

#### `__str__()`
**Returns:** `"{username/Anonymous} - {type} - {video_title}"`

**Example Output:**
```
"johndoe - LIKE - How to Build REST APIs"
"Anonymous - VIEW - Python Tutorial"
```

### Usage Examples

#### Recording a View (Authenticated User)
```python
from .choices import InteractionType

interaction = Interaction.objects.create(
    user=request.user,
    video=video,
    type=InteractionType.VIEW,
    value=1,
    session_id=request.session.session_key,
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)

# Increment video view count
video.increment_view_count()
```

#### Recording a View (Anonymous User)
```python
import uuid

# Generate session ID if not exists
session_id = request.session.session_key or str(uuid.uuid4())

interaction = Interaction.objects.create(
    user=None,  # Anonymous
    video=video,
    type=InteractionType.VIEW,
    value=1,
    session_id=session_id,
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)
```

#### Recording a Like
```python
# Check if user already liked
existing_like = Interaction.objects.filter(
    user=request.user,
    video=video,
    type=InteractionType.LIKE
).first()

if existing_like:
    # Toggle like off
    existing_like.delete()
    video.like_count = models.F('like_count') - 1
else:
    # Add new like
    Interaction.objects.create(
        user=request.user,
        video=video,
        type=InteractionType.LIKE,
        value=1,
        session_id=request.session.session_key
    )
    video.like_count = models.F('like_count') + 1

video.save()
video.refresh_from_db()
```

#### Recording Watch Time
```python
# Update watch time periodically (e.g., every 10 seconds)
Interaction.objects.create(
    user=request.user,
    video=video,
    type=InteractionType.WATCH_TIME,
    value=10,  # 10 seconds watched
    session_id=request.session.session_key
)
```

#### Preventing Duplicate Views
```python
from django.utils import timezone
from datetime import timedelta

# Check if user/session viewed in last 24 hours
recent_view = Interaction.objects.filter(
    video=video,
    type=InteractionType.VIEW,
    timestamp__gte=timezone.now() - timedelta(hours=24)
).filter(
    models.Q(user=request.user) | models.Q(session_id=request.session.session_key)
).exists()

if not recent_view:
    # Record new view
    Interaction.objects.create(...)
    video.increment_view_count()
```

#### Analytics Queries

**Get video's like/dislike ratio:**
```python
likes = Interaction.objects.filter(
    video=video,
    type=InteractionType.LIKE
).count()

dislikes = Interaction.objects.filter(
    video=video,
    type=InteractionType.DISLIKE
).count()

ratio = likes / (likes + dislikes) if (likes + dislikes) > 0 else 0
```

**Get user's interaction history:**
```python
user_interactions = Interaction.objects.filter(
    user=request.user
).select_related('video', 'video__channel').order_by('-timestamp')[:50]
```

**Get trending videos (most views in last 7 days):**
```python
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

trending = Video.objects.filter(
    interactions__type=InteractionType.VIEW,
    interactions__timestamp__gte=timezone.now() - timedelta(days=7)
).annotate(
    recent_views=Count('interactions')
).order_by('-recent_views')[:20]
```

---

## WatchSession

### Purpose
Provides detailed analytics for individual watch sessions. Tracks quality of experience (QoE) metrics including buffering events, startup time, bitrate adaptation, and completion rates. Essential for video performance optimization and user experience analysis.

### Class Definition
```python
class WatchSession(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='watch_sessions', nullable | User watching video (null for anonymous) |
| `video` | ForeignKey | CASCADE, related_name='watch_sessions' | Video being watched |

#### **Session Identification**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | CharField | max_length=100, indexed | Unique session identifier |

#### **Watch Metrics**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `watch_time_seconds` | IntegerField | 0 | Total time spent watching (excluding pauses) |
| `completion_percentage` | DecimalField | 0.0 | Percentage of video watched (0-100) |

#### **Quality of Experience (QoE) Metrics**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rebuffer_count` | IntegerField | 0 | Number of buffering events |
| `rebuffer_duration_seconds` | IntegerField | 0 | Total time spent buffering |
| `startup_time_ms` | IntegerField | 0 | Time from play to first frame (milliseconds) |
| `average_bitrate_kbps` | IntegerField | 0 | Average streaming bitrate |

#### **Device & Network Context**
| Field | Type | Description |
|-------|------|-------------|
| `device_type` | CharField | Device category (mobile, tablet, desktop, tv) |
| `browser` | CharField | Browser name and version |
| `os` | CharField | Operating system |
| `ip_address` | GenericIPAddressField | User's IP address |
| `country_code` | CharField | ISO 3166-1 alpha-2 country code |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `started_at` | DateTimeField | Session start timestamp (auto) |
| `ended_at` | DateTimeField | Session end timestamp (nullable) |

### Configuration

**Meta Options:**
- **Database Table:** `watch_sessions`
- **Default Ordering:** `-started_at` (newest first)
- **Indexes:**
  - `(video, started_at)` - Video watch history
  - `(user, started_at)` - User watch history
  - `(session_id)` - Session lookup

### Methods

#### `__str__()`
**Returns:** `"{username/Anonymous} - {video_title} - {watch_time}s"`

### Usage Examples

#### Starting a Watch Session
```python
import uuid
from user_agents import parse

# Parse user agent
user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

watch_session = WatchSession.objects.create(
    user=request.user if request.user.is_authenticated else None,
    video=video,
    session_id=str(uuid.uuid4()),
    device_type='mobile' if user_agent.is_mobile else 'desktop',
    browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
    os=f"{user_agent.os.family} {user_agent.os.version_string}",
    ip_address=request.META.get('REMOTE_ADDR'),
    country_code=get_country_from_ip(request.META.get('REMOTE_ADDR'))
)
```

#### Updating Watch Session (Periodic Updates)
```python
from django.utils import timezone

# Client sends updates every 10 seconds
watch_session.watch_time_seconds += 10
watch_session.completion_percentage = (
    watch_session.watch_time_seconds / video.duration_seconds * 100
)
watch_session.save()
```

#### Recording Quality Metrics
```python
# Client reports buffering event
watch_session.rebuffer_count += 1
watch_session.rebuffer_duration_seconds += 3  # 3 seconds of buffering
watch_session.save()

# Update average bitrate
watch_session.average_bitrate_kbps = (
    (watch_session.average_bitrate_kbps * samples + new_bitrate) / (samples + 1)
)
watch_session.save()
```

#### Ending a Watch Session
```python
from django.utils import timezone

watch_session.ended_at = timezone.now()
watch_session.completion_percentage = (
    watch_session.watch_time_seconds / video.duration_seconds * 100
)
watch_session.save()

# Update video's average watch time
video.average_watch_time_seconds = WatchSession.objects.filter(
    video=video
).aggregate(avg=models.Avg('watch_time_seconds'))['avg']
video.save()
```

#### Analytics Queries

**Get average completion rate for video:**
```python
avg_completion = WatchSession.objects.filter(
    video=video
).aggregate(avg=models.Avg('completion_percentage'))['avg']
```

**Get videos with high rebuffer rates:**
```python
problematic_videos = Video.objects.annotate(
    avg_rebuffers=models.Avg('watch_sessions__rebuffer_count')
).filter(avg_rebuffers__gt=2).order_by('-avg_rebuffers')
```

**Get user's watch history:**
```python
watch_history = WatchSession.objects.filter(
    user=request.user
).select_related('video', 'video__channel').order_by('-started_at')[:20]
```

**Device type distribution:**
```python
from django.db.models import Count

device_stats = WatchSession.objects.filter(
    video=video
).values('device_type').annotate(
    count=Count('id')
).order_by('-count')
```

**Geographic distribution:**
```python
geo_stats = WatchSession.objects.filter(
    video=video,
    country_code__isnull=False
).values('country_code').annotate(
    views=Count('id')
).order_by('-views')[:10]
```

---

## Playlist

### Purpose
Manages user-created playlists for organizing and curating video collections. Supports both public and private playlists for personal organization or content sharing.

### Class Definition
```python
class Playlist(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='playlists' | Playlist owner |

#### **Playlist Information**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `title` | CharField | max_length=150 | Playlist name |
| `description` | TextField | max_length=1000, optional | Playlist description |

#### **Visibility**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_public` | BooleanField | True | Whether playlist is publicly visible |

#### **Metadata Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Creation timestamp (auto) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |

### Configuration

**Meta Options:**
- **Database Table:** `playlists`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(user, is_public)` - User's playlists filtering

### Methods

#### `__str__()`
**Returns:** `"{title} by {username}"`

### Usage Examples

#### Creating a Playlist
```python
playlist = Playlist.objects.create(
    user=request.user,
    title="My Favorite Tech Tutorials",
    description="Collection of the best programming tutorials",
    is_public=True
)
```

#### Updating Playlist
```python
playlist.title = "Updated Playlist Name"
playlist.description = "New description"
playlist.save()
```

#### Querying User's Playlists
```python
# Get all user's playlists
user_playlists = Playlist.objects.filter(user=request.user)

# Get public playlists only
public_playlists = Playlist.objects.filter(
    user=request.user,
    is_public=True
)
```

#### Discovering Public Playlists
```python
# Get all public playlists
public_playlists = Playlist.objects.filter(
    is_public=True
).select_related('user')

# Get playlists by specific user
user_public_playlists = Playlist.objects.filter(
    user=creator_user,
    is_public=True
)
```

---

## PlaylistItem

### Purpose
Manages the many-to-many relationship between playlists and videos. Maintains video ordering within playlists and prevents duplicate entries.

### Class Definition
```python
class PlaylistItem(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `playlist` | ForeignKey | CASCADE, related_name='items' | Parent playlist |
| `video` | ForeignKey | CASCADE, related_name='playlist_items' | Video in playlist |
| `position` | IntegerField | default=0 | Order position in playlist (0-based) |
| `added_at` | DateTimeField | auto | Timestamp when video was added |

### Configuration

**Meta Options:**
- **Database Table:** `playlist_items`
- **Default Ordering:** 
  - `position` (custom order first)
  - `added_at` (chronological as secondary)
- **Unique Together:** `(playlist, video)` - Prevents duplicate videos
- **Indexes:**
  - `(playlist, position)` - Ordered playlist retrieval

### Methods

#### `__str__()`
**Returns:** `"{playlist_title} - {video_title}"`

### Usage Examples

#### Adding Video to Playlist
```python
# Get next position
max_position = PlaylistItem.objects.filter(
    playlist=playlist
).aggregate(max=models.Max('position'))['max'] or -1

PlaylistItem.objects.create(
    playlist=playlist,
    video=video,
    position=max_position + 1
)
```

#### Adding Multiple Videos
```python
videos_to_add = [video1, video2, video3]
max_position = PlaylistItem.objects.filter(
    playlist=playlist
).aggregate(max=models.Max('position'))['max'] or -1

items = []
for i, video in enumerate(videos_to_add, start=1):
    items.append(PlaylistItem(
        playlist=playlist,
        video=video,
        position=max_position + i
    ))

PlaylistItem.objects.bulk_create(items, ignore_conflicts=True)
```

#### Removing Video from Playlist
```python
PlaylistItem.objects.filter(
    playlist=playlist,
    video=video
).delete()

# Reorder remaining items
items = PlaylistItem.objects.filter(playlist=playlist).order_by('position')
for i, item in enumerate(items):
    item.position = i
    item.save()
```

#### Reordering Videos
```python
# Move video from position 5 to position 2
item = PlaylistItem.objects.get(playlist=playlist, video=video)
old_position = item.position
new_position = 2

if new_position < old_position:
    # Moving up: shift items down
    PlaylistItem.objects.filter(
        playlist=playlist,
        position__gte=new_position,
        position__lt=old_position
    ).update(position=models.F('position') + 1)
else:
    # Moving down: shift items up
    PlaylistItem.objects.filter(
        playlist=playlist,
        position__gt=old_position,
        position__lte=new_position
    ).update(position=models.F('position') - 1)

item.position = new_position
item.save()
```

#### Getting Playlist Videos
```python
# Get all videos in playlist (ordered)
playlist_videos = Video.objects.filter(
    playlist_items__playlist=playlist
).order_by('playlist_items__position')

# With prefetching for performance
playlist_items = PlaylistItem.objects.filter(
    playlist=playlist
).select_related('video', 'video__channel').order_by('position')
```

#### Checking if Video is in Playlist
```python
is_in_playlist = PlaylistItem.objects.filter(
    playlist=playlist,
    video=video
).exists()
```

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.core.validators import MinValueValidator
from .choices import InteractionType
```

### External Choice Classes
The following choice class must be defined in `choices.py`:
- **InteractionType**: VIEW, LIKE, DISLIKE, WATCH_TIME, SHARE, etc.

### Related Models
- **User**: From authentication models
- **Video**: From video models
- **Channel**: Indirectly through Video

---

## Best Practices

### Interaction Tracking
1. **Deduplicate views** using session/user + timestamp checks
2. **Rate limit interactions** to prevent spam (e.g., max 1 like toggle per second)
3. **Batch process** interaction data for analytics (don't update denormalized stats on every interaction)
4. **Archive old interactions** after 1-2 years to separate hot/cold data
5. **Use async tasks** for heavy analytics calculations

### Watch Session Management
1. **Send periodic updates** from client (every 5-10 seconds)
2. **Handle session abandonment** - mark sessions as ended after timeout
3. **Aggregate QoE metrics** for performance dashboards
4. **Monitor rebuffer rates** to identify CDN/encoding issues
5. **Respect user privacy** - anonymize IP addresses after geolocation

### Playlist Management
1. **Validate video availability** before adding to playlist
2. **Limit playlist size** (e.g., max 500 videos)
3. **Cache playlist data** for frequently accessed public playlists
4. **Implement playlist sharing** with unique URLs
5. **Allow collaborative playlists** for advanced features

---

## Performance Considerations

### Indexing Strategy
- **Interaction queries** are optimized for:
  - Video analytics: `(video, type, timestamp)`
  - User history: `(user, video, type)`
  - Anonymous tracking: `(session_id)`

- **WatchSession queries** are optimized for:
  - Video performance: `(video, started_at)`
  - User history: `(user, started_at)`

### Data Volume Management
```python
# Archive old interactions (keep last 90 days hot)
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=90)
old_interactions = Interaction.objects.filter(timestamp__lt=cutoff_date)
# Move to archive table or cold storage
```

### Caching Strategies
```python
from django.core.cache import cache

# Cache user's liked videos
def get_user_liked_videos(user_id):
    cache_key = f'user_likes:{user_id}'
    liked_videos = cache.get(cache_key)
    
    if liked_videos is None:
        liked_videos = list(Video.objects.filter(
            interactions__user_id=user_id,
            interactions__type=InteractionType.LIKE
        ).values_list('id', flat=True))
        cache.set(cache_key, liked_videos, 3600)  # 1 hour
    
    return liked_videos
```

---

## Security Considerations

1. **Validate ownership** before modifying playlists
2. **Rate limit** interaction endpoints (prevent like/view spam)
3. **Sanitize user agents** before storing (prevent injection)
4. **Anonymize IP addresses** after geolocation (GDPR compliance)
5. **Implement CAPTCHA** for anonymous interactions if abuse detected
6. **Validate session IDs** to prevent session hijacking
7. **Log suspicious patterns** (e.g., same IP with many sessions)

---

# Comment System Models Documentation

## Overview
This module implements a comprehensive comment system with threading support, reactions (likes/dislikes), moderation capabilities, and soft deletion. It features a 2-level threading structure (parent comments + replies), denormalized statistics for performance, and flexible moderation workflows.

---

## Comment

### Purpose
Core model for video comments supporting 2-level threading (parent comments and replies). Includes moderation features, engagement statistics, edit tracking, and soft deletion. Designed for high-performance comment retrieval with denormalized counters.

### Class Definition
```python
class Comment(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `video` | ForeignKey | CASCADE, related_name='comments' | Video being commented on |
| `user` | ForeignKey | CASCADE, related_name='comments' | Comment author |
| `parent` | ForeignKey | CASCADE, related_name='replies', nullable | Parent comment (null for top-level comments) |

#### **Content Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `text` | TextField | max_length=2000 | Comment content |

#### **Status & Moderation**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | CharField | CommentStatus.ACTIVE, choices | Comment moderation status |
| `edited` | BooleanField | False | Whether comment has been edited |
| `edited_at` | DateTimeField | nullable | Last edit timestamp |

#### **Statistics (Denormalized)**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `like_count` | IntegerField | 0 | Total likes on comment |
| `dislike_count` | IntegerField | 0 | Total dislikes on comment |
| `reply_count` | IntegerField | 0 | Number of direct replies |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Creation timestamp (auto, indexed) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |
| `deleted_at` | DateTimeField | Soft delete timestamp (nullable) |

### Configuration

**Meta Options:**
- **Database Table:** `comments`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(video, status, created_at)` - Video's comments by status
  - `(user, created_at)` - User's comment history
  - `(parent)` - Reply lookup

### Properties

#### `is_reply`
Determines if comment is a reply to another comment.

**Returns:** bool

**Logic:** `parent IS NOT NULL`

**Example:**
```python
if comment.is_reply:
    print(f"Reply to: {comment.parent.text[:50]}")
else:
    print("Top-level comment")
```

### Methods

#### `__str__()`
**Returns:** `"{username} on {video_title}"`

**Example Output:**
```
"johndoe on How to Build REST APIs"
```

### Usage Examples

#### Creating a Top-Level Comment
```python
comment = Comment.objects.create(
    video=video,
    user=request.user,
    text="Great tutorial! Very helpful explanation.",
    status=CommentStatus.ACTIVE
)

# Increment video's comment count
video.comment_count = models.F('comment_count') + 1
video.save()
```

#### Creating a Reply
```python
reply = Comment.objects.create(
    video=video,
    user=request.user,
    parent=parent_comment,
    text="I agree! This helped me solve my problem.",
    status=CommentStatus.ACTIVE
)

# Increment parent's reply count
parent_comment.reply_count = models.F('reply_count') + 1
parent_comment.save()

# Increment video's comment count
video.comment_count = models.F('comment_count') + 1
video.save()
```

#### Editing a Comment
```python
from django.utils import timezone

comment.text = "Updated comment text"
comment.edited = True
comment.edited_at = timezone.now()
comment.save()
```

#### Soft Deleting a Comment
```python
from django.utils import timezone

comment.status = CommentStatus.DELETED
comment.deleted_at = timezone.now()
comment.save()

# Decrement video's comment count
video.comment_count = models.F('comment_count') - 1
video.save()

# If it's a reply, decrement parent's reply count
if comment.parent:
    comment.parent.reply_count = models.F('reply_count') - 1
    comment.parent.save()
```

#### Moderating Comments
```python
# Flag comment for review
comment.status = CommentStatus.PENDING_REVIEW
comment.save()

# Hide spam comment
comment.status = CommentStatus.HIDDEN
comment.save()

# Restore hidden comment
comment.status = CommentStatus.ACTIVE
comment.save()
```

#### Querying Comments

**Get video's top-level comments:**
```python
top_level_comments = Comment.objects.filter(
    video=video,
    parent__isnull=True,
    status=CommentStatus.ACTIVE
).select_related('user').order_by('-created_at')
```

**Get comment with replies:**
```python
comment_with_replies = Comment.objects.prefetch_related(
    'replies__user'
).get(id=comment_id)

# Access replies
for reply in comment_with_replies.replies.filter(status=CommentStatus.ACTIVE):
    print(f"  → {reply.user.username}: {reply.text}")
```

**Get user's comment history:**
```python
user_comments = Comment.objects.filter(
    user=request.user,
    status=CommentStatus.ACTIVE
).select_related('video', 'video__channel').order_by('-created_at')
```

**Get most liked comments:**
```python
popular_comments = Comment.objects.filter(
    video=video,
    parent__isnull=True,
    status=CommentStatus.ACTIVE
).order_by('-like_count', '-created_at')[:10]
```

**Get comments pending moderation:**
```python
pending_comments = Comment.objects.filter(
    status=CommentStatus.PENDING_REVIEW
).select_related('user', 'video').order_by('created_at')
```

#### Pagination Example
```python
from django.core.paginator import Paginator

# Paginate top-level comments
comments = Comment.objects.filter(
    video=video,
    parent__isnull=True,
    status=CommentStatus.ACTIVE
).select_related('user')

paginator = Paginator(comments, 20)  # 20 comments per page
page_obj = paginator.get_page(page_number)

for comment in page_obj:
    # Load replies for each comment (limit to 3 initially)
    replies = comment.replies.filter(
        status=CommentStatus.ACTIVE
    ).select_related('user')[:3]
```

#### Nested Comment Structure Example
```python
def get_comment_tree(video_id):
    """Get comments with nested replies"""
    # Get top-level comments
    comments = Comment.objects.filter(
        video_id=video_id,
        parent__isnull=True,
        status=CommentStatus.ACTIVE
    ).prefetch_related(
        models.Prefetch(
            'replies',
            queryset=Comment.objects.filter(
                status=CommentStatus.ACTIVE
            ).select_related('user').order_by('created_at')
        )
    ).select_related('user').order_by('-created_at')
    
    return comments
```

---

## CommentReaction

### Purpose
Manages user reactions (likes/dislikes) on comments. Enforces one reaction per user per comment and maintains denormalized counters on the Comment model for performance.

### Class Definition
```python
class CommentReaction(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `comment` | ForeignKey | CASCADE, related_name='reactions' | Comment being reacted to |
| `user` | ForeignKey | CASCADE, related_name='comment_reactions' | User performing reaction |
| `is_like` | BooleanField | required | True = like, False = dislike |
| `created_at` | DateTimeField | auto | Reaction timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `comment_reactions`
- **Unique Together:** `(comment, user)` - One reaction per user per comment
- **Indexes:**
  - `(comment, is_like)` - Count likes/dislikes
  - `(user)` - User's reaction history

### Methods

#### `__str__()`
**Returns:** `"{username} {liked/disliked} comment"`

**Example Output:**
```
"johndoe liked comment"
"janedoe disliked comment"
```

### Usage Examples

#### Adding a Like
```python
from django.db import IntegrityError

try:
    reaction = CommentReaction.objects.create(
        comment=comment,
        user=request.user,
        is_like=True
    )
    
    # Increment like count
    comment.like_count = models.F('like_count') + 1
    comment.save()
    comment.refresh_from_db()
    
except IntegrityError:
    # User already reacted, handle toggle
    pass
```

#### Toggling Like/Dislike
```python
from django.db import transaction

@transaction.atomic
def toggle_comment_reaction(comment_id, user, is_like):
    """Toggle like/dislike on a comment"""
    comment = Comment.objects.select_for_update().get(id=comment_id)
    
    try:
        # Try to get existing reaction
        reaction = CommentReaction.objects.get(comment=comment, user=user)
        
        if reaction.is_like == is_like:
            # Same reaction - remove it
            reaction.delete()
            if is_like:
                comment.like_count = models.F('like_count') - 1
            else:
                comment.dislike_count = models.F('dislike_count') - 1
            comment.save()
            return None
        else:
            # Different reaction - switch it
            reaction.is_like = is_like
            reaction.save()
            
            if is_like:
                comment.like_count = models.F('like_count') + 1
                comment.dislike_count = models.F('dislike_count') - 1
            else:
                comment.like_count = models.F('like_count') - 1
                comment.dislike_count = models.F('dislike_count') + 1
            comment.save()
            return reaction
            
    except CommentReaction.DoesNotExist:
        # No existing reaction - create new one
        reaction = CommentReaction.objects.create(
            comment=comment,
            user=user,
            is_like=is_like
        )
        
        if is_like:
            comment.like_count = models.F('like_count') + 1
        else:
            comment.dislike_count = models.F('dislike_count') + 1
        comment.save()
        return reaction
```

#### Removing a Reaction
```python
try:
    reaction = CommentReaction.objects.get(comment=comment, user=request.user)
    
    # Decrement counter
    if reaction.is_like:
        comment.like_count = models.F('like_count') - 1
    else:
        comment.dislike_count = models.F('dislike_count') - 1
    comment.save()
    
    reaction.delete()
    
except CommentReaction.DoesNotExist:
    pass
```

#### Checking User's Reaction
```python
def get_user_reaction(comment_id, user_id):
    """Get user's reaction on a comment"""
    try:
        reaction = CommentReaction.objects.get(
            comment_id=comment_id,
            user_id=user_id
        )
        return 'like' if reaction.is_like else 'dislike'
    except CommentReaction.DoesNotExist:
        return None
```

#### Bulk Loading User Reactions
```python
def get_comments_with_user_reactions(video_id, user_id):
    """Get comments with user's reactions pre-loaded"""
    comments = Comment.objects.filter(
        video_id=video_id,
        parent__isnull=True,
        status=CommentStatus.ACTIVE
    ).select_related('user')
    
    # Get all user's reactions for these comments
    comment_ids = [c.id for c in comments]
    user_reactions = {
        r.comment_id: r.is_like 
        for r in CommentReaction.objects.filter(
            comment_id__in=comment_ids,
            user_id=user_id
        )
    }
    
    # Attach reaction info to comments
    for comment in comments:
        comment.user_reaction = user_reactions.get(comment.id)
    
    return comments
```

#### Analytics Queries

**Get most controversial comments (high engagement):**
```python
controversial = Comment.objects.filter(
    video=video,
    status=CommentStatus.ACTIVE
).annotate(
    total_reactions=models.F('like_count') + models.F('dislike_count')
).filter(
    total_reactions__gte=10
).order_by('-total_reactions')
```

**Get like/dislike ratio:**
```python
from django.db.models import F, Case, When, FloatField

comments_with_ratio = Comment.objects.filter(
    video=video,
    status=CommentStatus.ACTIVE
).annotate(
    like_ratio=Case(
        When(
            like_count__gt=0,
            dislike_count__gt=0,
            then=F('like_count') * 1.0 / (F('like_count') + F('dislike_count'))
        ),
        default=0.0,
        output_field=FloatField()
    )
).order_by('-like_ratio')
```

**Get user's liked comments:**
```python
liked_comments = Comment.objects.filter(
    reactions__user=request.user,
    reactions__is_like=True
).select_related('video', 'user').order_by('-reactions__created_at')
```

---

## Dependencies

### Required Imports
```python
from django.db import models
from .choices import CommentStatus
```

### External Choice Classes
The following choice class must be defined in `choices.py`:
- **CommentStatus**: ACTIVE, PENDING_REVIEW, HIDDEN, DELETED, FLAGGED

**Example CommentStatus definition:**
```python
class CommentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PENDING_REVIEW = 'pending_review', 'Pending Review'
    HIDDEN = 'hidden', 'Hidden'
    DELETED = 'deleted', 'Deleted'
    FLAGGED = 'flagged', 'Flagged'
```

### Related Models
- **User**: From authentication models
- **Video**: From video models

---

## Best Practices

### Comment Management

1. **Validate Comment Depth**
```python
def create_comment(video, user, text, parent=None):
    """Create comment with depth validation"""
    if parent and parent.parent:
        raise ValueError("Maximum comment depth (2 levels) exceeded")
    
    if parent and parent.video_id != video.id:
        raise ValueError("Parent comment must belong to same video")
    
    return Comment.objects.create(
        video=video,
        user=user,
        text=text,
        parent=parent
    )
```

2. **Rate Limiting**
```python
from django.core.cache import cache
from django.utils import timezone

def check_comment_rate_limit(user_id):
    """Allow max 10 comments per minute"""
    cache_key = f'comment_rate:{user_id}'
    count = cache.get(cache_key, 0)
    
    if count >= 10:
        raise ValueError("Rate limit exceeded. Please wait.")
    
    cache.set(cache_key, count + 1, 60)  # 60 seconds
```

3. **Content Moderation**
```python
def moderate_comment(text):
    """Check for spam/inappropriate content"""
    # Implement profanity filter
    # Check for spam patterns
    # Use ML-based moderation
    
    if contains_spam(text):
        return CommentStatus.PENDING_REVIEW
    return CommentStatus.ACTIVE
```

4. **Notification System**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    """Notify video owner and parent comment author"""
    if created and instance.status == CommentStatus.ACTIVE:
        # Notify video owner
        if instance.video.channel.user != instance.user:
            create_notification(
                user=instance.video.channel.user,
                type='new_comment',
                comment=instance
            )
        
        # Notify parent comment author
        if instance.parent and instance.parent.user != instance.user:
            create_notification(
                user=instance.parent.user,
                type='comment_reply',
                comment=instance
            )
```

### Performance Optimization

1. **Efficient Comment Loading**
```python
def get_video_comments_optimized(video_id, page=1, per_page=20):
    """Load comments with optimal queries"""
    offset = (page - 1) * per_page
    
    # Get top-level comments with user info
    comments = Comment.objects.filter(
        video_id=video_id,
        parent__isnull=True,
        status=CommentStatus.ACTIVE
    ).select_related('user').prefetch_related(
        models.Prefetch(
            'replies',
            queryset=Comment.objects.filter(
                status=CommentStatus.ACTIVE
            ).select_related('user').order_by('created_at')[:3]
        )
    )[offset:offset + per_page]
    
    return comments
```

2. **Caching Popular Comments**
```python
from django.core.cache import cache

def get_top_comments_cached(video_id, count=10):
    """Get top comments with caching"""
    cache_key = f'top_comments:{video_id}'
    comments = cache.get(cache_key)
    
    if comments is None:
        comments = list(Comment.objects.filter(
            video_id=video_id,
            parent__isnull=True,
            status=CommentStatus.ACTIVE
        ).select_related('user').order_by('-like_count')[:count])
        
        cache.set(cache_key, comments, 300)  # 5 minutes
    
    return comments
```

3. **Batch Counter Updates**
```python
from django.db.models import Count, Q

def sync_comment_counters(video_id):
    """Sync denormalized counters with actual data"""
    # Update reply counts
    Comment.objects.filter(
        video_id=video_id,
        parent__isnull=True
    ).update(
        reply_count=models.Subquery(
            Comment.objects.filter(
                parent=models.OuterRef('pk'),
                status=CommentStatus.ACTIVE
            ).values('parent').annotate(
                count=Count('id')
            ).values('count')
        )
    )
    
    # Update like/dislike counts
    for comment in Comment.objects.filter(video_id=video_id):
        reactions = CommentReaction.objects.filter(comment=comment).aggregate(
            likes=Count('id', filter=Q(is_like=True)),
            dislikes=Count('id', filter=Q(is_like=False))
        )
        comment.like_count = reactions['likes']
        comment.dislike_count = reactions['dislikes']
        comment.save(update_fields=['like_count', 'dislike_count'])
```

---

## Security Considerations

1. **Authorization Checks**
```python
def can_edit_comment(comment, user):
    """Check if user can edit comment"""
    return comment.user == user and comment.status == CommentStatus.ACTIVE

def can_delete_comment(comment, user):
    """Check if user can delete comment"""
    return (
        comment.user == user or 
        comment.video.channel.user == user or
        user.is_staff
    )
```

2. **XSS Prevention**
```python
from django.utils.html import escape

def sanitize_comment_text(text):
    """Sanitize comment text to prevent XSS"""
    return escape(text)
```

3. **Spam Prevention**
```python
def is_spam_comment(text, user):
    """Detect spam comments"""
    # Check for duplicate content
    recent_duplicate = Comment.objects.filter(
        user=user,
        text=text,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).exists()
    
    if recent_duplicate:
        return True
    
    # Check for excessive links
    if text.count('http') > 2:
        return True
    
    return False
```

4. **Soft Delete Implementation**
```python
def soft_delete_comment(comment):
    """Soft delete comment and update counters"""
    comment.status = CommentStatus.DELETED
    comment.deleted_at = timezone.now()
    comment.save()
    
    # Update video comment count
    comment.video.comment_count = models.F('comment_count') - 1
    comment.video.save()
    
    # Update parent reply count
    if comment.parent:
        comment.parent.reply_count = models.F('reply_count') - 1
        comment.parent.save()
```

---

## Threading Architecture

### 2-Level Structure
```
Video
├── Comment 1 (parent=None)
│   ├── Reply 1.1 (parent=Comment 1)
│   ├── Reply 1.2 (parent=Comment 1)
│   └── Reply 1.3 (parent=Comment 1)
├── Comment 2 (parent=None)
│   └── Reply 2.1 (parent=Comment 2)
└── Comment 3 (parent=None)
```

**Why 2 levels?**
- Simplifies UI/UX
- Prevents deeply nested threads
- Improves query performance
- Easier to paginate

**Enforcing depth limit:**
```python
if parent and parent.parent:
    raise ValidationError("Cannot reply to a reply")
```

---

# Subscription & Payment Models Documentation

## Overview
This module implements a comprehensive subscription and payment system supporting multiple pricing tiers, payment gateways, promotional codes, and subscription lifecycle management. It handles recurring billing, grace periods, cancellations, and detailed transaction tracking with multi-currency support.

---

## SubscriptionPlan

### Purpose
Defines available subscription tiers with features, pricing, and access levels. Supports multiple currencies and flexible pricing models (monthly/annual). Serves as the blueprint for user subscriptions.

### Class Definition
```python
class SubscriptionPlan(models.Model)
```

### Fields

#### **Plan Information**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | CharField | max_length=100 | Display name (e.g., "Premium Plus") |
| `plan_type` | CharField | max_length=30, choices, unique | Internal identifier (BASIC, PREMIUM, ENTERPRISE) |

#### **Feature Flags**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_resolution` | CharField | "1440p" | Maximum video resolution (720p, 1080p, 1440p, 4K) |
| `ad_free` | BooleanField | True | Whether plan includes ad-free experience |
| `premium_content_access` | BooleanField | True | Access to premium/exclusive content |
| `early_access` | BooleanField | False | Early access to new features/content |

#### **Pricing (Stored in Cents)**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `price_monthly_cents` | IntegerField | min=0 | Monthly price in cents (e.g., 999 = $9.99) |
| `price_annual_cents` | IntegerField | min=0, nullable | Annual price in cents (optional) |
| `display_currency` | CharField | max_length=3, default="USD" | ISO 4217 currency code |

**Why store prices in cents?**
- Avoids floating-point precision errors
- Ensures accurate calculations
- Standard practice in payment systems

#### **Status Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_active` | BooleanField | True | Whether plan is available for new subscriptions |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Creation timestamp (auto) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |

### Configuration

**Meta Options:**
- **Database Table:** `subscription_plans`
- **Default Ordering:** `price_monthly_cents` (cheapest first)

### Methods

#### `__str__()`
**Returns:** `"{name} - {plan_type}"`

**Example Output:**
```
"Premium Plus - PREMIUM"
"Basic - BASIC"
```

### Usage Examples

#### Creating Subscription Plans
```python
# Basic Plan
basic_plan = SubscriptionPlan.objects.create(
    name="Basic",
    plan_type=SubscriptionPlanType.BASIC,
    max_resolution="720p",
    ad_free=False,
    premium_content_access=False,
    early_access=False,
    price_monthly_cents=499,  # $4.99
    price_annual_cents=4990,  # $49.90 (2 months free)
    display_currency="USD",
    is_active=True
)

# Premium Plan
premium_plan = SubscriptionPlan.objects.create(
    name="Premium",
    plan_type=SubscriptionPlanType.PREMIUM,
    max_resolution="1080p",
    ad_free=True,
    premium_content_access=True,
    early_access=False,
    price_monthly_cents=999,  # $9.99
    price_annual_cents=9990,  # $99.90
    display_currency="USD",
    is_active=True
)

# Premium Plus Plan
premium_plus = SubscriptionPlan.objects.create(
    name="Premium Plus",
    plan_type=SubscriptionPlanType.PREMIUM_PLUS,
    max_resolution="4K",
    ad_free=True,
    premium_content_access=True,
    early_access=True,
    price_monthly_cents=1499,  # $14.99
    price_annual_cents=14990,  # $149.90
    display_currency="USD",
    is_active=True
)
```

#### Displaying Prices
```python
def format_price(cents, currency="USD"):
    """Format price for display"""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{cents / 100:.2f}"

# Usage
monthly_price = format_price(plan.price_monthly_cents, plan.display_currency)
# Output: "$9.99"

if plan.price_annual_cents:
    annual_price = format_price(plan.price_annual_cents, plan.display_currency)
    monthly_equivalent = plan.price_annual_cents / 12
    savings = plan.price_monthly_cents * 12 - plan.price_annual_cents
    print(f"Annual: {annual_price} (Save {format_price(savings)})")
```

#### Querying Plans
```python
# Get active plans
active_plans = SubscriptionPlan.objects.filter(is_active=True)

# Get plans with specific features
ad_free_plans = SubscriptionPlan.objects.filter(
    is_active=True,
    ad_free=True
).order_by('price_monthly_cents')

# Get plan by type
premium_plan = SubscriptionPlan.objects.get(
    plan_type=SubscriptionPlanType.PREMIUM
)
```

#### Updating Plan Features
```python
# Add 4K support to Premium plan
premium_plan.max_resolution = "4K"
premium_plan.save()

# Deprecate old plan
old_plan.is_active = False
old_plan.save()
```

---

## UserSubscription

### Purpose
Manages individual user subscriptions including billing cycles, payment gateway integration, cancellation handling, and grace periods. Supports one active subscription per user with automatic renewal tracking.

### Class Definition
```python
class UserSubscription(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | OneToOneField | CASCADE, related_name='active_subscription' | Subscriber (one active subscription per user) |
| `plan` | ForeignKey | PROTECT, related_name='subscriptions' | Subscribed plan |

#### **Status & Billing**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | CharField | SubscriptionStatus.ACTIVE, choices | Current subscription status |
| `payment_gateway` | CharField | choices | Payment provider (STRIPE, PAYPAL, etc.) |
| `gateway_subscription_id` | CharField | max_length=255 | Gateway's subscription ID |
| `gateway_customer_id` | CharField | max_length=255 | Gateway's customer ID |

#### **Date Management**
| Field | Type | Description |
|-------|------|-------------|
| `start_date` | DateTimeField | Subscription start date (default: now) |
| `end_date` | DateTimeField | Subscription end date (nullable for active) |
| `renewal_date` | DateTimeField | Next billing date |

#### **Cancellation Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `cancelled_at` | DateTimeField | nullable | Cancellation timestamp |
| `cancel_at_period_end` | BooleanField | False | Whether to cancel at period end vs immediately |

#### **Grace Period**
| Field | Type | Description |
|-------|------|-------------|
| `grace_period_ends_at` | DateTimeField | Grace period expiration (for payment failures) |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Creation timestamp (auto) |
| `updated_at` | DateTimeField | Last update timestamp (auto) |

### Configuration

**Meta Options:**
- **Database Table:** `user_subscriptions`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(user, status)` - User subscription lookup
  - `(status, renewal_date)` - Renewal processing

### Properties

#### `is_active`
Determines if subscription provides active benefits.

**Returns:** bool

**Logic:**
- `ACTIVE` status → True
- `GRACE_PERIOD` status → True if within grace period
- Otherwise → False

**Example:**
```python
if user.active_subscription.is_active:
    # Grant premium features
    allow_hd_streaming()
else:
    # Restrict to free tier
    show_upgrade_prompt()
```

### Methods

#### `__str__()`
**Returns:** `"{username} - {plan_name}"`

### Usage Examples

#### Creating a Subscription
```python
from datetime import timedelta
from django.utils import timezone

def create_subscription(user, plan, payment_gateway, gateway_ids):
    """Create new subscription"""
    subscription = UserSubscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        payment_gateway=payment_gateway,
        gateway_subscription_id=gateway_ids['subscription_id'],
        gateway_customer_id=gateway_ids['customer_id'],
        start_date=timezone.now(),
        renewal_date=timezone.now() + timedelta(days=30)  # Monthly
    )
    return subscription
```

#### Handling Subscription Renewal
```python
from django.db import transaction

@transaction.atomic
def renew_subscription(subscription):
    """Process subscription renewal"""
    # Charge payment gateway
    payment_result = charge_payment_gateway(
        subscription.gateway_subscription_id,
        subscription.plan.price_monthly_cents
    )
    
    if payment_result['success']:
        # Record transaction
        PaymentTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            payment_gateway=subscription.payment_gateway,
            gateway_transaction_id=payment_result['transaction_id'],
            amount_cents=subscription.plan.price_monthly_cents,
            currency=subscription.plan.display_currency,
            status='completed',
            completed_at=timezone.now()
        )
        
        # Update renewal date
        subscription.renewal_date = timezone.now() + timedelta(days=30)
        subscription.save()
        
        return True
    else:
        # Enter grace period
        subscription.status = SubscriptionStatus.GRACE_PERIOD
        subscription.grace_period_ends_at = timezone.now() + timedelta(days=7)
        subscription.save()
        
        # Record failed transaction
        PaymentTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            payment_gateway=subscription.payment_gateway,
            gateway_transaction_id=payment_result['transaction_id'],
            amount_cents=subscription.plan.price_monthly_cents,
            currency=subscription.plan.display_currency,
            status='failed',
            failure_reason=payment_result['error']
        )
        
        return False
```

#### Cancelling a Subscription
```python
def cancel_subscription(subscription, immediate=False):
    """Cancel subscription"""
    subscription.cancelled_at = timezone.now()
    
    if immediate:
        # Cancel immediately
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.end_date = timezone.now()
        
        # Cancel at payment gateway
        cancel_gateway_subscription(subscription.gateway_subscription_id)
    else:
        # Cancel at period end
        subscription.cancel_at_period_end = True
        subscription.end_date = subscription.renewal_date
    
    subscription.save()
```

#### Upgrading/Downgrading Plan
```python
@transaction.atomic
def change_subscription_plan(subscription, new_plan):
    """Change subscription plan"""
    old_plan = subscription.plan
    
    # Calculate prorated amount
    days_remaining = (subscription.renewal_date - timezone.now()).days
    days_in_period = 30
    
    old_daily_rate = old_plan.price_monthly_cents / days_in_period
    new_daily_rate = new_plan.price_monthly_cents / days_in_period
    
    prorated_amount = int((new_daily_rate - old_daily_rate) * days_remaining)
    
    if prorated_amount > 0:
        # Charge difference for upgrade
        payment_result = charge_payment_gateway(
            subscription.gateway_subscription_id,
            prorated_amount
        )
        
        if not payment_result['success']:
            raise ValueError("Payment failed")
        
        # Record transaction
        PaymentTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            payment_gateway=subscription.payment_gateway,
            gateway_transaction_id=payment_result['transaction_id'],
            amount_cents=prorated_amount,
            currency=new_plan.display_currency,
            status='completed',
            completed_at=timezone.now()
        )
    
    # Update plan
    subscription.plan = new_plan
    subscription.save()
    
    # Update gateway subscription
    update_gateway_subscription(subscription.gateway_subscription_id, new_plan)
```

#### Processing Grace Period Expirations
```python
from django.utils import timezone

def process_expired_grace_periods():
    """Cancel subscriptions with expired grace periods"""
    expired_subscriptions = UserSubscription.objects.filter(
        status=SubscriptionStatus.GRACE_PERIOD,
        grace_period_ends_at__lte=timezone.now()
    )
    
    for subscription in expired_subscriptions:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.end_date = timezone.now()
        subscription.save()
        
        # Notify user
        send_subscription_cancelled_email(subscription.user)
```

#### Checking Subscription Features
```python
def user_has_feature(user, feature_name):
    """Check if user's subscription includes feature"""
    try:
        subscription = user.active_subscription
        if not subscription.is_active:
            return False
        
        plan = subscription.plan
        
        feature_map = {
            'ad_free': plan.ad_free,
            'premium_content': plan.premium_content_access,
            'early_access': plan.early_access,
            'hd_streaming': plan.max_resolution in ['1080p', '1440p', '4K'],
            '4k_streaming': plan.max_resolution == '4K'
        }
        
        return feature_map.get(feature_name, False)
    except UserSubscription.DoesNotExist:
        return False
```

---

## PaymentTransaction

### Purpose
Records all payment transactions for audit trails, reconciliation, and financial reporting. Supports multiple payment gateways, currencies, and transaction states including refunds.

### Class Definition
```python
class PaymentTransaction(models.Model)
```

### Fields

#### **Relationship Fields**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | ForeignKey | CASCADE, related_name='payment_transactions' | User who made payment |
| `subscription` | ForeignKey | SET_NULL, related_name='transactions', nullable | Associated subscription |

#### **Gateway Information**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `payment_gateway` | CharField | choices | Payment provider |
| `gateway_transaction_id` | CharField | max_length=255, unique | Gateway's transaction ID |

#### **Amount Details**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `amount_cents` | IntegerField | required | Transaction amount in cents |
| `currency` | CharField | "USD" | ISO 4217 currency code |

#### **Status & Metadata**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | CharField | "pending" | Transaction status (pending, completed, failed, refunded) |
| `payment_method` | CharField | optional | Payment method type (card, mobile_banking, etc.) |
| `failure_reason` | TextField | optional | Error message for failed transactions |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Transaction creation (auto, indexed) |
| `completed_at` | DateTimeField | Transaction completion timestamp (nullable) |

### Configuration

**Meta Options:**
- **Database Table:** `payment_transactions`
- **Default Ordering:** `-created_at` (newest first)
- **Indexes:**
  - `(user, status)` - User transaction history
  - `(gateway_transaction_id)` - Gateway lookup

### Methods

#### `__str__()`
**Returns:** `"{username} - {amount} {currency}"`

**Example Output:**
```
"johndoe - 9.99 USD"
```

### Usage Examples

#### Recording a Successful Payment
```python
from django.utils import timezone

transaction = PaymentTransaction.objects.create(
    user=user,
    subscription=subscription,
    payment_gateway=PaymentGateway.STRIPE,
    gateway_transaction_id='ch_1234567890',
    amount_cents=999,
    currency='USD',
    status='completed',
    payment_method='card',
    completed_at=timezone.now()
)
```

#### Recording a Failed Payment
```python
transaction = PaymentTransaction.objects.create(
    user=user,
    subscription=subscription,
    payment_gateway=PaymentGateway.STRIPE,
    gateway_transaction_id='ch_failed_123',
    amount_cents=999,
    currency='USD',
    status='failed',
    payment_method='card',
    failure_reason='Insufficient funds'
)
```

#### Processing a Refund
```python
@transaction.atomic
def process_refund(original_transaction, refund_amount_cents=None):
    """Process refund for a transaction"""
    if refund_amount_cents is None:
        refund_amount_cents = original_transaction.amount_cents
    
    # Process refund at gateway
    refund_result = process_gateway_refund(
        original_transaction.gateway_transaction_id,
        refund_amount_cents
    )
    
    if refund_result['success']:
        # Update original transaction
        original_transaction.status = 'refunded'
        original_transaction.save()
        
        # Create refund transaction record
        refund_transaction = PaymentTransaction.objects.create(
            user=original_transaction.user,
            subscription=original_transaction.subscription,
            payment_gateway=original_transaction.payment_gateway,
            gateway_transaction_id=refund_result['refund_id'],
            amount_cents=-refund_amount_cents,  # Negative amount
            currency=original_transaction.currency,
            status='completed',
            payment_method=original_transaction.payment_method,
            completed_at=timezone.now()
        )
        
        return refund_transaction
    else:
        raise ValueError(f"Refund failed: {refund_result['error']}")
```

#### Querying Transactions

**Get user's payment history:**
```python
transactions = PaymentTransaction.objects.filter(
    user=user,
    status='completed'
).order_by('-created_at')
```

**Calculate total revenue:**
```python
from django.db.models import Sum

total_revenue = PaymentTransaction.objects.filter(
    status='completed',
    amount_cents__gt=0  # Exclude refunds
).aggregate(
    total=Sum('amount_cents')
)['total'] or 0

print(f"Total Revenue: ${total_revenue / 100:.2f}")
```

**Get failed transactions for retry:**
```python
failed_transactions = PaymentTransaction.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timedelta(days=7)
).select_related('user', 'subscription')
```

**Monthly revenue report:**
```python
from django.db.models.functions import TruncMonth

monthly_revenue = PaymentTransaction.objects.filter(
    status='completed',
    amount_cents__gt=0
).annotate(
    month=TruncMonth('completed_at')
).values('month').annotate(
    revenue=Sum('amount_cents'),
    transaction_count=Count('id')
).order_by('-month')
```

---

## PromotionalCode

### Purpose
Manages discount codes for marketing campaigns, user acquisition, and retention. Supports percentage and fixed-amount discounts with flexible validity periods, usage limits, and plan restrictions.

### Class Definition
```python
class PromotionalCode(models.Model)
```

### Fields

#### **Code Information**
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | CharField | max_length=50, unique, indexed | Promotional code (e.g., "SUMMER2024") |

#### **Discount Configuration**
| Field | Type | Description |
|-------|------|-------------|
| `discount_type` | CharField | "percentage" or "fixed" |
| `discount_value` | IntegerField | Percentage (0-100) or amount in cents |

#### **Validity Period**
| Field | Type | Description |
|-------|------|-------------|
| `valid_from` | DateTimeField | Start of validity period |
| `valid_until` | DateTimeField | End of validity period |

#### **Usage Limits**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_uses` | IntegerField | nullable | Total usage limit (null = unlimited) |
| `max_uses_per_user` | IntegerField | 1 | Per-user usage limit |
| `current_uses` | IntegerField | 0 | Current usage count |

#### **Restrictions**
| Field | Type | Description |
|-------|------|-------------|
| `applicable_plans` | ManyToManyField | Plans this code applies to (empty = all plans) |

#### **Status Fields**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_active` | BooleanField | True | Whether code is active |

#### **Timestamp Fields**
| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Creation timestamp (auto) |

### Configuration

**Meta Options:**
- **Database Table:** `promotional_codes`
- **Default Ordering:** `-created_at` (newest first)

### Properties

#### `is_valid`
Checks if promotional code is currently valid.

**Returns:** bool

**Validation Logic:**
1. `is_active` must be True
2. Current time must be within `valid_from` and `valid_until`
3. If `max_uses` set, `current_uses` must be less than `max_uses`

### Methods

#### `__str__()`
**Returns:** `code`

### Usage Examples

#### Creating Promotional Codes

**Percentage discount:**
```python
from datetime import timedelta
from django.utils import timezone

summer_sale = PromotionalCode.objects.create(
    code="SUMMER2024",
    discount_type="percentage",
    discount_value=25,  # 25% off
    valid_from=timezone.now(),
    valid_until=timezone.now() + timedelta(days=30),
    max_uses=1000,
    max_uses_per_user=1,
    is_active=True
)

# Apply to specific plans
summer_sale.applicable_plans.add(premium_plan, premium_plus_plan)
```

**Fixed amount discount:**
```python
welcome_code = PromotionalCode.objects.create(
    code="WELCOME10",
    discount_type="fixed",
    discount_value=1000,  # $10 off
    valid_from=timezone.now(),
    valid_until=timezone.now() + timedelta(days=365),
    max_uses=None,  # Unlimited
    max_uses_per_user=1,
    is_active=True
)
```

**Influencer code:**
```python
influencer_code = PromotionalCode.objects.create(
    code="TECHGURU50",
    discount_type="percentage",
    discount_value=50,  # 50% off
    valid_from=timezone.now(),
    valid_until=timezone.now() + timedelta(days=90),
    max_uses=500,
    max_uses_per_user=1,
    is_active=True
)
```

#### Validating and Applying Promo Codes
```python
def validate_promo_code(code, user, plan):
    """Validate promotional code"""
    try:
        promo = PromotionalCode.objects.get(code=code.upper())
    except PromotionalCode.DoesNotExist:
        return {'valid': False, 'error': 'Invalid code'}
    
    # Check if code is valid
    if not promo.is_valid:
        return {'valid': False, 'error': 'Code expired or inactive'}
    
    # Check plan applicability
    if promo.applicable_plans.exists() and plan not in promo.applicable_plans.all():
        return {'valid': False, 'error': 'Code not applicable to this plan'}
    
    # Check per-user limit
    user_usage_count = PromoCodeUsage.objects.filter(
        promo_code=promo,
        user=user
    ).count()
    
    if user_usage_count >= promo.max_uses_per_user:
        return {'valid': False, 'error': 'Code already used'}
    
    # Calculate discount
    if promo.discount_type == 'percentage':
        discount = int(plan.price_monthly_cents * promo.discount_value / 100)
    else:
        discount = min(promo.discount_value, plan.price_monthly_cents)
    
    return {
        'valid': True,
        'promo': promo,
        'discount_cents': discount,
        'final_price_cents': plan.price_monthly_cents - discount
    }
```

#### Applying Promo Code to Transaction
```python
@transaction.atomic
def apply_promo_code(promo, user, plan, transaction):
    """Apply promo code and record usage"""
    # Calculate discount
    if promo.discount_type == 'percentage':
        discount = int(plan.price_monthly_cents * promo.discount_value / 100)
    else:
        discount = min(promo.discount_value, plan.price_monthly_cents)
    
    # Record usage
    usage = PromoCodeUsage.objects.create(
        promo_code=promo,
        user=user,
        transaction=transaction,
        discount_applied_cents=discount
    )
    
    # Increment usage count
    promo.current_uses = models.F('current_uses') + 1
    promo.save()
    promo.refresh_from_db()
    
    return discount
```

#### Managing Promo Codes

**Deactivate expired codes:**
```python
from django.utils import timezone

expired_codes = PromotionalCode.objects.filter(
    is_active=True,
    valid_until__lt=timezone.now()
)
expired_codes.update(is_active=False)
```

**Get code statistics:**
```python
def get_promo_code_stats(promo_code):
    """Get usage statistics for promo code"""
    usages = PromoCodeUsage.objects.filter(promo_code=promo_code)
    
    stats = {
        'total_uses': usages.count(),
        'unique_users': usages.values('user').distinct().count(),
        'total_discount_given': usages.aggregate(
            total=Sum('discount_applied_cents')
        )['total'] or 0,
        'revenue_generated': PaymentTransaction.objects.filter(
            id__in=usages.values_list('transaction_id', flat=True),
            status='completed'
        ).aggregate(
            total=Sum('amount_cents')
        )['total'] or 0
    }
    
    return stats
```

---

## PromoCodeUsage

### Purpose
Tracks individual uses of promotional codes for analytics, fraud prevention, and enforcing usage limits. Maintains audit trail of discounts applied.

### Class Definition
```python
class PromoCodeUsage(models.Model)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `promo_code` | ForeignKey | CASCADE, related_name='usages' | Promotional code used |
| `user` | ForeignKey | CASCADE, related_name='promo_code_usages' | User who used code |
| `transaction` | ForeignKey | SET_NULL, nullable | Associated payment transaction |
| `discount_applied_cents` | IntegerField | required | Actual discount amount applied |
| `used_at` | DateTimeField | auto | Usage timestamp |

### Configuration

**Meta Options:**
- **Database Table:** `promo_code_usages`
- **Default Ordering:** `-used_at` (newest first)
- **Indexes:**
  - `(promo_code, user)` - User usage lookup

### Methods

#### `__str__()`
**Returns:** `"{username} used {code}"`

### Usage Examples

#### Recording Promo Code Usage
```python
usage = PromoCodeUsage.objects.create(
    promo_code=promo,
    user=user,
    transaction=transaction,
    discount_applied_cents=discount_amount
)
```

#### Checking User's Usage History
```python
user_promo_history = PromoCodeUsage.objects.filter(
    user=user
).select_related('promo_code', 'transaction').order_by('-used_at')
```

#### Analytics Queries

**Most popular promo codes:**
```python
from django.db.models import Count

popular_codes = PromotionalCode.objects.annotate(
    usage_count=Count('usages')
).filter(
    usage_count__gt=0
).order_by('-usage_count')[:10]
```

**Total discounts given:**
```python
total_discounts = PromoCodeUsage.objects.aggregate(
    total=Sum('discount_applied_cents')
)['total'] or 0

print(f"Total Discounts: ${total_discounts / 100:.2f}")
```

**Promo code conversion rate:**
```python
def get_promo_conversion_rate(promo_code):
    """Calculate conversion rate for promo code"""
    usages = PromoCodeUsage.objects.filter(promo_code=promo_code)
    
    successful_conversions = usages.filter(
        transaction__status='completed'
    ).count()
    
    total_attempts = usages.count()
    
    if total_attempts == 0:
        return 0
    
    return (successful_conversions / total_attempts) * 100
```

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from .choices import SubscriptionPlanType, SubscriptionStatus, PaymentGateway
```

### External Choice Classes
The following choice classes must be defined in `choices.py`:

#### **SubscriptionPlanType**
```python
class SubscriptionPlanType(models.TextChoices):
    BASIC = 'basic', 'Basic'
    PREMIUM = 'premium', 'Premium'
    PREMIUM_PLUS = 'premium_plus', 'Premium Plus'
    ENTERPRISE = 'enterprise', 'Enterprise'
```

#### **SubscriptionStatus**
```python
class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'
    GRACE_PERIOD = 'grace_period', 'Grace Period'
    PENDING = 'pending', 'Pending'
    SUSPENDED = 'suspended', 'Suspended'
```

#### **PaymentGateway**
```python
class PaymentGateway(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    PAYPAL = 'paypal', 'PayPal'
    RAZORPAY = 'razorpay', 'Razorpay'
    PADDLE = 'paddle', 'Paddle'
    BRAINTREE = 'braintree', 'Braintree'
```

### Related Models
- **User**: From authentication models (django.contrib.auth or custom user model)

---

# Moderation & Flagging Models Documentation

---

## Overview
This module provides a comprehensive content moderation system with flagging capabilities, moderation logging, and user suspension management. It uses Django's ContentTypes framework to enable flagging and moderation of any content type (videos, comments, users, etc.).

---

## Models

### 1. Flag

**Purpose:** Allows users to report inappropriate or problematic content across the platform. Supports flagging any model type through generic relations.

**Table Name:** `flags`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `content_type` | ForeignKey | NOT NULL, CASCADE | References ContentType - identifies the model type being flagged |
| `object_id` | PositiveIntegerField | NOT NULL | ID of the specific object being flagged |
| `content_object` | GenericForeignKey | - | Virtual field providing direct access to the flagged object |
| `user` | ForeignKey(User) | NULL, SET_NULL | User who created the flag (null if user deleted) |
| `reason` | CharField(30) | NOT NULL, Choices | Predefined reason category for the flag |
| `reason_detail` | TextField(1000) | Optional | Additional context or explanation for the flag |
| `status` | CharField(20) | NOT NULL, Default: PENDING | Current review status of the flag |
| `reviewed_by` | ForeignKey(User) | NULL, Optional | Moderator who reviewed this flag |
| `reviewed_at` | DateTimeField | NULL, Optional | Timestamp when flag was reviewed |
| `review_notes` | TextField | Optional | Moderator's notes from review process |
| `created_at` | DateTimeField | Auto, Indexed | Timestamp when flag was created |

#### Relationships
- **User (flagger):** Many-to-One via `user` field
  - Related name: `flags_created`
  - Allows tracking all flags created by a user
  
- **User (reviewer):** Many-to-One via `reviewed_by` field
  - Related name: `flags_reviewed`
  - Allows tracking moderator workload and history

- **Content Object:** Generic relation to any model
  - Enables flagging videos, comments, users, or any other content type
  - Accessed via `content_object` property

#### Indexes
- Composite index on `(content_type, object_id)` - Fast lookup of flags for specific content
- Composite index on `(status, created_at)` - Efficient querying of pending flags
- Single index on `user` - Quick access to user's flag history

#### Meta Options
- **Ordering:** `["-created_at"]` - Newest flags first
- **DB Table:** `flags`

---

### 2. ModerationLog

**Purpose:** Maintains an audit trail of all moderation actions taken on the platform. Provides accountability and enables review of moderator decisions.

**Table Name:** `moderation_logs`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `moderator` | ForeignKey(User) | NULL, SET_NULL | User who performed the moderation action |
| `content_type` | ForeignKey | NOT NULL, CASCADE | Type of content being moderated |
| `object_id` | PositiveIntegerField | NOT NULL | ID of the moderated object |
| `content_object` | GenericForeignKey | - | Direct access to the moderated content |
| `action` | CharField(30) | NOT NULL, Choices | Type of moderation action taken |
| `reason` | TextField(2000) | NOT NULL | Explanation for the moderation action |
| `related_flag` | ForeignKey(Flag) | NULL, Optional | Flag that triggered this action (if applicable) |
| `duration_days` | IntegerField | NULL, Optional | Duration for temporary actions (suspensions, bans) |
| `expires_at` | DateTimeField | NULL, Optional | When temporary action expires |
| `created_at` | DateTimeField | Auto, Indexed | Timestamp of the moderation action |

#### Relationships
- **Moderator:** Many-to-One via `moderator` field
  - Related name: `moderation_actions`
  - Tracks all actions performed by each moderator
  
- **Content Object:** Generic relation to any model
  - Records what content was moderated
  - Supports videos, comments, users, etc.

- **Related Flag:** Many-to-One via `related_flag` field
  - Related name: `actions`
  - Links moderation actions back to user reports
  - Optional - actions can be taken proactively without flags

#### Indexes
- Composite index on `(moderator, created_at)` - Moderator activity tracking
- Composite index on `(content_type, object_id)` - Content moderation history
- Composite index on `(action, created_at)` - Action type analytics

#### Meta Options
- **Ordering:** `["-created_at"]` - Most recent actions first
- **DB Table:** `moderation_logs`

---

### 3. UserSuspension

**Purpose:** Manages temporary and permanent user account suspensions. Tracks suspension history and enables automated expiration.

**Table Name:** `user_suspensions`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `user` | ForeignKey(User) | NOT NULL, CASCADE | User being suspended |
| `reason` | TextField(2000) | NOT NULL | Detailed explanation for suspension |
| `suspended_by` | ForeignKey(User) | NULL, SET_NULL | Moderator who issued the suspension |
| `is_permanent` | BooleanField | Default: False | Whether suspension is permanent |
| `suspended_at` | DateTimeField | Auto | Timestamp when suspension began |
| `expires_at` | DateTimeField | NULL, Optional | When temporary suspension ends |
| `lifted_at` | DateTimeField | NULL, Optional | When suspension was manually lifted |
| `lifted_by` | ForeignKey(User) | NULL, Optional | Moderator who lifted the suspension |

#### Relationships
- **User (suspended):** Many-to-One via `user` field
  - Related name: `suspensions`
  - CASCADE delete - removes suspension records when user deleted
  - Allows viewing user's suspension history

- **Suspended By:** Many-to-One via `suspended_by` field
  - Related name: `suspensions_issued`
  - Tracks which moderator issued each suspension

- **Lifted By:** Many-to-One via `lifted_by` field
  - Related name: `suspensions_lifted`
  - Records who ended the suspension early

#### Properties

**`is_active`** (property)
- **Returns:** Boolean
- **Purpose:** Determines if suspension is currently in effect
- **Logic:**
  - Returns `False` if suspension was lifted (`lifted_at` is set)
  - Returns `True` if permanent suspension
  - Returns `True/False` based on `expires_at` comparison for temporary suspensions
  - Returns `True` if no expiration set

#### Indexes
- Composite index on `(user, suspended_at)` - User suspension history lookup

#### Meta Options
- **Ordering:** `["-suspended_at"]` - Most recent suspensions first
- **DB Table:** `user_suspensions`

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .choices import FlagReason, FlagStatus, ModerationAction
```

### External Choice Classes
The following choice classes must be defined in `choices.py`:

#### **FlagReason**
Defines categories for content flags:
- Spam
- Harassment
- Inappropriate content
- Copyright violation
- Misinformation
- Other violations

#### **FlagStatus**
Tracks flag review state:
- `PENDING` - Awaiting moderator review
- `REVIEWED` - Reviewed but no action taken
- `ACTIONED` - Action taken on flagged content
- `DISMISSED` - Flag rejected as invalid

#### **ModerationAction**
Types of moderation actions:
- Content removal
- Content warning
- User warning
- Temporary suspension
- Permanent ban
- Content restoration
- Other actions

### Related Models
- **User:** From authentication models
  - Referenced by: `Flag.user`, `Flag.reviewed_by`, `ModerationLog.moderator`, `UserSuspension.user`, `UserSuspension.suspended_by`, `UserSuspension.lifted_by`
  - Multiple relationships tracking flaggers, moderators, and suspended users

- **ContentType:** Django's contenttypes framework
  - Enables generic relations to any model
  - Used by: `Flag`, `ModerationLog`

---

## Model Relationships

### Entity Relationship Overview

```
User (Flagger) ──┐
                 ├──→ Flag ──→ ContentType + object_id (Generic)
User (Reviewer) ─┘       │
                         │
                         ↓
                    ModerationLog ──→ ContentType + object_id (Generic)
                         ↑
                         │
User (Moderator) ────────┘

User (Suspended) ──→ UserSuspension ←── User (Suspended By)
                           ↑
                           │
                    User (Lifted By)
```

### Relationship Details

#### **Flag Relationships**
- **User → Flag (flagger):** One user creates many flags
- **User → Flag (reviewer):** One moderator reviews many flags
- **Flag → Any Content:** Generic relation to videos, comments, users, etc.

#### **ModerationLog Relationships**
- **User → ModerationLog:** One moderator performs many actions
- **Flag → ModerationLog:** One flag can trigger multiple actions
- **ModerationLog → Any Content:** Generic relation to moderated content

#### **UserSuspension Relationships**
- **User → UserSuspension (suspended):** One user can have multiple suspensions
- **User → UserSuspension (issuer):** One moderator issues many suspensions
- **User → UserSuspension (lifter):** One moderator lifts many suspensions

---

## Use Cases

### Flag Model
- User reports inappropriate video content
- Community members flag spam comments
- Users report harassment or abuse
- Automated systems flag potential violations
- Moderators review and process flags

### ModerationLog Model
- Audit trail for all moderation decisions
- Moderator performance tracking
- Appeal review and verification
- Compliance and legal documentation
- Platform safety analytics

### UserSuspension Model
- Temporary account suspensions (1-30 days)
- Permanent account bans
- Suspension appeal management
- Automated suspension expiration
- Repeat offender tracking

---

## Key Features

### Generic Content Flagging
- Flag any content type using ContentTypes framework
- Flexible reason categories with detailed explanations
- Multi-stage review workflow (pending → reviewed → actioned)

### Comprehensive Audit Trail
- Every moderation action logged permanently
- Links actions to triggering flags
- Tracks moderator identity and reasoning
- Supports temporary actions with expiration

### Flexible Suspension System
- Both temporary and permanent suspensions
- Automatic expiration handling via `is_active` property
- Manual suspension lifting capability
- Complete suspension history per user

### Performance Optimization
- Strategic indexes for common queries
- Efficient flag status filtering
- Fast moderator activity lookups
- Optimized content moderation history access

---

# Analytics & Caching Models Documentation

---

## Overview
This module provides comprehensive analytics tracking, caching mechanisms, and data aggregation for a video platform. It includes trending video calculations, personalized recommendations, search analytics, channel/video performance metrics, and user watch history tracking.

---

## Models

### 1. TrendingVideo

**Purpose:** Caches trending videos based on calculated scores, supporting regional and category-specific trending lists.

**Table Name:** `trending_videos`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `video` | ForeignKey(Video) | NOT NULL, CASCADE | Reference to the trending video |
| `rank` | IntegerField | NOT NULL | Position in trending list (1 = top) |
| `score` | FloatField | NOT NULL | Calculated trending score based on views, velocity, engagement |
| `category` | CharField(50) | Optional | Category-specific trending (e.g., "Gaming", "Music") |
| `region` | CharField(2) | Default: "BD" | ISO country code for regional trending |
| `date` | DateField | Indexed | Snapshot date for this trending entry |
| `created_at` | DateTimeField | Auto | Timestamp when entry was created |

#### Relationships
- **Video:** Many-to-One via `video` field
  - Related name: `trending_entries`
  - CASCADE delete - removes trending entries when video deleted
  - One video can appear in multiple trending lists (different dates/regions)

#### Constraints
- **Unique Together:** `[video, date, region]`
  - Prevents duplicate entries for same video on same date in same region
  - Allows same video to trend in different regions simultaneously

#### Indexes
- Single index on `date` - Fast filtering by date
- Composite index on `(date, region, rank)` - Optimized trending list retrieval

#### Meta Options
- **Ordering:** `["date", "rank"]` - Chronological, then by rank
- **DB Table:** `trending_videos`

---

### 2. RecommendationCache

**Purpose:** Stores pre-calculated personalized video recommendations per user to reduce computation overhead.

**Table Name:** `recommendation_caches`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `user` | ForeignKey(User) | NOT NULL, CASCADE | User receiving recommendations |
| `video_ids` | JSONField | Default: [] | List of recommended video IDs (max 50) |
| `context` | CharField(50) | Default: "home" | Recommendation context (home, watch_next, subscriptions) |
| `algorithm_version` | CharField(20) | Default: "v1" | Version of recommendation algorithm used |
| `score_threshold` | FloatField | Default: 0.0 | Minimum score threshold for recommendations |
| `expires_at` | DateTimeField | Indexed | Cache expiration timestamp |
| `created_at` | DateTimeField | Auto | When cache was created |
| `updated_at` | DateTimeField | Auto | Last cache update timestamp |

#### Relationships
- **User:** Many-to-One via `user` field
  - Related name: `recommendation_caches`
  - CASCADE delete - removes cache when user deleted
  - One user can have multiple caches for different contexts

#### Constraints
- **Unique Together:** `[user, context]`
  - One cache per user per context
  - Ensures cache consistency

#### Indexes
- Composite index on `(user, context)` - Fast cache lookup
- Single index on `expires_at` - Efficient cleanup of expired caches

#### Methods

**`get_video_ids()`**
- **Returns:** List of integers
- **Purpose:** Safely retrieves video IDs as a list
- **Logic:** Returns `video_ids` if it's a list, otherwise returns empty list

**`set_video_ids(video_ids)`**
- **Parameters:** `video_ids` (iterable)
- **Purpose:** Sets video IDs with automatic limit enforcement
- **Logic:** Converts to list and limits to 50 items

#### Meta Options
- **Ordering:** `["-updated_at"]` - Most recently updated first
- **DB Table:** `recommendation_caches`

---

### 3. SearchQuery

**Purpose:** Tracks individual search queries for analytics, autocomplete improvement, and user behavior analysis.

**Table Name:** `search_queries`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `user` | ForeignKey(User) | NULL, SET_NULL | User who performed the search (optional) |
| `query` | CharField(255) | Indexed | Original search query as entered |
| `normalized_query` | CharField(255) | Indexed | Lowercase, trimmed version for grouping |
| `result_count` | IntegerField | Default: 0 | Number of results returned |
| `clicked_video` | ForeignKey(Video) | NULL, SET_NULL | Video clicked from results (if any) |
| `click_position` | IntegerField | NULL, Optional | Position of clicked video in results (1-indexed) |
| `session_id` | CharField(100) | Optional | Session identifier for anonymous tracking |
| `ip_address` | GenericIPAddressField | NULL, Optional | IP address for analytics (IPv4/IPv6) |
| `created_at` | DateTimeField | Auto, Indexed | Timestamp when search was performed |

#### Relationships
- **User:** Many-to-One via `user` field
  - Related name: `search_queries`
  - SET_NULL on delete - preserves search data for analytics
  - Optional - supports anonymous searches

- **Clicked Video:** Many-to-One via `clicked_video` field
  - Related name: `search_clicks`
  - SET_NULL on delete - preserves click data
  - Tracks search effectiveness

#### Indexes
- Single index on `query` - Fast query lookup
- Single index on `normalized_query` - Efficient grouping
- Composite index on `(normalized_query, created_at)` - Trending searches
- Composite index on `(user, created_at)` - User search history

#### Methods

**`save(*args, **kwargs)`** (Override)
- **Purpose:** Auto-generates normalized query on save
- **Logic:** 
  - If `normalized_query` not set, creates it from `query`
  - Converts to lowercase and strips whitespace
  - Calls parent save method

#### Meta Options
- **Ordering:** `["-created_at"]` - Most recent searches first
- **DB Table:** `search_queries`

---

### 4. PopularSearch

**Purpose:** Aggregates search data to provide popular/trending searches for autocomplete and discovery features.

**Table Name:** `popular_searches`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `query` | CharField(255) | Unique, Indexed | Normalized search query |
| `search_count` | IntegerField | Default: 0 | Total number of times searched (all-time) |
| `click_through_rate` | FloatField | Default: 0.0 | Percentage of searches resulting in clicks |
| `daily_count` | IntegerField | Default: 0 | Searches in last 24 hours |
| `weekly_count` | IntegerField | Default: 0 | Searches in last 7 days |
| `monthly_count` | IntegerField | Default: 0 | Searches in last 30 days |
| `last_searched_at` | DateTimeField | Auto | Most recent search timestamp |

#### Constraints
- **Unique:** `query` field
  - One entry per unique search term
  - Prevents duplicates

#### Indexes
- Descending index on `search_count` - Fast popular queries retrieval
- Single index on `query` - Quick query lookup

#### Meta Options
- **Ordering:** `["-search_count"]` - Most popular first
- **DB Table:** `popular_searches`

---

### 5. ChannelAnalytics

**Purpose:** Daily aggregated analytics for channels, providing comprehensive performance metrics and insights.

**Table Name:** `channel_analytics`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `channel` | ForeignKey(Channel) | NOT NULL, CASCADE | Channel being analyzed |
| `date` | DateField | Indexed | Date of analytics snapshot |
| `total_views` | IntegerField | Default: 0 | Total video views for the day |
| `unique_viewers` | IntegerField | Default: 0 | Unique users who viewed content |
| `total_watch_time_seconds` | BigIntegerField | Default: 0 | Total watch time across all videos |
| `average_view_duration_seconds` | IntegerField | Default: 0 | Average time per view |
| `likes` | IntegerField | Default: 0 | Total likes received |
| `dislikes` | IntegerField | Default: 0 | Total dislikes received |
| `comments` | IntegerField | Default: 0 | Total comments posted |
| `shares` | IntegerField | Default: 0 | Total shares/forwards |
| `new_subscribers` | IntegerField | Default: 0 | New subscriptions gained |
| `unsubscribers` | IntegerField | Default: 0 | Subscriptions lost |
| `net_subscriber_change` | IntegerField | Default: 0 | Net change (new - lost) |
| `estimated_revenue_cents` | IntegerField | Default: 0 | Estimated revenue in cents |
| `traffic_source_data` | JSONField | Default: {} | Breakdown of traffic sources (search, suggested, etc.) |
| `created_at` | DateTimeField | Auto | When analytics record was created |

#### Relationships
- **Channel:** Many-to-One via `channel` field
  - Related name: `analytics`
  - CASCADE delete - removes analytics when channel deleted
  - One channel has multiple daily analytics records

#### Constraints
- **Unique Together:** `[channel, date]`
  - One analytics record per channel per day
  - Prevents duplicate daily snapshots

#### Indexes
- Composite index on `(channel, date)` - Efficient time-series queries

#### Properties

**`estimated_revenue`** (property)
- **Returns:** Float
- **Purpose:** Converts revenue from cents to dollars
- **Calculation:** `estimated_revenue_cents / 100`

**`average_watch_time_minutes`** (property)
- **Returns:** Float
- **Purpose:** Converts watch time to minutes
- **Calculation:** `average_view_duration_seconds / 60`

#### Meta Options
- **Ordering:** `["-date"]` - Most recent first
- **DB Table:** `channel_analytics`

---

### 6. VideoAnalytics

**Purpose:** Daily aggregated analytics for individual videos, tracking performance, engagement, and audience behavior.

**Table Name:** `video_analytics`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `video` | ForeignKey(Video) | NOT NULL, CASCADE | Video being analyzed |
| `date` | DateField | Indexed | Date of analytics snapshot |
| `views` | IntegerField | Default: 0 | Total views for the day |
| `unique_viewers` | IntegerField | Default: 0 | Unique users who viewed |
| `watch_time_seconds` | BigIntegerField | Default: 0 | Total watch time |
| `average_view_duration_seconds` | IntegerField | Default: 0 | Average time per view |
| `average_percentage_viewed` | FloatField | Default: 0.0 | Average % of video watched |
| `likes` | IntegerField | Default: 0 | Likes received |
| `dislikes` | IntegerField | Default: 0 | Dislikes received |
| `comments` | IntegerField | Default: 0 | Comments posted |
| `shares` | IntegerField | Default: 0 | Shares/forwards |
| `retention_curve` | JSONField | Default: [] | Audience retention at 5% intervals (list of floats) |
| `demographics_data` | JSONField | Default: {} | Age, gender, location breakdown |
| `traffic_sources` | JSONField | Default: {} | Where viewers came from |
| `estimated_revenue_cents` | IntegerField | Default: 0 | Estimated revenue in cents |
| `created_at` | DateTimeField | Auto | When analytics record was created |

#### Relationships
- **Video:** Many-to-One via `video` field
  - Related name: `analytics`
  - CASCADE delete - removes analytics when video deleted
  - One video has multiple daily analytics records

#### Constraints
- **Unique Together:** `[video, date]`
  - One analytics record per video per day
  - Prevents duplicate daily snapshots

#### Indexes
- Composite index on `(video, date)` - Efficient time-series queries

#### Properties

**`estimated_revenue`** (property)
- **Returns:** Float
- **Purpose:** Converts revenue from cents to dollars
- **Calculation:** `estimated_revenue_cents / 100`

**`engagement_rate`** (property)
- **Returns:** Float
- **Purpose:** Calculates overall engagement percentage
- **Calculation:** `(likes + dislikes + comments + shares) / views * 100`
- **Edge Case:** Returns 0.0 if views is 0

**`watch_time_hours`** (property)
- **Returns:** Float
- **Purpose:** Converts watch time to hours
- **Calculation:** `watch_time_seconds / 3600`

#### Meta Options
- **Ordering:** `["-date"]` - Most recent first
- **DB Table:** `video_analytics`

---

### 7. UserWatchHistory

**Purpose:** Tracks user viewing behavior for recommendations, resume playback, and personalization.

**Table Name:** `user_watch_history`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `user` | ForeignKey(User) | NOT NULL, CASCADE | User who watched the video |
| `video` | ForeignKey(Video) | NOT NULL, CASCADE | Video that was watched |
| `watch_percentage` | FloatField | Default: 0.0 | Percentage of video watched (0-100) |
| `watch_duration_seconds` | IntegerField | Default: 0 | Total time spent watching |
| `completed` | BooleanField | Default: False | Whether video was completed (>90%) |
| `last_position_seconds` | IntegerField | Default: 0 | Last playback position for resume |
| `watched_at` | DateTimeField | Auto, Indexed | When video was first watched |
| `updated_at` | DateTimeField | Auto | Last update timestamp |

#### Relationships
- **User:** Many-to-One via `user` field
  - Related name: `watch_history`
  - CASCADE delete - removes history when user deleted
  - One user has many watch history entries

- **Video:** Many-to-One via `video` field
  - Related name: `watch_history_entries`
  - CASCADE delete - removes history when video deleted
  - One video has many watch history entries

#### Constraints
- **Unique Together:** `[user, video]`
  - One watch history entry per user per video
  - Updates existing entry on re-watch

#### Indexes
- Composite index on `(user, -watched_at)` - User's watch history (descending)
- Composite index on `(video, watched_at)` - Video's viewer history

#### Methods

**`mark_completed()`**
- **Purpose:** Automatically marks video as completed if watch percentage ≥ 90%
- **Logic:** 
  - Checks if `watch_percentage >= 90.0`
  - Sets `completed = True`
  - Saves only the `completed` field

#### Properties

**`watch_duration_minutes`** (property)
- **Returns:** Float
- **Purpose:** Converts watch duration to minutes
- **Calculation:** `watch_duration_seconds / 60`

#### Meta Options
- **Ordering:** `["-watched_at"]` - Most recent first
- **DB Table:** `user_watch_history`

---

## Dependencies

### Required Imports
```python
from django.db import models
```

### Related Models
- **Video:** Core video model
  - Referenced by: `TrendingVideo`, `RecommendationCache` (via JSON), `SearchQuery`, `VideoAnalytics`, `UserWatchHistory`
  
- **User:** Authentication/user model
  - Referenced by: `RecommendationCache`, `SearchQuery`, `ChannelAnalytics` (via Channel), `UserWatchHistory`
  
- **Channel:** Channel/creator model
  - Referenced by: `ChannelAnalytics`

---

## Model Relationships

### Entity Relationship Overview

```
User ──┬──→ RecommendationCache
       ├──→ SearchQuery
       ├──→ UserWatchHistory ──→ Video
       └──→ Channel ──→ ChannelAnalytics

Video ──┬──→ TrendingVideo
        ├──→ VideoAnalytics
        ├──→ UserWatchHistory
        └──→ SearchQuery (clicked_video)

SearchQuery ──→ PopularSearch (aggregated)
```

### Relationship Details

#### **Caching & Recommendations**
- **User → RecommendationCache:** One user has multiple caches (different contexts)
- **Video → TrendingVideo:** One video can appear in multiple trending lists

#### **Search Analytics**
- **User → SearchQuery:** One user performs many searches
- **Video → SearchQuery:** One video receives many search clicks
- **SearchQuery → PopularSearch:** Many queries aggregated into popular searches

#### **Performance Analytics**
- **Channel → ChannelAnalytics:** One channel has daily analytics records
- **Video → VideoAnalytics:** One video has daily analytics records

#### **User Behavior**
- **User → UserWatchHistory:** One user has many watch history entries
- **Video → UserWatchHistory:** One video has many watch history entries

---

# Creator Monetization Models Documentation

---

## Overview
This module manages creator monetization, revenue tracking, and payout processing for a video platform. It handles revenue attribution, payout calculations with fees and taxes, multiple payment methods, and comprehensive payout status tracking.

---

## Models

### 1. CreatorPayout

**Purpose:** Manages periodic revenue payouts to content creators, tracking revenue breakdown, fees, payment status, and processing lifecycle.

**Table Name:** `creator_payouts`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `channel` | ForeignKey(Channel) | NOT NULL, CASCADE | Channel receiving the payout |
| `period_start` | DateField | NOT NULL | Start date of payout period |
| `period_end` | DateField | NOT NULL | End date of payout period |
| `ad_revenue_cents` | IntegerField | Default: 0 | Revenue from advertisements (in cents) |
| `premium_revenue_cents` | IntegerField | Default: 0 | Revenue from premium subscriptions (in cents) |
| `total_revenue_cents` | IntegerField | Default: 0 | Total gross revenue (in cents) |
| `platform_fee_cents` | IntegerField | Default: 0 | Platform commission fee (in cents) |
| `payment_gateway_fee_cents` | IntegerField | Default: 0 | Payment processing fee (in cents) |
| `tax_withheld_cents` | IntegerField | Default: 0 | Tax withholding amount (in cents) |
| `net_payout_cents` | IntegerField | Default: 0 | Final payout amount after deductions (in cents) |
| `currency` | CharField(3) | Default: "USD" | ISO 4217 currency code |
| `status` | CharField(20) | Choices, Default: PENDING | Current payout status (from PayoutStatus) |
| `payment_method` | CharField(100) | Optional | Payment method used for payout |
| `payment_reference` | CharField(255) | Optional | External payment reference/transaction ID |
| `created_at` | DateTimeField | Auto | When payout record was created |
| `processed_at` | DateTimeField | NULL, Optional | When payout processing started |
| `completed_at` | DateTimeField | NULL, Optional | When payout was successfully completed |
| `notes` | TextField | Optional | Additional notes or comments |
| `failure_reason` | TextField | Optional | Reason for payout failure (if applicable) |

#### Relationships
- **Channel:** Many-to-One via `channel` field
  - Related name: `payouts`
  - CASCADE delete - removes payouts when channel deleted
  - One channel has multiple payout records (one per period)

#### Constraints
- **Unique Together:** `[channel, period_start, period_end]`
  - One payout per channel per period
  - Prevents duplicate payout records for same time period

#### Indexes
- Composite index on `(channel, status)` - Channel-specific payout filtering
- Composite index on `(status, created_at)` - Status-based payout queries

#### Properties

**`payout_amount_display`** (property)
- **Returns:** String
- **Purpose:** Formats net payout amount with currency for display
- **Format:** `"{currency} {amount:.2f}"` (e.g., "USD 1234.56")
- **Calculation:** `net_payout_cents / 100` with 2 decimal places

#### Meta Options
- **Ordering:** `["-period_end", "-created_at"]` - Most recent period first, then by creation
- **DB Table:** `creator_payouts`

#### PayoutStatus Choices
Referenced from `choices.PayoutStatus`:
- `PENDING` - Awaiting processing
- `PROCESSING` - Currently being processed
- `COMPLETED` - Successfully paid out
- `FAILED` - Payment failed
- `CANCELLED` - Payout cancelled

---

### 2. RevenueShare

**Purpose:** Tracks daily revenue attribution per video, calculating creator earnings based on configurable revenue share percentages.

**Table Name:** `revenue_shares`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `video` | ForeignKey(Video) | NOT NULL, CASCADE | Video generating revenue |
| `channel` | ForeignKey(Channel) | NOT NULL, CASCADE | Channel owning the video |
| `date` | DateField | Indexed | Date of revenue snapshot |
| `ad_impressions` | IntegerField | Default: 0 | Number of ad impressions served |
| `ad_revenue_cents` | IntegerField | Default: 0 | Revenue from ads (in cents) |
| `premium_views` | IntegerField | Default: 0 | Views from premium subscribers |
| `premium_revenue_cents` | IntegerField | Default: 0 | Revenue from premium views (in cents) |
| `total_revenue_cents` | IntegerField | Default: 0 | Total revenue for the day (in cents) |
| `creator_share_percentage` | DecimalField(5,2) | Default: 70.00, Min: 0 | Creator's revenue share percentage |
| `creator_revenue_cents` | IntegerField | Default: 0 | Creator's earnings after revenue split (in cents) |
| `created_at` | DateTimeField | Auto | When record was created |

#### Relationships
- **Video:** Many-to-One via `video` field
  - Related name: `revenue_shares`
  - CASCADE delete - removes revenue records when video deleted
  - One video has multiple daily revenue records

- **Channel:** Many-to-One via `channel` field
  - Related name: `revenue_shares`
  - CASCADE delete - removes revenue records when channel deleted
  - One channel has multiple revenue records across all videos

#### Constraints
- **Unique Together:** `[video, date]`
  - One revenue record per video per day
  - Prevents duplicate daily snapshots

#### Indexes
- Single index on `date` - Fast date-based filtering
- Composite index on `(channel, date)` - Channel revenue queries
- Composite index on `(video, date)` - Video revenue queries

#### Validators
- **creator_share_percentage:** `MinValueValidator(0)` - Ensures non-negative percentage

#### Meta Options
- **Ordering:** `["-date"]` - Most recent first
- **DB Table:** `revenue_shares`

#### Revenue Calculation Logic
```
total_revenue_cents = ad_revenue_cents + premium_revenue_cents
creator_revenue_cents = total_revenue_cents * (creator_share_percentage / 100)
platform_revenue_cents = total_revenue_cents - creator_revenue_cents
```

---

### 3. PayoutMethod

**Purpose:** Stores creator payment method configurations for processing payouts securely.

**Table Name:** `payout_methods`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary Key | Auto-incrementing unique identifier |
| `channel` | ForeignKey(Channel) | NOT NULL, CASCADE | Channel owning the payout method |
| `method_type` | CharField(50) | Choices | Type of payment method |
| `account_details` | JSONField | NOT NULL | Encrypted account information (JSON) |
| `is_default` | BooleanField | Default: False | Whether this is the default payment method |
| `is_verified` | BooleanField | Default: False | Whether payment method is verified |
| `created_at` | DateTimeField | Auto | When method was added |
| `updated_at` | DateTimeField | Auto | Last update timestamp |

#### Relationships
- **Channel:** Many-to-One via `channel` field
  - Related name: `payout_methods`
  - CASCADE delete - removes payment methods when channel deleted
  - One channel can have multiple payment methods

#### Method Type Choices

| Value | Display Name | Description |
|-------|--------------|-------------|
| `bank_transfer` | Bank Transfer | Direct bank account transfer |
| `paypal` | PayPal | PayPal account payment |
| `mobile_banking` | Mobile Banking | Mobile banking services (e.g., bKash, Nagad) |

#### Account Details Structure (JSONField)

**Note:** Should be encrypted at application level before storage.

**Bank Transfer:**
```json
{
  "account_holder_name": "John Doe",
  "bank_name": "Example Bank",
  "account_number": "encrypted_value",
  "routing_number": "encrypted_value",
  "swift_code": "EXAMPLEXXX"
}
```

**PayPal:**
```json
{
  "email": "encrypted_email@example.com",
  "account_id": "encrypted_value"
}
```

**Mobile Banking:**
```json
{
  "provider": "bKash",
  "account_number": "encrypted_value",
  "account_holder_name": "John Doe"
}
```

#### Meta Options
- **Ordering:** `["-is_default", "-created_at"]` - Default method first, then by creation date
- **DB Table:** `payout_methods`

#### Security Considerations
- **Encryption Required:** `account_details` must be encrypted before storage
- **Verification:** `is_verified` flag ensures payment method validity
- **Default Method:** Only one method should have `is_default=True` per channel

---

## Dependencies

### Required Imports
```python
from django.db import models
from django.core.validators import MinValueValidator
from .choices import PayoutStatus
```

### Related Models
- **Channel:** Creator/channel model
  - Referenced by: `CreatorPayout`, `RevenueShare`, `PayoutMethod`
  
- **Video:** Video content model
  - Referenced by: `RevenueShare`

### External Dependencies
- **PayoutStatus:** Enum/TextChoices class defining payout status values
  - Located in: `.choices` module
  - Values: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED

---

## Model Relationships

### Entity Relationship Overview

```
Channel ──┬──→ CreatorPayout (payouts)
          ├──→ RevenueShare (revenue_shares)
          └──→ PayoutMethod (payout_methods)

Video ────→ RevenueShare (revenue_shares)
```

### Relationship Details

#### **Revenue Flow**
1. **Video → RevenueShare:** Daily revenue attribution per video
2. **RevenueShare → Channel:** Aggregated revenue per channel
3. **Channel → CreatorPayout:** Periodic payout based on accumulated revenue

#### **Payment Processing**
1. **Channel → PayoutMethod:** Payment method configuration
2. **PayoutMethod → CreatorPayout:** Selected method for payout execution

#### **Data Aggregation Pattern**
```
Daily: Video generates revenue → RevenueShare (daily snapshot)
Weekly/Monthly: RevenueShare records aggregated → CreatorPayout (periodic)
```

### Cardinality

| Relationship | Type | Description |
|--------------|------|-------------|
| Channel → CreatorPayout | One-to-Many | One channel has multiple payouts over time |
| Channel → RevenueShare | One-to-Many | One channel has revenue from multiple videos |
| Video → RevenueShare | One-to-Many | One video has daily revenue records |
| Channel → PayoutMethod | One-to-Many | One channel can have multiple payment methods |

---

## Payout Lifecycle

### Status Flow
```
PENDING → PROCESSING → COMPLETED
                    ↓
                  FAILED
                    ↓
                CANCELLED
```

### Timestamp Tracking
1. **created_at:** Payout record created
2. **processed_at:** Payment processing initiated
3. **completed_at:** Payment successfully transferred

### Revenue Calculation Example
```python
# Daily revenue attribution
total_revenue = ad_revenue + premium_revenue
creator_revenue = total_revenue * (creator_share_percentage / 100)

# Periodic payout calculation
gross_revenue = sum(creator_revenue for period)
platform_fee = gross_revenue * platform_fee_rate
gateway_fee = gross_revenue * gateway_fee_rate
tax_withheld = gross_revenue * tax_rate
net_payout = gross_revenue - platform_fee - gateway_fee - tax_withheld
```

### Currency Handling
- All monetary values stored in **cents** (smallest currency unit)
- Prevents floating-point precision errors
- Convert to dollars/major unit for display: `amount_cents / 100`
- Support for multiple currencies via ISO 4217 codes