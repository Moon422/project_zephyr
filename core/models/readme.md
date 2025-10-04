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

## Table of Contents
- [Channel](#channel)
- [Subscription](#subscription)

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