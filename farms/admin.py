from django.contrib import admin
from .models import Crop, Farm, Season, Planting, SeasonReview


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'typical_cycle_days', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'scientific_name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'location_description',
        'total_land_ha', 'irrigation_type', 'soil_type',
    )
    list_filter = ('irrigation_type', 'soil_type')
    search_fields = ('name', 'location_description', 'owner__username')
    filter_horizontal = ('preferred_crops',)
    readonly_fields = ('created_at', 'updated_at')


class PlantingInline(admin.TabularInline):
    model = Planting
    extra = 0
    fields = (
        'crop', 'area_ha',
        'planting_date', 'harvest_date',
        'yield_kg', 'production_cost_mwk', 'revenue_mwk',
    )


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'start_date', 'end_date', 'planting_count')
    list_filter = ('start_date',)
    search_fields = ('name', 'farm__name')
    date_hierarchy = 'start_date'
    inlines = [PlantingInline]

    def planting_count(self, obj):
        return obj.plantings.count()
    planting_count.short_description = 'Plantings'


@admin.register(Planting)
class PlantingAdmin(admin.ModelAdmin):
    list_display = (
        'crop', 'season', 'area_ha',
        'yield_kg', 'revenue_mwk', 'gross_margin_display',
    )
    list_filter = ('crop', 'season')
    search_fields = ('crop__name', 'season__name', 'season__farm__name')

    def gross_margin_display(self, obj):
        gm = obj.gross_margin_mwk
        if gm is None:
            return '—'
        return f'{gm:,.2f}'
    gross_margin_display.short_description = 'Gross margin (MWK)'


@admin.register(SeasonReview)
class SeasonReviewAdmin(admin.ModelAdmin):
    list_display = ('season', 'associated_plan', 'overall_satisfaction', 'created_at')
    list_filter = ('overall_satisfaction',)
    search_fields = ('season__name', 'season__farm__name', 'lessons_learned')
