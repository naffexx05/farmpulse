from django.contrib import admin
from .models import District, ClimateSource, ClimateRecord, WeatherStation, DailyWeatherObservation, WeatherForecast


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



@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'station_id', 'district', 'station_type', 'is_active', 'last_sync')
    list_filter = ('district', 'station_type', 'is_active')
    search_fields = ('name', 'station_id')


@admin.register(DailyWeatherObservation)
class DailyWeatherObservationAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'rainfall_mm', 'temp_max_c', 'temp_min_c', 'is_verified')
    list_filter = ('station__district', 'date', 'is_verified')
    search_fields = ('station__name', 'date')
    date_hierarchy = 'date'


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ('station', 'target_date', 'expected_rain_mm', 'rain_probability_pct', 'temp_max_c', 'temp_min_c', 'condition_code')
    list_filter = ('station__district', 'condition_code', 'target_date')
    search_fields = ('station__name', 'target_date')
    date_hierarchy = 'target_date'
