from django.contrib import admin
from .models import Plan, PlanItem, PlanAssumption


class PlanItemInline(admin.TabularInline):
    model = PlanItem
    extra = 0
    fields = (
        'crop', 'area_ha', 'expected_yield_kg_total',
        'expected_total_cost_mwk', 'expected_revenue_mwk',
        'expected_gross_margin_mwk', 'break_even_price_mwk_per_kg'
    )


class PlanAssumptionInline(admin.TabularInline):
    model = PlanAssumption
    extra = 0


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'farm', 'strategy_type', 'status',
        'total_land_ha', 'total_expected_cost_mwk',
        'total_expected_revenue_mwk', 'total_expected_margin_mwk'
    )
    list_filter = ('strategy_type', 'status')
    search_fields = ('name', 'farm__name')
    inlines = [PlanItemInline, PlanAssumptionInline]


@admin.register(PlanItem)
class PlanItemAdmin(admin.ModelAdmin):
    list_display = (
        'crop', 'plan', 'area_ha', 'expected_total_cost_mwk',
        'expected_revenue_mwk', 'expected_gross_margin_mwk',
        'break_even_price_mwk_per_kg'
    )
    list_filter = ('crop',)
