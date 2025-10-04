# 📚 User Authentication & Identity Models Documentation

**File:** `models/user.py`  
**Module:** User Authentication & Identity Management  
**Version:** Project Zephyr MVP

---

## 📋 Overview

This module contains the core authentication and user identity models for the Project Zephyr video streaming platform. It implements a custom user model with enhanced security features including MFA (Multi-Factor Authentication), account lockout mechanisms, soft deletion, and OAuth social login integration.

### Key Responsibilities
- ✅ User account management and authentication
- ✅ Role-based access control (Viewer, Creator, Moderator, Admin)
- ✅ Multi-factor authentication (TOTP)
- ✅ Social OAuth integration (Google, Facebook, Apple)
- ✅ JWT refresh token management with revocation
- ✅ Password reset token handling
- ✅ Account security (lockout after failed attempts)
- ✅ Soft deletion with 30-day recovery window

### Related Modules
- `models/channel.py` - Creator channel management
- `models/subscription.py` - Premium subscription handling
- `models/video.py` - Content ownership and permissions
- `services/auth_service.py` - Authentication business logic

---

## 🔧 Model: `CustomUserManager`

**Purpose:** Custom manager for User model creation with proper email normalization and role assignment.

### Methods

#### `create_user(email, username, password=None, **extra_fields)`
Creates a standard user account.

**Parameters:**
- `email` (str): User's email address (required)
- `username` (str): Unique username (required)
- `password` (str): Plain text password (will be hashed)
- `**extra_fields`: Additional user fields

**Returns:** `User` instance

**Raises:** `ValueError` if email or username is missing

**Example:**
```python
user = User.objects.create_user(
    email='creator@example.com',
    username='awesome_creator',
    password='SecurePass123!',
    first_name='John',
    birthdate='1995-05-15'
)
```

#### `create_superuser(email, username, password=None, **extra_fields)`
Creates an admin user with elevated permissions.

**Auto-sets:**
- `role` → `UserRole.ADMIN`
- `is_staff` → `True`
- `is_superuser` → `True`
- `status` → `UserStatus.ACTIVE`

**Example:**
```python
admin = User.objects.create_superuser(
    email='admin@zephyr.com',
    username='admin',
    password='AdminSecure456!'
)
```

---

## 👤 Model: `User`

**Purpose:** Core user model extending Django's `AbstractBaseUser` with platform-specific fields for authentication, profile management, security, and preferences.

**Inherits:** `AbstractBaseUser`, `PermissionsMixin`

### Field Reference

| Field | Type | Description | Constraints | Default |
|-------|------|-------------|-------------|---------|
| **Authentication** |
| `email` | `EmailField` | Primary login identifier | Unique, max 255 chars, indexed | - |
| `username` | `CharField` | Public display name | Unique, 3-50 chars, indexed | - |
| `password` | `CharField` | Hashed password (Argon2id) | Inherited from AbstractBaseUser | - |
| **Profile** |
| `first_name` | `CharField` | User's first name | Max 100 chars, optional | `''` |
| `last_name` | `CharField` | User's last name | Max 100 chars, optional | `''` |
| `birthdate` | `DateField` | Date of birth (age verification) | Optional, nullable | `None` |
| `avatar_url` | `URLField` | Profile picture URL | Max 500 chars, optional | `''` |
| `bio` | `TextField` | User biography | Max 500 chars, optional | `''` |
| **Role & Status** |
| `role` | `CharField` | User role (see UserRole choices) | Max 20 chars | `VIEWER` |
| `status` | `CharField` | Account status (see UserStatus) | Max 30 chars | `ACTIVE` |
| **Security** |
| `mfa_enabled` | `BooleanField` | MFA activation status | - | `False` |
| `mfa_secret` | `CharField` | TOTP secret key (encrypted) | Max 32 chars, optional | `''` |
| `failed_login_attempts` | `IntegerField` | Failed login counter | Min 0 | `0` |
| `locked_until` | `DateTimeField` | Account lockout expiry | Optional, nullable | `None` |
| `last_login_ip` | `GenericIPAddressField` | Last successful login IP | IPv4/IPv6, nullable | `None` |
| **Preferences** |
| `preferred_language` | `CharField` | UI language preference | Max 5 chars (see LanguageCode) | `ENGLISH` |
| `email_notifications_enabled` | `BooleanField` | Email notification opt-in | - | `True` |
| **Metadata** |
| `is_staff` | `BooleanField` | Django admin access | - | `False` |
| `is_active` | `BooleanField` | Account active status | - | `True` |
| `email_verified` | `BooleanField` | Email verification status | - | `False` |
| `email_verified_at` | `DateTimeField` | Email verification timestamp | Optional, nullable | `None` |
| `created_at` | `DateTimeField` | Account creation timestamp | Auto, indexed | `now()` |
| `updated_at` | `DateTimeField` | Last update timestamp | Auto | `now()` |
| `deleted_at` | `DateTimeField` | Soft deletion timestamp | Nullable | `None` |

