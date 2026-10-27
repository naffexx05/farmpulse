from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    # Module 1: Farm & Crop
    path('my-farm/', views.my_farm, name='my_farm'),
    path('my-farm/edit/', views.farm_edit, name='farm_edit'),

    # Module 2: Farm History
    path('farm-history/', views.farm_history, name='farm_history'),
    path('farm-history/seasons/new/', views.season_create, name='season_create'),
    path('farm-history/seasons/<int:pk>/edit/', views.season_edit, name='season_edit'),
    path('farm-history/seasons/<int:pk>/delete/', views.season_delete, name='season_delete'),
    path('farm-history/plantings/new/', views.planting_create, name='planting_create'),
    path('farm-history/plantings/<int:pk>/edit/', views.planting_edit, name='planting_edit'),
    path('farm-history/plantings/<int:pk>/delete/', views.planting_delete, name='planting_delete'),
]
