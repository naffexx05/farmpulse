from decimal import Decimal
from django.db import models


class District(models.Model):
    """Malawian district administrative and agro-ecological boundary."""

    REGION_CHOICES = [
        ('northern', 'Northern Region'),
        ('central', 'Central Region'),
        ('southern', 'Southern Region'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='central')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    elevation_m = models.PositiveIntegerField(null=True, blank=True, help_text="Average elevation in metres above sea level.")
    description = models.TextField(blank=True, help_text="Agro-ecological zone characteristics, soil dynamics, and rainfall regime.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_region_display()})"


class ClimateSource(models.Model):
    """Provenance and metadata for climate datasets."""

    SOURCE_TYPES = [
        ('historical_observed', 'Historical Observations'),
        ('seasonal_outlook', 'Official Seasonal Outlook'),
        ('illustrative_scenario', 'Illustrative Scenario'),
    ]

    name = models.CharField(max_length=150, unique=True)
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPES, default='historical_observed')
    attribution = models.TextField(help_text="Institutional attribution and source methodology.")
    citation_url = models.URLField(blank=True)
    is_synthetic = models.BooleanField(
        default=True,
        help_text="Clearly distinguishes synthetic calibrated demo data from live certified meteorological feeds."
    )
    last_updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        synthetic_flag = " [Synthetic]" if self.is_synthetic else " [Certified]"
        return f"{self.name}{synthetic_flag}"


class ClimateRecord(models.Model):
    """
    Monthly aggregated historical or projected climate record for a district.
    Captures rainfall, temperature, dry spells, and heat wave episodes.
    """

    RECORD_TYPES = [
        ('historical', 'Historical Observation'),
        ('outlook', 'Official Seasonal Outlook'),
        ('scenario', 'Illustrative Scenario'),
    ]

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='climate_records')
    source = models.ForeignKey(ClimateSource, on_delete=models.PROTECT, related_name='climate_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='historical')

    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField(help_text="Month number (1-12)")

    # Rainfall parameters
    rainfall_mm = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        help_text="Total monthly precipitation in millimetres."
    )
    rainfall_days = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Number of days in month with >= 1.0mm rainfall."
    )
    dry_spell_days_max = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Longest consecutive sequence of dry days during the month."
    )

    # Temperature parameters
    temp_min_c = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Monthly average daily minimum temperature in °C."
    )
    temp_mean_c = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Monthly mean temperature in °C."
    )
    temp_max_c = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Monthly average daily maximum temperature in °C."
    )

    # Extreme heat metrics
    heat_wave_days = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of days exceeding extreme heat threshold (e.g. >= 33°C)."
    )
    heat_wave_events = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of sustained extreme heat episodes (>= 3 consecutive heat days)."
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', 'month']
        unique_together = ('district', 'year', 'month', 'record_type')

    def __str__(self):
        return f"{self.district.name} — {self.year}-{self.month:02d} ({self.get_record_type_display()})"



class WeatherStation(models.Model):
    """
    Physical Automated Weather Station (AWS) or virtual agrometeorological grid telemetry point.
    """
    STATION_TYPES = [
        ('dccms_aws', 'DCCMS Automated Station (AWS)'),
        ('open_meteo', 'High-Resolution Numerical Grid (Open-Meteo/ECMWF)'),
        ('research_station', 'National Agro-Research Station (Chitedze/Bvumbwe)'),
    ]

    station_id = models.CharField(max_length=60, unique=True, help_text="e.g. DCCMS-CHITEDZE-01")
    name = models.CharField(max_length=140)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='stations')
    station_type = models.CharField(max_length=40, choices=STATION_TYPES, default='dccms_aws')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    elevation_m = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    hardware_notes = models.TextField(blank=True, help_text="Telemetry sensor model, telemetry protocol, maintenance notes.")
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Timestamp of last successful live API ingestion.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.station_id}) — {self.district.name}"


class DailyWeatherObservation(models.Model):
    """
    Ground-truth daily observed readings recorded by the station's physical sensors.
    """
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, related_name='observations')
    date = models.DateField(db_index=True)

    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    temp_max_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    temp_min_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    temp_mean_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    relative_humidity_pct = models.PositiveSmallIntegerField(null=True, blank=True)
    solar_radiation_mj = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_speed_kmh = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    is_verified = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('station', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.station.name} — {self.date} ({self.rainfall_mm}mm, {self.temp_max_c}°C)"


class WeatherForecast(models.Model):
    """
    Rolling 7-to-14 day forecast emitted by Numerical Weather Prediction (NWP) model runs.
    """
    CONDITION_CHOICES = [
        ('sunny', 'Clear / Sunny'),
        ('partly_cloudy', 'Partly Cloudy'),
        ('overcast', 'Overcast'),
        ('isolated_showers', 'Isolated Light Showers'),
        ('heavy_rain', 'Heavy Rain / Thunderstorms'),
        ('dry_spell', 'Dry Spell Condition'),
    ]

    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, related_name='forecasts')
    target_date = models.DateField(db_index=True)
    issued_at = models.DateTimeField(auto_now=True)

    expected_rain_mm = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    rain_probability_pct = models.PositiveSmallIntegerField(default=0, help_text="Probability of precipitation 0–100%")
    temp_max_c = models.DecimalField(max_digits=4, decimal_places=1)
    temp_min_c = models.DecimalField(max_digits=4, decimal_places=1)
    condition_code = models.CharField(max_length=40, choices=CONDITION_CHOICES, default='partly_cloudy')
    wind_speed_max_kmh = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('station', 'target_date')
        ordering = ['target_date']

    def __str__(self):
        return f"{self.station.name} Forecast: {self.target_date} ({self.expected_rain_mm}mm, {self.rain_probability_pct}%)"
