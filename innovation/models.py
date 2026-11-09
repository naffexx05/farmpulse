from django.db import models
from decimal import Decimal
from farms.models import Farm, Crop


class SatelliteParcel(models.Model):
    """
    Cadastral field polygon mapped to Sentinel-2 multi-spectral Earth Observation bands.
    """
    STRESS_CHOICES = [
        ('optimal', 'Optimal Canopy Vigor (NDVI > 0.60)'),
        ('moderate_stress', 'Moderate Chlorophyll / Moisture Stress (NDVI 0.35–0.60)'),
        ('severe_stress', 'Severe Drought / Lodging Anomaly (NDVI < 0.35)'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='satellite_parcels')
    name = models.CharField(max_length=120, default="Primary Cropping Parcel")
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    polygon_geojson = models.JSONField(help_text="GeoJSON Polygon coordinates [[lng, lat], ...]")
    centroid_lat = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('-13.962612'))
    centroid_lng = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal('33.774119'))
    calculated_area_ha = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('2.50'))

    # Earth Observation Telemetry
    mean_ndvi = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.64'), help_text="Normalized Difference Vegetation Index (0.0 to 1.0)")
    soil_moisture_pct = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal('27.5'), help_text="Volumetric 0-5cm topsoil moisture percentage")
    stress_level = models.CharField(max_length=30, choices=STRESS_CHOICES, default='optimal')
    last_satellite_pass = models.DateField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.calculated_area_ha} ha) — NDVI {self.mean_ndvi}"


class ParametricInsurancePolicy(models.Model):
    """
    Zero-adjuster, satellite rainfall-triggered smart micro-insurance policy.
    """
    STATUS_CHOICES = [
        ('active', 'Active Coverage'),
        ('triggered', 'Drought Triggered — Payout Dispatched'),
        ('matured', 'Matured (Normal Rainfall)'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='insurance_policies')
    policy_number = models.CharField(max_length=40, unique=True)
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT)
    coverage_ha = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('2.00'))
    sum_insured_mwk = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('400000.00'))
    premium_mwk = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('28000.00'))

    # Parametric Trigger Definition
    trigger_dry_spell_days = models.PositiveSmallIntegerField(default=14, help_text="Consecutive dry days (< 1.5mm rain) required to trigger auto-payout")
    trigger_window_start = models.DateField()
    trigger_window_end = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    observed_dry_spell_days = models.PositiveSmallIntegerField(default=6)
    payout_mwk = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    mobile_money_provider = models.CharField(max_length=40, default="Airtel Money")
    payout_recipient_phone = models.CharField(max_length=30, default="+265 99 123 4567")
    transaction_ref = models.CharField(max_length=80, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parametric Insurance Policy"
        verbose_name_plural = "Parametric Insurance Policies"
        ordering = ['-created_at']

    def __str__(self):
        return f"Policy {self.policy_number} — {self.crop.name} ({self.get_status_display()})"
