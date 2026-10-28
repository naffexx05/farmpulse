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


class MarketHub(models.Model):
    """
    Physical agricultural commodity market hub, aggregation depot, or terminal trading center in Malawi.
    """
    HUB_TYPES = [
        ('rural_aggregation', 'Rural Aggregation & Assembly Depot (Primary Farmgate)'),
        ('urban_wholesale', 'Urban Wholesale & Processing Terminal (AMIS Regional Hub)'),
        ('cross_border', 'Strategic Cross-Border Market (Regional Trade Flow)'),
        ('commodity_exchange', 'Formal Commodity Exchange / Auction Floor (AHCX / Auction Floors)'),
    ]

    hub_id = models.CharField(max_length=60, unique=True, help_text="e.g. AMIS-LL-MITUNDU-01")
    name = models.CharField(max_length=140)
    district = models.ForeignKey('climate.District', on_delete=models.CASCADE, related_name='market_hubs')
    hub_type = models.CharField(max_length=40, choices=HUB_TYPES, default='rural_aggregation')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    primary_commodities = models.CharField(max_length=200, default='Maize, Soybeans, Groundnuts, Beans')
    operating_schedule = models.CharField(max_length=100, default='Daily Trading')
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Timestamp of last live price surveillance sync.")
    api_endpoint = models.URLField(blank=True, default='https://amis.agriculture.gov.mw/api/v1/live-feed')
    notes = models.TextField(blank=True, help_text="Trading capacity, road access, and major buyer profiles.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.hub_id}) — {self.district.name}"


class DailyMarketPrice(models.Model):
    """
    Ground-truth and daily surveillance price quote recorded at an agricultural trading hub.
    Captures farmgate, wholesale, and retail price tiers with trading volume and short-term trend.
    """
    TREND_CHOICES = [
        ('rising', 'Rising (High Demand / Lean Season)'),
        ('falling', 'Falling (Harvest Glut / High Supply)'),
        ('stable', 'Stable (Equilibrium)'),
    ]

    hub = models.ForeignKey(MarketHub, on_delete=models.CASCADE, related_name='daily_prices')
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, related_name='daily_market_prices')
    date = models.DateField(db_index=True)

    price_farmgate_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Direct village/aggregation purchase price paid to smallholder."
    )
    price_wholesale_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Wholesale price per kg for bulk bagged trade."
    )
    price_retail_mwk = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Urban or local consumer retail price per kg."
    )
    volume_traded_bags = models.PositiveIntegerField(
        default=0,
        help_text="Estimated 50kg bags transacted on market day."
    )
    price_trend = models.CharField(max_length=20, choices=TREND_CHOICES, default='stable')
    source_label = models.CharField(max_length=120, default='MoA AMIS Live Surveillance')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hub', 'crop', 'date')
        ordering = ['-date', 'crop__name']

    def __str__(self):
        return f"{self.hub.name} — {self.crop.name} ({self.date}): FG {self.price_farmgate_mwk} / WS {self.price_wholesale_mwk} MWK"

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


class MarketPriceForecast(models.Model):
    """
    Rolling 7-to-30 day price projection generated from seasonal price curves,
    crop production balances, and spatial market integration models.
    """
    TREND_CHOICES = [
        ('bullish', 'Bullish (+ Rising Price Expected)'),
        ('bearish', 'Bearish (- Softening Price Expected)'),
        ('sideways', 'Sideways (Stable Plateau Expected)'),
    ]

    hub = models.ForeignKey(MarketHub, on_delete=models.CASCADE, related_name='price_forecasts')
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, related_name='price_forecasts')
    target_date = models.DateField(db_index=True)
    horizon_days = models.PositiveIntegerField(help_text="Days ahead (e.g. 7, 14, 21, 30)")

    projected_farmgate_mwk = models.DecimalField(max_digits=10, decimal_places=2)
    projected_wholesale_mwk = models.DecimalField(max_digits=10, decimal_places=2)
    projected_retail_mwk = models.DecimalField(max_digits=10, decimal_places=2)

    confidence_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.85,
        help_text="Econometric statistical confidence level (0.00 - 1.00)."
    )
    trend_direction = models.CharField(max_length=20, choices=TREND_CHOICES, default='bullish')
    market_driver = models.CharField(
        max_length=250,
        help_text="Dominant market driver (e.g. Lean season depletion, commercial brewer demand, export border flows)."
    )
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hub', 'crop', 'target_date')
        ordering = ['target_date', 'crop__name']

    def __str__(self):
        return f"{self.hub.name} Forecast {self.crop.name} [{self.target_date} (+{self.horizon_days}d)]: FG {self.projected_farmgate_mwk} MWK"
