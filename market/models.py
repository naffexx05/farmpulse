from django.db import models


class MarketSource(models.Model):
    """Institutional data source for price, input, and logistics tracking."""

    name = models.CharField(max_length=150, unique=True)
    attribution = models.TextField(help_text="Survey methodology, frequency, and market coverage details.")
    citation_url = models.URLField(blank=True)
    is_synthetic = models.BooleanField(
        default=True,
        help_text="Flag indicating synthetic demonstration baseline versus live certified market feed."
    )
    last_updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        suffix = " [Synthetic]" if self.is_synthetic else " [Live]"
        return f"{self.name}{suffix}"


class CropPrice(models.Model):
    """
    Monthly price record for a crop with clear separation of market types:
    - Farmgate (Amber)
    - Wholesale (Green)
    - Retail (Blue)
    """

    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, related_name='market_prices')
    district = models.ForeignKey(
        'climate.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crop_prices',
        help_text="Leave blank for national benchmark average.",
    )
    source = models.ForeignKey(MarketSource, on_delete=models.PROTECT, related_name='crop_prices')

    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField(help_text="Month number 1–12")
    price_date = models.DateField(null=True, blank=True)

    # Three strictly distinguished price channels (MWK per kg)
    price_farmgate_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Farmgate price received directly by farmers at village aggregation."
    )
    price_wholesale_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Wholesale price traded at regional aggregation depots and urban markets."
    )
    price_retail_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Retail price paid by final consumer per kg."
    )

    market_name = models.CharField(max_length=120, blank=True, help_text="e.g. Mitundu, Mchesi, Lunzu")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month', 'crop__name']
        unique_together = ('crop', 'district', 'year', 'month')

    def __str__(self):
        dist_str = f" ({self.district.name})" if self.district else " (National)"
        return f"{self.crop.name} — {self.year}-{self.month:02d}{dist_str}"

    @property
    def wholesale_spread_mwk(self):
        """Wholesale markup over farmgate."""
        if self.price_wholesale_mwk is not None and self.price_farmgate_mwk is not None:
            return self.price_wholesale_mwk - self.price_farmgate_mwk
        return None

    @property
    def retail_spread_mwk(self):
        """Retail markup over farmgate."""
        if self.price_retail_mwk is not None and self.price_farmgate_mwk is not None:
            return self.price_retail_mwk - self.price_farmgate_mwk
        return None


class InputCost(models.Model):
    """Itemized agronomic input and operational cost benchmark per hectare."""

    CATEGORY_CHOICES = [
        ('seed', 'Certified Seed'),
        ('fertilizer_basal', 'Basal Fertiliser (NPK)'),
        ('fertilizer_top', 'Top Dressing (Urea)'),
        ('chemical', 'Agrochemicals / Protection'),
        ('labour', 'Field Labour & Land Prep'),
        ('other', 'Other Operational Inputs'),
    ]

    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, related_name='input_costs')
    source = models.ForeignKey(MarketSource, on_delete=models.PROTECT, related_name='input_costs')
    year = models.PositiveIntegerField(default=2024)

    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default='other')
    item_name = models.CharField(max_length=120, help_text="e.g. Hybrid Maize SC403 10kg, Urea 50kg bag")
    unit = models.CharField(max_length=50, help_text="e.g. 50 kg bag, 10 kg pocket, man-days, litre")
    cost_per_unit_mwk = models.DecimalField(max_digits=10, decimal_places=2)
    units_per_ha_recommended = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Standard recommended agronomic application rate per hectare."
    )
    cost_per_ha_mwk = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Total calculated cost per hectare."
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['crop__name', 'category', 'item_name']

    def __str__(self):
        return f"{self.crop.name} — {self.item_name} ({self.cost_per_ha_mwk:,.0f} MWK/ha)"


class TransportCost(models.Model):
    """Logistical transport freight rate from farming zones to wholesale markets."""

    ROAD_CONDITIONS = [
        ('good_tarred', 'Tarred / Paved Highway'),
        ('seasonal_earth', 'Seasonal Earth / Feeder Road'),
        ('rough_track', 'Unpaved / Mountainous Track'),
    ]

    from_location = models.CharField(max_length=120, help_text="e.g. Rural Farmgate, Lilongwe West")
    to_market = models.CharField(max_length=120, help_text="e.g. Lilongwe Wholesale Market, Blantyre Hub")
    distance_km = models.PositiveIntegerField(null=True, blank=True)
    cost_per_50kg_bag_mwk = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Standard tariff per 50 kg bag in MWK."
    )
    cost_per_ton_km_mwk = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Freight rate per metric ton per kilometre."
    )
    road_condition = models.CharField(max_length=20, choices=ROAD_CONDITIONS, default='seasonal_earth')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['from_location', 'to_market']

    def __str__(self):
        return f"{self.from_location} &rarr; {self.to_market} ({self.cost_per_50kg_bag_mwk:,.0f} MWK/bag)"
