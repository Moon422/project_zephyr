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