from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('dev/design-preview/', core_views.design_preview, name='design_preview'),
    path('', include('farms.urls')),
    path('', include('climate.urls')),
]