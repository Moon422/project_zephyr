Below is developer-facing documentation for the Django data models found in repomix-output.xml. It is structured for an open-source repository: each model includes purpose, fields, relationships, constraints, indexes, typical operations, and SRS mapping notes. Where relevant, I highlight divergences or confirmations against SRS Section 20 and related sections.

Repository modules
- user.py: User, SocialAuth, RefreshToken, PasswordResetToken
- channel.py: Channel, Subscription
- video.py: Video, VideoVersion, VideoAsset, VideoTag, VideoTagRelation, Subtitle
- interaction.py: Interaction, WatchSession, Playlist, PlaylistItem
- comment.py: Comment, CommentReaction
- moderation.py: Flag, ModerationLog, UserSuspension
- subscription.py: SubscriptionPlan, UserSubscription, PaymentTransaction, PromotionalCode, PromoCodeUsage
- payment.py: CreatorPayout, RevenueShare, PayoutMethod
- analytics.py: TrendingVideo, RecommendationCache, SearchQuery, PopularSearch, ChannelAnalytics, VideoAnalytics, UserWatchHistory

Conventions
- All model table names are set via Meta.db_table and most include useful composite indexes.
- Deletions are mostly CASCADE for owned/child data (e.g., comments, assets) and SET_NULL for reviewer links or optional references.
- Timestamps: created_at present on most records; updated_at on many; soft-delete fields exist on selected models (User, Channel, Video).
- Choices are centralized in choices.py and used throughout.

1) User and Identity (user.py)
User
Purpose: Custom user model with email login, roles, security features, preferences, and soft-delete. Maps to SRS entity User.

Key fields:
- email (unique, indexed), username (unique, indexed), first_name, last_name, birthdate, avatar_url, bio
- role (choices: GUEST/VIEWER/CREATOR/MODERATOR/ADMIN/PREMIUM), status (ACTIVE/SUSPENDED/BANNED/PENDING_VERIFICATION/DELETED)
- Security: mfa_enabled, mfa_secret, failed_login_attempts, locked_until, last_login_ip
- Preferences: preferred_language (en/bn), email_notifications_enabled
- Metadata: is_staff, is_active, email_verified, email_verified_at
- Timestamps: created_at (indexed), updated_at, deleted_at (soft delete)

Relationships:
- One-to-one Channel via Channel.user (reverse: user.channel)
- One-to-one UserSubscription via related_name active_subscription
- Many child relations across the app (comments, flags, interactions, etc.)

Constraints/Indexes:
- UNIQUE email, username
- Indexes on (email, status), username, (role, status)

Helpers:
- full_name (property)
- is_creator (property; returns True for CREATOR or ADMIN)
- is_premium (property; delegates to active_subscription.is_active)
- soft_delete() sets deleted flags and DELETED status

SRS alignment:
- Matches Section 10 (Auth, MFA, sessions), Section 20 User entity. Age minimum policy (Section 3.2) is not enforced here; implement in application logic/validators.

SocialAuth
Purpose: OAuth connection records (Google, Facebook, Apple optional). Maps to SRS 10.1 Social logins.

Fields:
- user (FK), provider, provider_user_id, access_token, refresh_token, expires_at
Constraints:
- unique_together (provider, provider_user_id)
- Index on (user, provider)

RefreshToken
Purpose: Manage rotating JWT refresh tokens. Maps to SRS 10.3 Sessions.

Fields:
- user (FK), token (unique, indexed), expires_at, revoked, revoked_at, device_info, ip_address, created_at
Computed:
- is_valid property
Methods:
- revoke()

PasswordResetToken
Purpose: Password reset flows. Maps to SRS 10.4 Account Deletion and general auth flows.

Fields:
- user, token (unique, indexed), expires_at, used, used_at, created_at
Computed:
- is_valid property

2) Channels and Subscriptions (channel.py)
Channel
Purpose: Creator’s channel profile, quotas, stats, monetization flags. Maps to SRS Channel entity and quota rules (Section 4.3).

