from django.contrib import admin
from .models import SeasonJourney, FarmActivityLog, JourneyCheckIn, HarvestRecord


@admin.register(SeasonJourney)
class SeasonJourneyAdmin(admin.ModelAdmin):
    list_display = ('farm', 'season_label', 'status', 'activated_at', 'plan')
    list_filter = ('status', 'season_label')
    search_fields = ('farm__name',)
    date_hierarchy = 'activated_at'


@admin.register(FarmActivityLog)
class FarmActivityLogAdmin(admin.ModelAdmin):
    list_display = ('farm', 'category', 'activity_date', 'description', 'amount_mwk', 'is_income')
    list_filter = ('category', 'is_income', 'activity_date')
    search_fields = ('farm__name', 'description', 'product_name')
    date_hierarchy = 'activity_date'


@admin.register(JourneyCheckIn)
class JourneyCheckInAdmin(admin.ModelAdmin):
    list_display = ('journey', 'week_number', 'stage', 'pest_pressure', 'moisture_score', 'checked_in_at')
    list_filter = ('stage', 'pest_pressure', 'disease_pressure')
    search_fields = ('journey__farm__name',)


@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ('journey', 'crop', 'actual_area_ha', 'actual_yield_kg', 'bags_50kg', 'actual_revenue_mwk', 'harvested_at')
    list_filter = ('crop', 'harvested_at')
    search_fields = ('journey__farm__name', 'crop__name')