### Database Configuration

```python
USERNAME_FIELD = "email"  # Login with email
REQUIRED_FIELDS = ["username"]  # Required for createsuperuser

class Meta:
    db_table = "users"
    ordering = ["-created_at"]  # Newest first
```

### Indexes

```python
indexes = [
    models.Index(fields=["email", "status"]),     # Login queries
    models.Index(fields=["username"]),            # Profile lookups
    models.Index(fields=["role", "status"]),      # Admin filtering
]
```

**Performance Notes:**
- Composite index on `(email, status)` optimizes authentication queries
- Single-column indexes support unique constraints and fast lookups
- `created_at` index supports chronological sorting

---

### Properties

#### `full_name`
**Returns:** User's full name or username as fallback

```python
user.full_name  # "John Doe" or "awesome_creator"
```

#### `is_creator`
**Returns:** `True` if user has creator or admin role

```python
if user.is_creator:
    # Allow video upload
    pass
```

**Business Rule:** Aligns with SRS requirement that creators can upload content.

#### `is_premium`
**Returns:** `True` if user has active premium subscription

```python
if user.is_premium:
    # Enable 1440p playback
    # Disable ads
    pass
```

**Note:** Checks for related `UserSubscription` with active status.

---

### Methods

#### `soft_delete()`
Performs soft deletion with 30-day recovery window (per SRS Section 10.4).

**Actions:**
1. Sets `deleted_at` to current timestamp
2. Changes `status` to `UserStatus.DELETED`
3. Sets `is_active` to `False`

```python
user.soft_delete()
# User can be recovered within 30 days
# After 30 days, PII is purged via scheduled job
```

**Related SRS:** Section 10.4 - Account Deletion

---

### Usage Examples

#### User Registration
```python
from django.utils import timezone
from datetime import date

# Create new viewer account
user = User.objects.create_user(
    email='viewer@example.com',
    username='movie_fan',
    password='SecurePassword123!',
    birthdate=date(1998, 3, 20),
    preferred_language=LanguageCode.BANGLA
)

# Verify email (simulate verification flow)
user.email_verified = True
user.email_verified_at = timezone.now()
user.save()
```

#### Upgrade to Creator
```python
# User requests creator access
user.role = UserRole.CREATOR
user.save()

# Now user can create channel and upload videos
```

#### Enable MFA
```python
import pyotp

# Generate TOTP secret
secret = pyotp.random_base32()
user.mfa_secret = secret
user.mfa_enabled = True
user.save()

# User scans QR code with authenticator app
```

#### Account Lockout (Security)
```python
# After 5 failed login attempts (per SRS Section 10.2)
from datetime import timedelta

user.failed_login_attempts += 1

if user.failed_login_attempts >= 5:
    user.locked_until = timezone.now() + timedelta(minutes=15)
    user.save()
    # Exponential backoff on subsequent failures
```

#### Query Active Creators
```python
# Find all active creators for analytics
active_creators = User.objects.filter(
    role=UserRole.CREATOR,
    status=UserStatus.ACTIVE,
    deleted_at__isnull=True
)
```