Fields:
- user (OneToOne), name, handle (unique slug, indexed), description
- Branding: avatar_url, banner_url
- status (choices: ACTIVE/SUSPENDED/UNDER_REVIEW/DELETED), verified, verified_at
- Stats: subscriber_count (indexed), total_views, total_videos
- Monetization: monetization_enabled, monetization_enabled_at
- Quotas: max_videos_per_week, max_video_duration_minutes, max_file_size_gb
- Timestamps: created_at (indexed), updated_at, deleted_at

Indexes:
- handle, (status, verified), subscriber_count

Methods:
- update_quotas(): applies rules based on subscriber_count (>=1000 unlocks unlimited weekly count, 12h max duration, 50GB file size; else default 10/week, 15m, 2GB)
- increment_subscriber_count(), decrement_subscriber_count() using F expressions; updates quotas when incrementing

SRS alignment:
- Implements explicit quotas from SRS 4.3 and upgrade path (R5).
- Consider admin overrides (SRS 12.1) via the portal; model supports direct edits.

Subscription (Channel subscription by a user)
Purpose: Follows/subscribe to a Channel; notification preference. Maps to SRS 7.1 subscriptions.

Fields:
- subscriber (User), channel (Channel), notifications_enabled, subscribed_at
Constraints:
- unique_together (subscriber, channel)
Indexes:
- (subscriber, channel), (channel, subscribed_at)

3) Video and Media (video.py)
Video
Purpose: Core video record with status, visibility, restrictions, stats, and link to active version. Maps to SRS Video entity.

Fields:
- channel (FK), title, description
- status (choices VideoStatus; indexed), visibility (PUBLIC/UNLISTED/PREMIUM/PRIVATE)
- Restriction: age_restricted, geo_restrictions (JSON of country codes)
- active_version (FK to VideoVersion, nullable)
- Thumbnails: thumbnail_url, thumbnail_auto_generated
- Stats: view_count (indexed), like_count, dislike_count, comment_count, share_count
- Engagement: average_watch_time_seconds, completion_rate (0–100)
- Metadata: duration_seconds, language
- Timestamps: published_at (indexed), created_at (indexed), updated_at, deleted_at, last_activity_at

Indexes:
- (channel, status), (status, visibility, published_at), view_count, -published_at

Methods:
- publish(): transitions Processing -> Published and sets published_at if active_version present
- increment_view_count(): F expression increment + last_activity_at update
Properties:
- is_published

SRS alignment:
- Matches Video fields and lifecycle (Section 4), visibility settings (premium only), age restriction.

VideoVersion
Purpose: Versioning for re-uploads; holds source & transcoding state. Maps to SRS 4.2 Versioning and 24 architecture.

Fields:
- video (FK), version_number, is_active
- Source: source_object_key (S3 key), size, duration, resolution, codec
- Transcoding: profile set, status (TranscodingStatus), started/completed/error
- created_at
Constraints/Indexes:
- unique (video, version_number), index (video, is_active)

VideoAsset
Purpose: Transcoded variant records for ABR ladder. Maps to SRS 5.2/5.3.

Fields:
- video_version (FK), resolution (choices: 240p…1440p), bitrate_kbps
- playlist_url, segment_path_prefix
- file_size_bytes, codec
Constraints/Indexes:
- unique (video_version, resolution), index (video_version, resolution)

VideoTag and VideoTagRelation
Purpose: Tagging and mapping between videos and tags. Maps to SRS 8.2 Indexed fields (tags).

VideoTag fields:
- name (unique, indexed), slug (unique), usage_count, created_at

VideoTagRelation fields:
- video (FK), tag (FK), created_at
Constraints/Indexes:
- unique (video, tag), indexes on video and tag

Subtitle
Purpose: External subtitle tracks per video version. Maps to SRS 6.1 Subtitles.

Fields:
- video_version (FK), language_code, language_name
- file_key, file_url, is_published, is_auto_generated
- created_at, updated_at
Constraints/Indexes:
- unique (video_version, language_code), index (video_version, language_code)

4) Interactions, Sessions, Playlists (interaction.py)
Interaction
Purpose: Generic record for video interactions: LIKE, DISLIKE, VIEW, NOT_INTERESTED, WATCH_TIME. Maps to SRS 7.1, 7.2, 9.1 signals.

Fields:
- user (FK nullable for anonymous), video (FK), type (InteractionType), value (seconds for WATCH_TIME; 1/0 flag for like/dislike), session_id (indexed), ip_address, user_agent, timestamp (indexed)
Indexes:
- (video, type, timestamp), (user, video, type), session_id

Notes:
- Model allows multiple records per user/video/type; deduplication logic belongs in services if needed.
- “Not Interested” covered via InteractionType.

WatchSession
Purpose: Fine-grained QoE and watch metrics per session. Maps to SRS 13.1 QoE.

Fields:
- user (nullable), video, session_id (indexed)
- watch_time_seconds, completion_percentage (Decimal, min 0)
- QoE: rebuffer_count, rebuffer_duration_seconds, startup_time_ms, average_bitrate_kbps
- Device/Network: device_type, browser, os, ip_address, country_code
- Timestamps: started_at, ended_at
Indexes:
- (video, started_at), (user, started_at), session_id

Playlist and PlaylistItem
Purpose: User-created playlists and their items. Maps to SRS 6.1 Playlist, 21. Playlists.

Playlist fields:
- user, title, description, is_public, created_at, updated_at
Indexes:
- (user, is_public)

PlaylistItem fields:
- playlist, video, position, added_at
Constraints/Indexes:
- unique (playlist, video), index (playlist, position)

5) Comments (comment.py)
Comment
Purpose: Threaded comments (2 levels: parent and replies). Maps to SRS 7 social and 20 Comment entity.

Fields:
- video, user, parent (nullable), text
- status (ACTIVE/FLAGGED/HIDDEN/REMOVED)
- denormalized counts: like_count, dislike_count, reply_count
- edited, edited_at
- created_at (indexed), updated_at, deleted_at
Indexes:
- (video, status, created_at), (user, created_at), (parent)

Computed:
- is_reply property

CommentReaction
Purpose: Likes/dislikes on comments. Maps to SRS 7.1 comment reactions.

Fields:
- comment, user, is_like (bool), created_at
Constraints/Indexes:
- unique (comment, user), indexes on (comment, is_like), user

6) Moderation (moderation.py)
Flag
Purpose: Reports on any content via generic relations; covers videos, comments, users. Maps to SRS 12 moderation rules.

Fields:
- content_type, object_id, content_object (Generic)
- user (flagger, nullable), reason (choices FlagReason), reason_detail
- status (FlagStatus), reviewed_by (User nullable), reviewed_at, review_notes
- created_at (indexed)
Indexes:
- (content_type, object_id), (status, created_at), user

ModerationLog
Purpose: Audit trail of moderation actions. Maps to SRS 12.3 logging/audit.

Fields:
- moderator (nullable), content_type/object_id (Generic), action (ModerationAction), reason, related_flag (nullable)
- duration_days, expires_at
- created_at (indexed)
Indexes:
- (moderator, created_at), (content_type, object_id), (action, created_at)

UserSuspension
Purpose: Record suspensions with expiry and lifting. Maps to SRS 12 actions.

Fields:
- user, reason, suspended_by, is_permanent
- suspended_at, expires_at, lifted_at, lifted_by
Indexes:
- (user, suspended_at)
Computed:
- is_active property computes active suspension state

7) Subscriptions and Billing (subscription.py)
SubscriptionPlan
Purpose: Premium plan catalog. Maps to SRS 11.1 Plans.

Fields:
- name, plan_type (unique; FREE, PREMIUM_MONTHLY, PREMIUM_ANNUAL)
- Features: max_resolution (default 1440p), ad_free, premium_content_access, early_access
- Pricing: price_monthly_cents, price_annual_cents (optional)
- Display currency, is_active
- created_at, updated_at
Ordering: by price_monthly_cents

