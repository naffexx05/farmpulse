from django.contrib import admin
from .models import MarketSource, CropPrice, InputCost, TransportCost


@admin.register(MarketSource)
class MarketSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_synthetic', 'last_updated')
    list_filter = ('is_synthetic',)
    search_fields = ('name', 'attribution')


@admin.register(CropPrice)
class CropPriceAdmin(admin.ModelAdmin):
    list_display = (
        'crop', 'year', 'month', 'district',
        'price_farmgate_mwk', 'price_wholesale_mwk', 'price_retail_mwk',
        'wholesale_spread_mwk',
    )
    list_filter = ('crop', 'year', 'district')
    search_fields = ('crop__name', 'market_name', 'notes')


@admin.register(InputCost)
class InputCostAdmin(admin.ModelAdmin):
    list_display = (
        'crop', 'item_name', 'category',
        'cost_per_unit_mwk', 'units_per_ha_recommended', 'cost_per_ha_mwk',
    )
    list_filter = ('crop', 'category', 'year')
    search_fields = ('crop__name', 'item_name')


@admin.register(TransportCost)
class TransportCostAdmin(admin.ModelAdmin):
    list_display = (
        'from_location', 'to_market', 'distance_km',
        'cost_per_50kg_bag_mwk', 'road_condition',
    )
    list_filter = ('road_condition',)
    search_fields = ('from_location', 'to_market')