---

## 🔗 Model: `SocialAuth`

**Purpose:** Manages OAuth social login connections (Google, Facebook, Apple) as per SRS Section 10.1.

### Field Reference

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user` | `ForeignKey` | Related user account | CASCADE delete, indexed |
| `provider` | `CharField` | OAuth provider name | Max 50 chars (`google`, `facebook`, `apple`) |
| `provider_user_id` | `CharField` | Provider's unique user ID | Max 255 chars |
| `access_token` | `TextField` | OAuth access token (encrypted) | Optional |
| `refresh_token` | `TextField` | OAuth refresh token (encrypted) | Optional |
| `expires_at` | `DateTimeField` | Token expiration timestamp | Nullable |
| `created_at` | `DateTimeField` | Connection creation time | Auto |
| `updated_at` | `DateTimeField` | Last token refresh time | Auto |

### Database Configuration

```python
class Meta:
    db_table = "social_auths"
    unique_together = [["provider", "provider_user_id"]]  # One account per provider
    indexes = [
        models.Index(fields=["user", "provider"]),  # Fast user lookup
    ]
```

### Usage Examples

#### Link Google Account
```python
# After OAuth callback
social_auth = SocialAuth.objects.create(
    user=user,
    provider='google',
    provider_user_id='108123456789012345678',
    access_token='ya29.a0AfH6SMB...',
    refresh_token='1//0gHdP...',
    expires_at=timezone.now() + timedelta(hours=1)
)
```

#### Check Existing Connections
```python
# Prevent duplicate social logins
existing = SocialAuth.objects.filter(
    provider='facebook',
    provider_user_id='1234567890'
).first()

if existing:
    # Log in existing user
    user = existing.user
else:
    # Create new user account
    pass
```

#### Revoke Social Connection
```python
# User wants to unlink Google account
SocialAuth.objects.filter(
    user=user,
    provider='google'
).delete()
```

---

## 🎫 Model: `RefreshToken`

**Purpose:** JWT refresh token management with revocation support (per SRS Section 10.3).

**Security Features:**
- 30-day validity (rotating tokens)
- Device tracking
- IP logging
- Revocation list

### Field Reference

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user` | `ForeignKey` | Token owner | CASCADE delete, indexed |
| `token` | `CharField` | Refresh token string | Max 500 chars, unique, indexed |
| `expires_at` | `DateTimeField` | Token expiration | Required |
| `revoked` | `BooleanField` | Revocation status | Default `False` |
| `revoked_at` | `DateTimeField` | Revocation timestamp | Nullable |
| `device_info` | `CharField` | User agent string | Max 255 chars, optional |
| `ip_address` | `GenericIPAddressField` | Request IP address | IPv4/IPv6, nullable |
| `created_at` | `DateTimeField` | Token creation time | Auto |

### Database Configuration

```python
class Meta:
    db_table = "refresh_tokens"
    ordering = ["-created_at"]  # Newest first
    indexes = [
        models.Index(fields=["user", "revoked"]),  # Active token queries
        models.Index(fields=["token"]),            # Fast token lookup
    ]
```

### Properties

#### `is_valid`
**Returns:** `True` if token is not revoked and not expired

```python
if refresh_token.is_valid:
    # Issue new access token
    pass
else:
    # Require re-authentication
    pass
```

### Methods

#### `revoke()`
Revokes the refresh token immediately.

```python
refresh_token.revoke()
# Sets revoked=True and revoked_at=now()
```

### Usage Examples

#### Issue Refresh Token
```python
from datetime import timedelta
import secrets

# After successful login
refresh_token = RefreshToken.objects.create(
    user=user,
    token=secrets.token_urlsafe(64),
    expires_at=timezone.now() + timedelta(days=30),
    device_info=request.META.get('HTTP_USER_AGENT', ''),
    ip_address=request.META.get('REMOTE_ADDR')
)
```

