from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from core import views as core_views
from core import auth_views

def sw_js(request):
    return HttpResponse('', content_type='application/javascript')

account_patterns = ([
    path('login/', auth_views.user_login, name='login'),
    path('register/', auth_views.user_register, name='register'),
    path('logout/', auth_views.user_logout, name='logout'),
    path('password-reset/', auth_views.user_password_reset, name='password_reset'),
], 'accounts')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', sw_js, name='sw_js'),
    path('', core_views.home, name='home'),
    path('dev/design-preview/', core_views.design_preview, name='design_preview'),
    path('settings/', core_views.settings_index, name='settings_index'),
    path('settings/export/', core_views.export_user_data, name='export_user_data'),
    path('search/', core_views.search_global, name='search_global'),
    path('admin-portal/', core_views.admin_portal, name='admin_portal'),
    path('accounts/', include(account_patterns)),
    path('', include('farms.urls')),
    path('', include('climate.urls')),
    path('', include('market.urls')),
    path('', include('planner.urls')),
    path('', include('innovation.urls')),
    path('journey/', include('journey.urls', namespace='journey')),
]
