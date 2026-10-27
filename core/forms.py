from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserAccountForm(forms.ModelForm):
    """Personal identity and contact details."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'Given name'}),
            'last_name': forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'Family name'}),
            'email': forms.EmailInput(attrs={'class': 'fp-input', 'placeholder': 'agronomist@farmpulse.mw'}),
        }


class UserProfileForm(forms.ModelForm):
    """Agronomic units, regional defaults, and privacy preferences."""
    class Meta:
        model = UserProfile
        fields = [
            'phone_number',
            'preferred_district',
            'land_unit',
            'yield_unit',
            'currency_format',
            'share_anonymous_benchmarks',
            'receive_sms_alerts',
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'fp-input', 'placeholder': '+265 99 123 4567'}),
            'preferred_district': forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'e.g. Lilongwe, Kasungu, Salima'}),
            'land_unit': forms.Select(attrs={'class': 'fp-input'}),
            'yield_unit': forms.Select(attrs={'class': 'fp-input'}),
            'currency_format': forms.Select(attrs={'class': 'fp-input'}),
            'share_anonymous_benchmarks': forms.CheckboxInput(attrs={'class': 'rounded border-earth-border text-leaf focus:ring-leaf'}),
            'receive_sms_alerts': forms.CheckboxInput(attrs={'class': 'rounded border-earth-border text-leaf focus:ring-leaf'}),
        }
