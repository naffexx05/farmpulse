from django.contrib import admin
from .models import UserProfile

admin.site.site_header = "FarmPulse Malawi — Central Administration"
admin.site.site_title = "FarmPulse Admin Portal"
admin.site.index_title = "National Agricultural Intelligence & Operations Governance"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'phone_number', 'preferred_district',
        'land_unit', 'yield_unit', 'receive_sms_alerts',
        'share_anonymous_benchmarks', 'created_at',
    )
    list_filter = ('preferred_district', 'receive_sms_alerts', 'share_anonymous_benchmarks', 'land_unit')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