UserSubscription
Purpose: A user’s current subscription. Maps to SRS 11.2 Subscriptions.

Fields:
- user (OneToOne), plan (PROTECT)
- status (ACTIVE/CANCELLED/EXPIRED/GRACE_PERIOD/SUSPENDED)
- payment_gateway (SSLCommerz/2Checkout), gateway ids
- start_date (default now), end_date, renewal_date
- cancelled_at, cancel_at_period_end
- grace_period_ends_at
- created_at, updated_at
Indexes:
- (user, status), (status, renewal_date)
Computed:
- is_active property honors GRACE_PERIOD window

PaymentTransaction
Purpose: Gateway transaction ledger. Maps to SRS 11.6 gateways and general billing.

Fields:
- user, subscription (nullable)
- payment_gateway, gateway_transaction_id (unique)
- amount_cents, currency, status (string: pending/completed/failed/refunded)
- payment_method, failure_reason
- created_at (indexed), completed_at
Indexes:
- (user, status), gateway_transaction_id

PromotionalCode and PromoCodeUsage
Purpose: Discount codes and their usages. Maps to SRS 11.7 Promotional Codes.

PromotionalCode fields:
- code (unique, indexed), discount_type (percentage/fixed), discount_value
- valid_from, valid_until, max_uses, max_uses_per_user, current_uses
- applicable_plans (M2M), is_active, created_at
Computed:
- is_valid property checks time window, active and caps

PromoCodeUsage fields:
- promo_code, user, transaction (nullable)
- discount_applied_cents, used_at
Indexes:
- (promo_code, user)

8) Payouts and Revenue Attribution (payment.py)
CreatorPayout
Purpose: Aggregated payouts per channel and period. Maps to SRS 11.5 Creator Revenue Share and payouts.

Fields:
- channel, period_start, period_end
- ad_revenue_cents, premium_revenue_cents, total_revenue_cents
- platform_fee_cents, payment_gateway_fee_cents, tax_withheld_cents
- net_payout_cents, currency (default USD)
- status (PENDING/PROCESSING/COMPLETED/FAILED/CANCELLED)
- payment_method, payment_reference
- created_at, processed_at, completed_at
- notes, failure_reason
Constraints/Indexes:
- unique (channel, period_start, period_end)
- (channel, status), (status, created_at)
Computed:
- payout_amount_display

RevenueShare
Purpose: Per-video daily revenue attribution and creator share computation. Maps to SRS 11.5 and analytics.

Fields:
- video, channel, date
- ad_impressions, ad_revenue_cents
- premium_views, premium_revenue_cents
- total_revenue_cents
- creator_share_percentage (default 70.00), creator_revenue_cents
Constraints/Indexes:
- unique (video, date), (channel, date), (video, date)

PayoutMethod
Purpose: Creator payout configuration. Maps to SRS 11.6 gateway-agnostic payout methods.

Fields:
- channel, method_type (bank_transfer/paypal/mobile_banking)
- account_details (JSON; should be encrypted in app layer)
- is_default, is_verified
- created_at, updated_at

9) Analytics and Recommendations (analytics.py)
TrendingVideo
Purpose: Cached trending ranks per date/region/category. Maps to SRS 9 trending, 13 analytics.

Fields:
- video, rank, score, category, region (default BD), date (indexed), created_at
Constraints/Indexes:
- unique (video, date, region); index (date, region, rank)

RecommendationCache
Purpose: Per-user cached recommendation lists by context. Maps to SRS 9.3 infrastructure design.

Fields:
- user, video_ids (JSON list), context (home/watch_next/etc.), algorithm_version, score_threshold, expires_at (indexed), created_at, updated_at
Constraints/Indexes:
- unique (user, context); indexes on (user, context) and expires_at
Helpers:
- get_video_ids(), set_video_ids(video_ids) cap to 50

