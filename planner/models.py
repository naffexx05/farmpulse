from django.db import models


class Plan(models.Model):
    """A strategic seasonal crop and resource allocation plan for a farm."""

    STRATEGY_CHOICES = [
        ('balanced', 'Balanced Portfolio'),
        ('return_focused', 'Return-Focused Strategy'),
        ('risk_conscious', 'Risk-Conscious / Food Security'),
        ('custom', 'Custom Field Split'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active Planned'),
        ('completed', 'Completed'),
    ]

    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=140, default="New Seasonal Plan")
    strategy_type = models.CharField(max_length=30, choices=STRATEGY_CHOICES, default='balanced')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    total_land_ha = models.DecimalField(max_digits=7, decimal_places=2)
    total_budget_mwk = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    total_expected_cost_mwk = models.DecimalField(max_digits=12, decimal_places=2)
    total_expected_revenue_mwk = models.DecimalField(max_digits=12, decimal_places=2)
    total_expected_margin_mwk = models.DecimalField(max_digits=12, decimal_places=2)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_strategy_type_display()}) — {self.farm.name}"


class PlanItem(models.Model):
    """One crop allocation within a seasonal plan."""

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='items')
    crop = models.ForeignKey('farms.Crop', on_delete=models.PROTECT, related_name='plan_items')

    area_ha = models.DecimalField(max_digits=7, decimal_places=2)
    expected_yield_kg_per_ha = models.DecimalField(max_digits=10, decimal_places=2)
    expected_yield_kg_total = models.DecimalField(max_digits=10, decimal_places=2)

    expected_cost_per_ha_mwk = models.DecimalField(max_digits=12, decimal_places=2)
    expected_total_cost_mwk = models.DecimalField(max_digits=12, decimal_places=2)

    expected_selling_price_mwk_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    expected_revenue_mwk = models.DecimalField(max_digits=12, decimal_places=2)
    expected_gross_margin_mwk = models.DecimalField(max_digits=12, decimal_places=2)

    # Star Metric from Brief: "At what price per kg does this crop stop losing money?"
    break_even_price_mwk_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Break-even price per kg = Expected Cost / Expected Yield."
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['crop__name']

    def __str__(self):
        return f"{self.crop.name} — {self.area_ha} ha in {self.plan.name}"


class PlanAssumption(models.Model):
    """Transparent assumptions underlying every figure in a plan."""

    CATEGORY_CHOICES = [
        ('price', 'Commodity Price'),
        ('yield', 'Yield Projection'),
        ('cost', 'Input Expenditure'),
        ('climate', 'Climate / Water'),
    ]

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='assumptions')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='price')
    parameter_name = models.CharField(max_length=120)
    value_used = models.CharField(max_length=120)
    source_note = models.CharField(max_length=200)

    class Meta:
        ordering = ['category', 'parameter_name']

    def __str__(self):
        return f"{self.parameter_name}: {self.value_used} ({self.source_note})"