#### Rotate Refresh Token
```python
# When refreshing access token
old_token.revoke()

new_token = RefreshToken.objects.create(
    user=user,
    token=secrets.token_urlsafe(64),
    expires_at=timezone.now() + timedelta(days=30),
    device_info=old_token.device_info,
    ip_address=request.META.get('REMOTE_ADDR')
)
```

#### Revoke All User Sessions
```python
# User changes password or requests logout from all devices
RefreshToken.objects.filter(
    user=user,
    revoked=False
).update(
    revoked=True,
    revoked_at=timezone.now()
)
```

#### Cleanup Expired Tokens (Scheduled Job)
```python
# Daily cleanup task
expired_tokens = RefreshToken.objects.filter(
    expires_at__lt=timezone.now()
)
expired_tokens.delete()
```

---

## 🔐 Model: `PasswordResetToken`

**Purpose:** Secure password reset token management with single-use validation.

### Field Reference

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `user` | `ForeignKey` | User requesting reset | CASCADE delete |
| `token` | `CharField` | Reset token (hashed) | Max 100 chars, unique, indexed |
| `expires_at` | `DateTimeField` | Token expiration (1 hour) | Required |
| `used` | `BooleanField` | Single-use flag | Default `False` |
| `used_at` | `DateTimeField` | Usage timestamp | Nullable |
| `created_at` | `DateTimeField` | Token creation time | Auto |

### Database Configuration

```python
class Meta:
    db_table = "password_reset_tokens"
    ordering = ["-created_at"]
```

### Properties

#### `is_valid`
**Returns:** `True` if token is unused and not expired

```python
if reset_token.is_valid:
    # Allow password reset
    pass
else:
    # Token expired or already used
    pass
```

### Usage Examples

#### Generate Reset Token
```python
import secrets
from datetime import timedelta

# User requests password reset
token = PasswordResetToken.objects.create(
    user=user,
    token=secrets.token_urlsafe(32),
    expires_at=timezone.now() + timedelta(hours=1)
)

# Send email with reset link
send_password_reset_email(user.email, token.token)
```

#### Validate and Use Token
```python
# User clicks reset link
try:
    reset_token = PasswordResetToken.objects.get(token=submitted_token)
    
    if reset_token.is_valid:
        # Allow password change
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.used = True
        reset_token.used_at = timezone.now()
        reset_token.save()
        
        # Invalidate all refresh tokens (security)
        RefreshToken.objects.filter(user=user).update(
            revoked=True,
            revoked_at=timezone.now()
        )
    else:
        # Token invalid
        raise ValidationError("Reset link expired or already used")
        
except PasswordResetToken.DoesNotExist:
    raise ValidationError("Invalid reset token")
```

#### Cleanup Old Tokens (Scheduled Job)
```python
# Delete tokens older than 24 hours
from datetime import timedelta

cutoff = timezone.now() - timedelta(hours=24)
PasswordResetToken.objects.filter(
    created_at__lt=cutoff
).delete()
```

---

## 🔄 Integration Points

### With Channel Model
```python
# User creates a channel (one-to-one relationship)
from models.channel import Channel

channel = Channel.objects.create(
    user=user,
    name=f"{user.username}'s Channel",
    description="Welcome to my channel!"
)
```

### With Subscription Model
```python
# Check premium status
from models.subscription import UserSubscription

if user.is_premium:
    max_resolution = '1440p'
else:
    max_resolution = '1080p'
```

### With Video Model
```python
# Creator uploads video
from models.video import Video

if user.is_creator:
    video = Video.objects.create(
        channel=user.channel,
        title="My First Video",
        # ... other fields
    )
```

### Authentication Flow
```python
# Login with email + password
from django.contrib.auth import authenticate

user = authenticate(
    request,
    username=email,  # USERNAME_FIELD is email
    password=password
)

if user and user.mfa_enabled:
    # Require TOTP verification
    pass
```

---

## 📊 Business Rules Summary

### Age Verification (SRS Section 3.2)
- Minimum registration age: **13 years** (configurable)
- `birthdate` field required for age-restricted content access
- Age gate enforced at playback for flagged videos

