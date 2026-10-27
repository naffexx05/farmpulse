from django.urls import path
from . import views

app_name = 'innovation'

urlpatterns = [
    path('innovation/', views.innovation_hub, name='hub'),
    path('satellite/', views.satellite_twin, name='satellite_twin'),
    path('ussd/', views.ussd_simulator, name='ussd_simulator'),
    path('ussd/api/', views.ussd_api, name='ussd_api'),
    path('insurance/', views.parametric_insurance, name='parametric_insurance'),
    path('advisor/', views.mlimi_advisor, name='mlimi_advisor'),
]