SearchQuery and PopularSearch
Purpose: Search telemetry and aggregated popular queries. Maps to SRS 8 search analytics.

SearchQuery fields:
- user (nullable), query, normalized_query (auto lower/trim on save), result_count
- clicked_video (nullable), click_position
- session_id, ip_address
- created_at (indexed)
Indexes:
- (normalized_query, created_at), (user, created_at)

PopularSearch fields:
- query (unique, indexed), search_count, click_through_rate
- daily_count, weekly_count, monthly_count, last_searched_at
Indexes:
- -search_count, query

ChannelAnalytics and VideoAnalytics
Purpose: Daily aggregates. Maps to SRS 13.2/13.3/13.1.

ChannelAnalytics fields:
- channel, date (unique per channel/date)
- total_views, unique_viewers
- total_watch_time_seconds, average_view_duration_seconds
- likes, dislikes, comments, shares
- new_subscribers, unsubscribers, net_subscriber_change
- estimated_revenue_cents
- traffic_source_data (JSON)
- created_at
Computed:
- estimated_revenue ($), average_watch_time_minutes

VideoAnalytics fields:
- video, date (unique per video/date)
- views, unique_viewers
- watch_time_seconds, average_view_duration_seconds, average_percentage_viewed
- likes, dislikes, comments, shares
- retention_curve (list of floats per 5% interval)
- demographics_data, traffic_sources (JSON)
- estimated_revenue_cents, created_at
Computed:
- estimated_revenue ($), engagement_rate, watch_time_hours

UserWatchHistory
Purpose: Per-user last watch state and completion flag per video (unique). Maps to SRS 9.1 signals and 6.1 playback resume.

Fields:
- user, video
- watch_percentage, watch_duration_seconds, completed
- last_position_seconds
- watched_at (indexed), updated_at
Constraints/Indexes:
- unique (user, video)
Helpers:
- mark_completed() if watch_percentage >= 90
- watch_duration_minutes

10) Cross-cutting index and constraint notes
- Most high-cardinality queries are covered by composite indexes (e.g., interactions by video/type/time; comments by video/status/time).
- Many-to-one relations default to CASCADE, which matches UGC lifecycle (deleting a video cascades to comments, assets, analytics records).
- Unique constraints ensure data integrity for one-to-one-like records (e.g., UserSubscription per user, VideoVersion per video/version number, PlaylistItem uniqueness).

11) SRS mapping summary and divergences
- Matches SRS Section 20 entities: User, Channel, Video, VideoVersion, VideoAsset, Subtitle, Interaction, Comment, Flag, SubscriptionPlan, UserSubscription, CreatorPayout, RecommendationCache. Additional useful entities exist: Tagging, Playlists, RevenueShare, QoE sessions, Search telemetry, Social auth, Tokens, Moderation logs, Suspensions, Promo codes.
- Session/Token models (RefreshToken, PasswordResetToken, SocialAuth) implement SRS 10 auth/session/MFA integration points.
- Monetization aligns with SRS 11; payout threshold/frequency are not encoded in models (should be configuration in app/admin).
- Age policy/KYC, DMCA retention windows, archival moves are not automatically enforced in models; implement in scheduled jobs/services using last_activity_at, deleted_at, and VideoStatus. The Video.last_activity_at supports archival (SRS 4.1 step 9).
- Search engine choice (SRS 8.1) is not represented here; these models support telemetry regardless of engine.

12) Usage examples
Create a user and channel
- user = User.objects.create_user(email="a@b.com", username="alice", password="secret")
- channel = Channel.objects.create(user=user, name="Alice TV", handle="alice-tv")
- channel.update_quotas()

Upload and publish a video
- v = Video.objects.create(channel=channel, title="My First Vlog", status=VideoStatus.PROCESSING)
- vv1 = VideoVersion.objects.create(video=v, version_number=1, source_object_key="uploads/uuid.mp4")
- v.active_version = vv1; v.save(update_fields=["active_version"])
- v.publish()

