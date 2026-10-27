from django.db import models


class Crop(models.Model):
    """A crop that can be planned or tracked. Static reference data — not farm-specific."""

    CATEGORY_CHOICES = [
        ('cereal', 'Cereal'),
        ('legume', 'Legume'),
        ('cash_crop', 'Cash crop'),
        ('vegetable', 'Vegetable'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    scientific_name = models.CharField(max_length=120, blank=True)
    typical_cycle_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Rough indicative cycle length. Not authoritative.",
    )
    photo_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
class Farm(models.Model):
    """A farmer's farm — current facts about land, resources, and preferences."""

    IRRIGATION_CHOICES = [
        ('rainfed', 'Rain-fed'),
        ('borehole', 'Borehole'),
        ('river', 'River / stream'),
        ('canal', 'Canal'),
        ('drip', 'Drip irrigation'),
        ('mixed', 'Mixed'),
    ]

    SOIL_CHOICES = [
        ('unknown', 'Unknown'),
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loam', 'Loam'),
        ('silt', 'Silt'),
    ]

    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='farms',
    )
    name = models.CharField(max_length=120)
    location_description = models.CharField(
        max_length=200,
        help_text="e.g. Lilongwe District, Central Region",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    total_land_ha = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text="Total land the farm owns, in hectares.",
    )
    cultivated_land_ha = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text="Land actually cultivated this season, if different from total.",
    )

    irrigation_type = models.CharField(
        max_length=20, choices=IRRIGATION_CHOICES, default='rainfed',
    )
    water_notes = models.TextField(blank=True)

    soil_type = models.CharField(max_length=20, choices=SOIL_CHOICES, default='unknown')
    soil_notes = models.TextField(blank=True)

    seasonal_budget_mwk = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Available budget in Malawian Kwacha for the season.",
    )
    available_labour_persons = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="How many people are available to work the farm.",
    )
    labour_notes = models.TextField(blank=True)

    preferred_crops = models.ManyToManyField(Crop, blank=True, related_name='farms_preferring')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """Basic sanity check: cultivated cannot exceed total."""
        from django.core.exceptions import ValidationError
        if (
            self.cultivated_land_ha is not None
            and self.total_land_ha is not None
            and self.cultivated_land_ha > self.total_land_ha
        ):
            raise ValidationError({
                'cultivated_land_ha': 'Cultivated land cannot exceed total land.'
            })
class Season(models.Model):
    """A growing season on a farm — a container for one or more plantings."""

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(
        max_length=120,
        help_text="e.g. 2024/25 Rainy Season",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} — {self.farm.name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date must be on or after start date.'})


class Planting(models.Model):
    """One crop planted within a season — the atom of farm history."""

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='plantings')
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT, related_name='plantings')

    area_ha = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text="Land allocated to this crop, in hectares.",
    )
    planting_date = models.DateField(null=True, blank=True)
    harvest_date = models.DateField(null=True, blank=True)

    yield_kg = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Actual harvested weight. Leave blank if unknown.",
    )
    production_cost_mwk = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Total observed cost for this planting, in MWK.",
    )
    selling_price_mwk_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Average price received per kg, if known.",
    )
    revenue_mwk = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Actual total revenue received. Not necessarily yield × price.",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['season', 'crop__name']

    def __str__(self):
        return f"{self.crop.name} — {self.area_ha} ha ({self.season.name})"

    @property
    def gross_margin_mwk(self):
        """Computed, never stored. Returns None if either component is missing."""
        if self.revenue_mwk is None or self.production_cost_mwk is None:
            return None
        return self.revenue_mwk - self.production_cost_mwk

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if self.planting_date and self.harvest_date and self.harvest_date < self.planting_date:
            errors['harvest_date'] = 'Harvest date must be on or after planting date.'
        if errors:
            raise ValidationError(errors)