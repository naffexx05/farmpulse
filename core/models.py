from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    User settings, display preferences, and regional units for FarmPulse.
    """
    LAND_UNIT_CHOICES = [
        ('ha', 'Hectares (ha)'),
        ('acre', 'Acres (ac)'),
    ]
    YIELD_UNIT_CHOICES = [
        ('kg', 'Kilograms (kg)'),
        ('bag_50kg', '50 kg Bags'),
    ]
    CURRENCY_FORMAT_CHOICES = [
        ('standard', 'MWK 1,250,000 (Standard)'),
        ('compact', 'MWK 1.25M (Compact)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=30, blank=True)
    preferred_district = models.CharField(max_length=80, default="Lilongwe", blank=True)

    # Units & Display
    land_unit = models.CharField(max_length=10, choices=LAND_UNIT_CHOICES, default='ha')
    yield_unit = models.CharField(max_length=10, choices=YIELD_UNIT_CHOICES, default='kg')
    currency_format = models.CharField(max_length=20, choices=CURRENCY_FORMAT_CHOICES, default='standard')

    # Data & Privacy
    share_anonymous_benchmarks = models.BooleanField(
        default=True,
        help_text="Contribute anonymized yield observations to national agricultural indices."
    )
    receive_sms_alerts = models.BooleanField(
        default=False,
        help_text="Receive extreme weather and market price threshold notifications."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


def get_user_profile(user):
    """Safe helper to retrieve or create UserProfile."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile
