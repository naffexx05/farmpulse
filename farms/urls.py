from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    path('my-farm/', views.my_farm, name='my_farm'),
    path('my-farm/edit/', views.farm_edit, name='farm_edit'),
]