Add ABR assets
- VideoAsset.objects.create(video_version=vv1, resolution=VideoResolution.RES_1080P, bitrate_kbps=4500, playlist_url="https://...", segment_path_prefix="s3://...", file_size_bytes=123456789)

Interactions and analytics
- Interaction.objects.create(user=user, video=v, type=InteractionType.LIKE, value=1)
- ws = WatchSession.objects.create(user=user, video=v, session_id="abc123", watch_time_seconds=600, startup_time_ms=1200)
- UserWatchHistory.objects.update_or_create(user=user, video=v, defaults={"watch_percentage": 95.0, "completed": True})

Commenting
- c = Comment.objects.create(video=v, user=user, text="Great video!")
- CommentReaction.objects.create(comment=c, user=user, is_like=True)

Subscriptions
- plan = SubscriptionPlan.objects.create(name="Premium Monthly", plan_type=SubscriptionPlanType.PREMIUM_MONTHLY, price_monthly_cents=399, price_annual_cents=3599)
- us = UserSubscription.objects.create(user=user, plan=plan, payment_gateway=PaymentGateway.SSLCOMMERZ, renewal_date=timezone.now() + timedelta(days=30))

Playlists
- pl = Playlist.objects.create(user=user, title="Watch Later")
- PlaylistItem.objects.create(playlist=pl, video=v, position=1)

Moderation
- flag = Flag.objects.create(content_object=v, user=user, reason=FlagReason.SPAM)
- ModerationLog.objects.create(moderator=None, content_object=v, action=ModerationAction.NO_ACTION, reason="Auto-review passed", related_flag=flag)

Payouts
- rs = RevenueShare.objects.create(video=v, channel=channel, date=date.today(), ad_impressions=1000, ad_revenue_cents=500, creator_revenue_cents=350)
- CreatorPayout.objects.create(channel=channel, period_start=date(2025,9,1), period_end=date(2025,9,30), total_revenue_cents=10000, net_payout_cents=7000)

13) Data retention and operational notes
- Soft deletes: User.deleted_at, Channel.deleted_at, Video.deleted_at. Implement periodic purge/anonymization jobs respecting SRS 10.4 and 13.5.
- Archival: Use Video.last_activity_at and VideoStatus. For lifecycle moves to Glacier, handle externally; models store metadata only.
- Unique per-user history: UserWatchHistory ensures one row per (user, video) for resume/recency; update on playback.
- Quotas: Enforced via Channel.update_quotas and application logic during upload; consider capturing effective quotas in audit logs when changed.

14) Permissions and admin suggestions
- Use Django admin with list_display filters on status fields and search on handle, title, username, email.
- Enforce role-based access in services, e.g., only channel owner or admin can modify a Video; moderators write ModerationLog entries.
- Consider signals or service layer for denormalized counters consistency (e.g., increment/decrement like_count, reply_count).

15) Potential extensions
- Add unique constraint for one active VideoVersion per Video (currently implied by logic, not enforced).
- For Interaction likes/dislikes, consider a separate unique constraint to prevent multiple likes per user per video if stored via Interaction instead of a dedicated Like model.
- Add indexes for frequent listing queries, e.g., Video.visibility combined with published_at.
- Introduce a Deleted/Removed status timestamp reason in Video for DMCA transparency (SRS 17.3).
- If guests are restricted to 720p (SRS D16), enforce in playback service; VideoAsset already holds higher variants.

How to consume this documentation
- Each model above can be turned into ReST/Sphinx or MkDocs pages. I can generate per-model API docs (autodoc) and cross-reference SRS sections inline.
- If you want, I can produce a docs/ folder with:
  - models/ per-app pages
  - ER diagram (Graphviz/pygraphviz) from these models
  - Migration policy and data retention guide aligned with SRS
  - QuickStart code snippets and admin usage

If you prefer a specific format (e.g., Markdown files per model, Sphinx, or mkdocstrings with YAML navigation), tell me and I’ll output the docs in that structure.