### Account Security (SRS Section 10.2)
- **Password Policy:** Min 10 chars, 1 letter + 1 number/symbol
- **Lockout:** 5 failed attempts → 15 min lock (exponential backoff)
- **MFA:** TOTP required for monetization-eligible creators

### Session Management (SRS Section 10.3)
- **Access Token:** 15 min validity (JWT)
- **Refresh Token:** 30 days (rotating, revocable)
- Session invalidation on password change

### Soft Deletion (SRS Section 10.4)
- **Grace Period:** 30 days recovery window
- **PII Purge:** After 30 days, anonymize analytics
- Status changes: `ACTIVE` → `DELETED`

### Role Hierarchy
```
ADMIN (full access)
  ├── MODERATOR (content moderation)
  ├── CREATOR (upload + channel management)
  └── VIEWER (playback + social interactions)
```

---

## 🎯 API Endpoint Examples

### User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "awesome_user",
  "password": "SecurePass123!",
  "birthdate": "1995-08-15",
  "preferred_language": "bn"
}
```

### Login with MFA
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "mfa_code": "123456"  // If MFA enabled
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "dGhpc2lz...",
  "user": { ... }
}
```

### Refresh Access Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "dGhpc2lz..."
}
```

### Password Reset Request
```http
POST /api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

---

## 🔍 Common Queries

### Find Users by Role
```python
creators = User.objects.filter(
    role=UserRole.CREATOR,
    status=UserStatus.ACTIVE
).select_related('channel')
```

### Active Premium Users
```python
from models.subscription import UserSubscription

premium_users = User.objects.filter(
    subscriptions__status='active',
    subscriptions__end_date__gt=timezone.now()
).distinct()
```

### Users with MFA Enabled
```python
mfa_users = User.objects.filter(
    mfa_enabled=True,
    status=UserStatus.ACTIVE
).count()
```

### Recently Registered Users
```python
from datetime import timedelta

new_users = User.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7)
).order_by('-created_at')
```

---

## 🛡️ Security Considerations

### Password Storage
- Uses **Argon2id** hashing (SRS Section 10.1)
- Configuration: `memory=256MB, iterations=3, parallelism=2`

### Token Security
- Refresh tokens stored hashed in database
- Access tokens signed with RS256 (asymmetric)
- Tokens include `jti` (JWT ID) for revocation

### PII Protection
- Sensitive fields encrypted at rest (AES-256)
- `mfa_secret`, `access_token`, `refresh_token` encrypted
- Minimal data collection (SRS Section 17.1)

### Rate Limiting
- Login attempts: 5 per 15 minutes per IP
- Password reset: 3 requests per hour per email
- MFA verification: 5 attempts per 5 minutes

---

## 📈 Performance Optimization

### Database Indexes
```sql
-- Composite index for login queries
CREATE INDEX idx_users_email_status ON users(email, status);

-- Username lookups
CREATE INDEX idx_users_username ON users(username);

-- Admin filtering
CREATE INDEX idx_users_role_status ON users(role, status);

-- Token lookups
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_revoked ON refresh_tokens(user_id, revoked);
```

### Query Optimization
```python
# Use select_related for foreign keys
users_with_channels = User.objects.select_related('channel').filter(
    role=UserRole.CREATOR
)

# Use prefetch_related for reverse foreign keys
users_with_tokens = User.objects.prefetch_related('refresh_tokens').all()
```

---

## ✅ Testing Checklist

- [ ] User registration with valid/invalid data
- [ ] Email uniqueness constraint
- [ ] Username uniqueness and length validation
- [ ] Password hashing (never stored plain text)
- [ ] MFA setup and verification flow
- [ ] Account lockout after failed attempts
- [ ] Soft deletion and recovery
- [ ] Social auth linking/unlinking
- [ ] Refresh token rotation
- [ ] Password reset token expiration
- [ ] Role-based permission checks
- [ ] Premium status calculation

---

**Last Updated:** 2025-10-04  
**SRS Version:** Draft v1  
**Database Schema Version:** 1.0.0