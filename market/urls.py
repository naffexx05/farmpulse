from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('market/', views.market_dashboard, name='dashboard'),
    path('market/hubs/<str:hub_id>/sync/', views.sync_market_hub, name='sync_market_hub'),
    path('market/ticker/', views.ticker_api, name='ticker_api'),
]
