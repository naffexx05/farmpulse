from django.urls import path
from . import views

app_name = 'climate'

urlpatterns = [
    path('climate/', views.climate_dashboard, name='dashboard'),
]
