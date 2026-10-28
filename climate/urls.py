from django.urls import path
from . import views

app_name = 'climate'

urlpatterns = [
    path('climate/', views.climate_dashboard, name='dashboard'),
    path('climate/stations/<str:station_id>/sync/', views.sync_station_forecast, name='sync_station_forecast'),
]
