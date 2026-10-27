from django.contrib import admin
from .models import District, ClimateSource, ClimateRecord


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'elevation_m', 'latitude', 'longitude')
    list_filter = ('region',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ClimateSource)
class ClimateSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'is_synthetic', 'last_updated')
    list_filter = ('source_type', 'is_synthetic')
    search_fields = ('name', 'attribution')


@admin.register(ClimateRecord)
class ClimateRecordAdmin(admin.ModelAdmin):
    list_display = (
        'district', 'year', 'month', 'record_type',
        'rainfall_mm', 'temp_max_c', 'dry_spell_days_max', 'heat_wave_days',
    )
    list_filter = ('district', 'record_type', 'year')
    search_fields = ('district__name', 'notes')
    date_hierarchy = None
