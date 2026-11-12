from django.urls import path
from . import views

app_name = 'journey'

urlpatterns = [
    path('', views.journey_list, name='journey_list'),
    path('activate/<int:plan_id>/', views.activate_journey, name='activate'),
    path('<int:pk>/', views.journey_detail, name='detail'),
    path('<int:pk>/log/', views.activity_log, name='activity_log'),
    path('<int:pk>/log/add/', views.add_activity, name='add_activity'),
    path('<int:pk>/checkin/', views.checkin, name='checkin'),
    path('<int:pk>/harvest/', views.log_harvest, name='harvest'),
    path('<int:pk>/review/', views.season_review, name='review'),
    path('log/<int:log_id>/delete/', views.delete_activity, name='delete_activity'),
]

