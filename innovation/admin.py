from django.contrib import admin
from .models import SatelliteParcel, ParametricInsurancePolicy


@admin.register(SatelliteParcel)
class SatelliteParcelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'farm', 'crop', 'calculated_area_ha',
        'mean_ndvi', 'soil_moisture_pct', 'stress_level',
        'last_satellite_pass',
    )
    list_filter = ('stress_level', 'crop', 'farm__irrigation_type')
    search_fields = ('name', 'farm__name', 'farm__owner__username')
    readonly_fields = ('created_at', 'last_satellite_pass')


@admin.register(ParametricInsurancePolicy)
class ParametricInsurancePolicyAdmin(admin.ModelAdmin):
    list_display = (
        'policy_number', 'farm', 'crop', 'coverage_ha',
        'sum_insured_mwk', 'premium_mwk', 'status',
        'observed_dry_spell_days', 'payout_mwk', 'mobile_money_provider',
    )
    list_filter = ('status', 'mobile_money_provider', 'crop')
    search_fields = ('policy_number', 'farm__name', 'farm__owner__username', 'transaction_ref')
    readonly_fields = ('created_at', 'updated_at')
