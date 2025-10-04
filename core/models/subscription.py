from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from .choices import SubscriptionPlanType, SubscriptionStatus, PaymentGateway


class SubscriptionPlan(models.Model):
    """Premium subscription plans"""

    name = models.CharField(max_length=100)
    plan_type = models.CharField(
        max_length=30, choices=SubscriptionPlanType.choices, unique=True
    )

    # Features
    max_resolution = models.CharField(max_length=10, default="1440p")
    ad_free = models.BooleanField(default=True)
    premium_content_access = models.BooleanField(default=True)
    early_access = models.BooleanField(default=False)

    # Pricing (in USD cents to avoid decimal issues)
    price_monthly_cents = models.IntegerField(validators=[MinValueValidator(0)])
    price_annual_cents = models.IntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )

    # Display pricing (for different currencies)
    display_currency = models.CharField(max_length=3, default="USD")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription_plans"
        ordering = ["price_monthly_cents"]

    def __str__(self):
        return f"{self.name} - {self.plan_type}"


class UserSubscription(models.Model):
    """User's active subscription"""

    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="active_subscription"
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions"
    )

    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )

    # Billing
    payment_gateway = models.CharField(max_length=20, choices=PaymentGateway.choices)
    gateway_subscription_id = models.CharField(max_length=255, blank=True)
    gateway_customer_id = models.CharField(max_length=255, blank=True)

    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    renewal_date = models.DateTimeField()

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # Grace period for payment failures
    grace_period_ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "renewal_date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_active(self):
        now = timezone.now()
        if self.status == SubscriptionStatus.ACTIVE:
            return True
        if self.status == SubscriptionStatus.GRACE_PERIOD and self.grace_period_ends_at:
            return now < self.grace_period_ends_at
        return False


class PaymentTransaction(models.Model):
    """Payment transaction history"""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="payment_transactions"
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    # Gateway details
    payment_gateway = models.CharField(max_length=20, choices=PaymentGateway.choices)
    gateway_transaction_id = models.CharField(max_length=255, unique=True)

    # Amount
    amount_cents = models.IntegerField()
    currency = models.CharField(max_length=3, default="USD")

    # Status
    status = models.CharField(
        max_length=20, default="pending"
    )  # pending, completed, failed, refunded

    # Metadata
    payment_method = models.CharField(
        max_length=50, blank=True
    )  # card, mobile_banking, etc.
    failure_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payment_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["gateway_transaction_id"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.amount_cents/100} {self.currency}"


class PromotionalCode(models.Model):
    """Discount/promotional codes"""

    code = models.CharField(max_length=50, unique=True, db_index=True)

    # Discount
    discount_type = models.CharField(
        max_length=20, choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")]
    )
    discount_value = models.IntegerField(
        help_text="Percentage (0-100) or fixed amount in cents"
    )

    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    # Usage limits
    max_uses = models.IntegerField(null=True, blank=True)
    max_uses_per_user = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)

    # Restrictions
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan, blank=True, related_name="promotional_codes"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "promotional_codes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        return True


class PromoCodeUsage(models.Model):
    """Track promo code usage"""

    promo_code = models.ForeignKey(
        PromotionalCode, on_delete=models.CASCADE, related_name="usages"
    )
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="promo_code_usages"
    )
    transaction = models.ForeignKey(
        PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True
    )

    discount_applied_cents = models.IntegerField()

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "promo_code_usages"
        ordering = ["-used_at"]
        indexes = [
            models.Index(fields=["promo_code", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username} used {self.promo_code.code}"
