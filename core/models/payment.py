from django.db import models
from django.core.validators import MinValueValidator
from .choices import PayoutStatus


class CreatorPayout(models.Model):
    """Creator revenue payouts"""

    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="payouts"
    )

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Revenue breakdown (in cents)
    ad_revenue_cents = models.IntegerField(default=0)
    premium_revenue_cents = models.IntegerField(default=0)
    total_revenue_cents = models.IntegerField(default=0)

    # Fees & Net
    platform_fee_cents = models.IntegerField(default=0)
    payment_gateway_fee_cents = models.IntegerField(default=0)
    tax_withheld_cents = models.IntegerField(default=0)

    net_payout_cents = models.IntegerField(default=0)

    # Currency
    currency = models.CharField(max_length=3, default="USD")

    # Status
    status = models.CharField(
        max_length=20, choices=PayoutStatus.choices, default=PayoutStatus.PENDING
    )

    # Payment details
    payment_method = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        db_table = "creator_payouts"
        ordering = ["-period_end", "-created_at"]
        unique_together = [["channel", "period_start", "period_end"]]
        indexes = [
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.channel.name} - {self.period_start} to {self.period_end}"

    @property
    def payout_amount_display(self):
        return f"{self.currency} {self.net_payout_cents / 100:.2f}"


class RevenueShare(models.Model):
    """Track revenue attribution per video"""

    video = models.ForeignKey(
        "Video", on_delete=models.CASCADE, related_name="revenue_shares"
    )
    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="revenue_shares"
    )

    # Date
    date = models.DateField(db_index=True)

    # Metrics
    ad_impressions = models.IntegerField(default=0)
    ad_revenue_cents = models.IntegerField(default=0)

    premium_views = models.IntegerField(default=0)
    premium_revenue_cents = models.IntegerField(default=0)

    total_revenue_cents = models.IntegerField(default=0)

    # Creator share (70% default)
    creator_share_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=70.00, validators=[MinValueValidator(0)]
    )
    creator_revenue_cents = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "revenue_shares"
        ordering = ["-date"]
        unique_together = [["video", "date"]]
        indexes = [
            models.Index(fields=["channel", "date"]),
            models.Index(fields=["video", "date"]),
        ]

    def __str__(self):
        return f"{self.video.title} - {self.date}"


class PayoutMethod(models.Model):
    """Creator payout method configuration"""

    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="payout_methods"
    )

    method_type = models.CharField(
        max_length=50,
        choices=[
            ("bank_transfer", "Bank Transfer"),
            ("paypal", "PayPal"),
            ("mobile_banking", "Mobile Banking"),
        ],
    )

    # Encrypted account details (should be encrypted at application level)
    account_details = models.JSONField(help_text="Encrypted account information")

    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payout_methods"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.channel.name} - {self.method_type}"
