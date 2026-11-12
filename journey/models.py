from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SeasonJourney(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    farm = models.ForeignKey(
        'farms.Farm', on_delete=models.CASCADE, related_name='journeys'
    )
    plan = models.ForeignKey(
        'planner.Plan', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='journeys'
    )
    season_label = models.CharField(max_length=20, default='2025/26')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    activated_at = models.DateTimeField(auto_now_add=True)
    expected_plant_date = models.DateField(null=True, blank=True)
    actual_plant_date = models.DateField(null=True, blank=True)
    expected_harvest_date = models.DateField(null=True, blank=True)
    actual_harvest_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-activated_at']
        verbose_name = 'Season Journey'
        verbose_name_plural = 'Season Journeys'

    def __str__(self):
        return f"{self.farm.name} - {self.season_label} Journey"

    @property
    def current_stage(self):
        latest = self.checkins.first()
        if latest:
            return latest.get_stage_display()
        return 'Land Preparation'

    @property
    def total_expenses(self):
        from django.db.models import Sum
        result = self.activities.filter(is_income=False).aggregate(total=Sum('amount_mwk'))
        return result['total'] or 0

    @property
    def total_income(self):
        from django.db.models import Sum
        result = self.activities.filter(is_income=True).aggregate(total=Sum('amount_mwk'))
        return result['total'] or 0

    @property
    def net_balance(self):
        return self.total_income - self.total_expenses

    @property
    def days_active(self):
        from django.utils import timezone
        delta = timezone.now() - self.activated_at
        return delta.days

    @property
    def week_number(self):
        return max(1, (self.days_active // 7) + 1)


class FarmActivityLog(models.Model):
    CATEGORY_CHOICES = [
        ('land_prep', 'Land Preparation'),
        ('input', 'Input Purchase'),
        ('planting', 'Planting'),
        ('management', 'Crop Management'),
        ('irrigation', 'Irrigation'),
        ('pest', 'Pest and Disease Control'),
        ('harvest', 'Harvest'),
        ('sale', 'Sale / Income'),
        ('labour', 'Labour Hire'),
        ('other', 'Other Expense'),
    ]

    farm = models.ForeignKey(
        'farms.Farm', on_delete=models.CASCADE, related_name='activity_logs'
    )
    journey = models.ForeignKey(
        SeasonJourney, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='activities'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    activity_date = models.DateField()
    description = models.CharField(max_length=255)
    amount_mwk = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_income = models.BooleanField(default=False)
    crop = models.ForeignKey(
        'farms.Crop', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='activity_logs'
    )
    area_ha = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=30, blank=True)
    product_name = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-activity_date', '-created_at']
        verbose_name = 'Farm Activity Log'
        verbose_name_plural = 'Farm Activity Logs'

    def __str__(self):
        return f"{self.farm.name} - {self.get_category_display()} on {self.activity_date}"


class JourneyCheckIn(models.Model):
    GROWTH_STAGES = [
        ('prep', 'Land Preparation'),
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative Growth'),
        ('flowering', 'Flowering / Silking'),
        ('grain_fill', 'Grain Fill / Pod Fill'),
        ('maturity', 'Maturity'),
        ('harvest', 'Harvest Ready'),
    ]
    PRESSURE_LEVELS = [
        ('none', 'None'),
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]

    journey = models.ForeignKey(
        SeasonJourney, on_delete=models.CASCADE, related_name='checkins'
    )
    week_number = models.PositiveIntegerField()
    stage = models.CharField(max_length=20, choices=GROWTH_STAGES, default='vegetative')
    pest_pressure = models.CharField(max_length=10, choices=PRESSURE_LEVELS, default='none')
    disease_pressure = models.CharField(max_length=10, choices=PRESSURE_LEVELS, default='none')
    moisture_score = models.PositiveSmallIntegerField(
        default=3, help_text='1=Very Dry, 2=Dry, 3=Adequate, 4=Moist, 5=Waterlogged'
    )
    canopy_cover_pct = models.PositiveSmallIntegerField(
        default=50, help_text='Estimated crop canopy coverage 0-100 percent'
    )
    advisory = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_number']
        verbose_name = 'Journey Check-In'
        verbose_name_plural = 'Journey Check-Ins'

    def __str__(self):
        return f"Week {self.week_number} check-in for {self.journey}"


class HarvestRecord(models.Model):
    journey = models.ForeignKey(
        SeasonJourney, on_delete=models.CASCADE, related_name='harvest_records'
    )
    crop = models.ForeignKey(
        'farms.Crop', on_delete=models.PROTECT, related_name='harvest_records'
    )
    actual_area_ha = models.DecimalField(max_digits=7, decimal_places=2)
    actual_yield_kg = models.DecimalField(max_digits=10, decimal_places=2)
    bags_50kg = models.PositiveIntegerField(default=0)
    selling_price_mwk = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_revenue_mwk = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    harvested_at = models.DateField()

    class Meta:
        ordering = ['-harvested_at']
        verbose_name = 'Harvest Record'
        verbose_name_plural = 'Harvest Records'

    def __str__(self):
        return f"{self.crop.name} harvest for {self.journey} on {self.harvested_at}"

    @property
    def yield_per_ha(self):
        if self.actual_area_ha:
            return float(self.actual_yield_kg) / float(self.actual_area_ha)
        return 0
