from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    # Module 5: Crop Planner
    path('planner/', views.planner_input, name='planner_input'),
    path('planner/result/', views.planner_result, name='planner_result'),
    path('planner/save/', views.save_plan, name='save_plan'),

    # Module 5: Game-like Scenario Simulator 🎮
    path('scenarios/', views.scenario_simulator, name='scenario_simulator'),
    path('scenarios/simulate-api/', views.simulate_scenario_api, name='simulate_scenario_api'),

    # Module 6: My Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/compare/', views.plan_compare, name='plan_compare'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:pk>/duplicate/', views.plan_duplicate, name='plan_duplicate'),
    path('plans/<int:pk>/export-csv/', views.plan_export_csv, name='plan_export_csv'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='plan_delete'),
]
