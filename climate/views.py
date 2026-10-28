import json
import statistics
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from farms.models import Farm
from .models import District, ClimateSource, ClimateRecord, WeatherStation, DailyWeatherObservation, WeatherForecast
from .risk import calculate_climate_risks
from .services import analyze_forecast_dry_spells, fetch_live_forecast_for_station


@login_required
def climate_dashboard(request):
    """
    Climate Intelligence Dashboard with 3 tabs:
    - Rainfall (Annual totals, monthly curve, dry spell risk)
    - Temperature (20-year trends, seasonal max/mean/min)
    - Heat Events (Frequency, duration, and thermal stress)
    Includes multi-district switching, risk scoring engine, and data attribution.
    """
    districts = District.objects.all().order_by('name')

    # Determine active district (from query param, user's farm, or default to Lilongwe)
    district_slug = request.GET.get('district')
    active_district = None

    if district_slug:
        active_district = District.objects.filter(slug=district_slug).first()

    if not active_district:
        # Check if user has a farm in a known district
        farm = Farm.objects.filter(owner=request.user).first()
        if farm and farm.location_description:
            for d in districts:
                if d.name.lower() in farm.location_description.lower():
                    active_district = d
                    break

    if not active_district:
        active_district = District.objects.filter(slug='lilongwe').first() or districts.first()

    # Sources
    sources = ClimateSource.objects.all()

    # Active Station & Live Telemetry for this District
    stations = WeatherStation.objects.filter(district=active_district, is_active=True)
    if not stations.exists():
        stations = WeatherStation.objects.filter(is_active=True)

    station_id_param = request.GET.get('station')
    active_station = None
    if station_id_param:
        active_station = WeatherStation.objects.filter(station_id=station_id_param).first()
    if not active_station:
        active_station = stations.first() or WeatherStation.objects.first()

    today = timezone.now().date()
    forecasts = []
    forecast_insights = {'max_dry_streak': 0, 'rainy_days': 0, 'total_rain_mm': Decimal('0.0'), 'advisory': 'Normal conditions', 'level': 'normal'}
    recent_observations = []

    if active_station:
        forecasts = list(active_station.forecasts.filter(target_date__gte=today).order_by('target_date')[:14])
        if not forecasts:
            # Auto-ingest if empty
            fetch_live_forecast_for_station(active_station)
            forecasts = list(active_station.forecasts.filter(target_date__gte=today).order_by('target_date')[:14])
        forecast_insights = analyze_forecast_dry_spells(forecasts)
        recent_observations = list(active_station.observations.order_by('-date')[:7])

    # Query records for active district
    hist_records = list(active_district.climate_records.filter(record_type='historical').order_by('year', 'month'))
    outlook_records = list(active_district.climate_records.filter(record_type='outlook').order_by('year', 'month'))
    scenario_records = list(active_district.climate_records.filter(record_type='scenario').order_by('year', 'month'))

    # Run Risk Scoring Service
    risk_assessment = calculate_climate_risks(active_district, hist_records)

    # --------------------------------------------------------------------------
    # 1. Rainfall Tab Data Preparation
    # --------------------------------------------------------------------------
    # Annual rainfall aggregation (2005 - 2024)
    annual_rainfall = {}
    annual_dry_spells = {}
    annual_heat_days = {}
    annual_max_temps = {}
    annual_mean_temps = {}
    annual_min_temps = {}

    for r in hist_records:
        y = r.year
        if r.rainfall_mm is not None:
            annual_rainfall[y] = annual_rainfall.get(y, 0.0) + float(r.rainfall_mm)
        if r.dry_spell_days_max is not None and r.month in [1, 2]:
            annual_dry_spells[y] = max(annual_dry_spells.get(y, 0), r.dry_spell_days_max)
        if r.heat_wave_days is not None:
            annual_heat_days[y] = annual_heat_days.get(y, 0) + r.heat_wave_days
        if r.temp_max_c is not None:
            annual_max_temps.setdefault(y, []).append(float(r.temp_max_c))
        if r.temp_mean_c is not None:
            annual_mean_temps.setdefault(y, []).append(float(r.temp_mean_c))
        if r.temp_min_c is not None:
            annual_min_temps.setdefault(y, []).append(float(r.temp_min_c))

    hist_years = sorted(list(annual_rainfall.keys()))
    annual_rain_values = [round(annual_rainfall[y], 1) for y in hist_years]
    mean_annual_rain = round(statistics.mean(annual_rain_values), 1) if annual_rain_values else 0.0

    # Monthly rainfall averages across 20 years (1 to 12)
    monthly_hist_rain = {m: [] for m in range(1, 13)}
    monthly_hist_dry = {m: [] for m in range(1, 13)}
    monthly_hist_max_t = {m: [] for m in range(1, 13)}
    monthly_hist_mean_t = {m: [] for m in range(1, 13)}
    monthly_hist_min_t = {m: [] for m in range(1, 13)}

    for r in hist_records:
        if r.rainfall_mm is not None:
            monthly_hist_rain[r.month].append(float(r.rainfall_mm))
        if r.dry_spell_days_max is not None:
            monthly_hist_dry[r.month].append(r.dry_spell_days_max)
        if r.temp_max_c is not None:
            monthly_hist_max_t[r.month].append(float(r.temp_max_c))
        if r.temp_mean_c is not None:
            monthly_hist_mean_t[r.month].append(float(r.temp_mean_c))
        if r.temp_min_c is not None:
            monthly_hist_min_t[r.month].append(float(r.temp_min_c))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg_rain = [
        round(statistics.mean(monthly_hist_rain[m]), 1) if monthly_hist_rain[m] else 0.0
        for m in range(1, 13)
    ]
    monthly_avg_dry_spells = [
        round(statistics.mean(monthly_hist_dry[m]), 1) if monthly_hist_dry[m] else 0.0
        for m in range(1, 13)
    ]

    # Reorder months to agricultural season: Jul to Jun
    # [Jul(7), Aug(8), Sep(9), Oct(10), Nov(11), Dec(12), Jan(1), Feb(2), Mar(3), Apr(4), May(5), Jun(6)]
    crop_season_month_indices = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    season_month_labels = [month_names[idx - 1] for idx in crop_season_month_indices]
    season_hist_rain = [monthly_avg_rain[idx - 1] for idx in crop_season_month_indices]

    # Outlook and Scenario curves for the season
    outlook_map = {r.month: float(r.rainfall_mm or 0) for r in outlook_records}
    scenario_map = {r.month: float(r.rainfall_mm or 0) for r in scenario_records}

    season_outlook_rain = [outlook_map.get(idx, None) for idx in crop_season_month_indices]
    season_scenario_rain = [scenario_map.get(idx, None) for idx in crop_season_month_indices]

    chart_rainfall_data = {
        'annual': {
            'labels': hist_years,
            'rainfall': annual_rain_values,
            'mean_benchmark': mean_annual_rain,
            'drought_flags': [y in [2015, 2016, 2024] for y in hist_years],
        },
        'seasonal_cycle': {
            'labels': season_month_labels,
            'historical': season_hist_rain,
            'outlook': season_outlook_rain,
            'scenario': season_scenario_rain,
        }
    }

    # --------------------------------------------------------------------------
    # 2. Temperature Tab Data Preparation
    # --------------------------------------------------------------------------
    avg_annual_max = [
        round(statistics.mean(annual_max_temps[y]), 1) if y in annual_max_temps else None
        for y in hist_years
    ]
    avg_annual_mean = [
        round(statistics.mean(annual_mean_temps[y]), 1) if y in annual_mean_temps else None
        for y in hist_years
    ]
    avg_annual_min = [
        round(statistics.mean(annual_min_temps[y]), 1) if y in annual_min_temps else None
        for y in hist_years
    ]

    # Monthly climatological temperature curves
    monthly_avg_max_t = [
        round(statistics.mean(monthly_hist_max_t[m]), 1) if monthly_hist_max_t[m] else None
        for m in range(1, 13)
    ]
    monthly_avg_mean_t = [
        round(statistics.mean(monthly_hist_mean_t[m]), 1) if monthly_hist_mean_t[m] else None
        for m in range(1, 13)
    ]
    monthly_avg_min_t = [
        round(statistics.mean(monthly_hist_min_t[m]), 1) if monthly_hist_min_t[m] else None
        for m in range(1, 13)
    ]

    chart_temperature_data = {
        'annual_trends': {
            'labels': hist_years,
            'max': avg_annual_max,
            'mean': avg_annual_mean,
            'min': avg_annual_min,
        },
        'monthly_profile': {
            'labels': month_names,
            'max': monthly_avg_max_t,
            'mean': monthly_avg_mean_t,
            'min': monthly_avg_min_t,
        }
    }

    # --------------------------------------------------------------------------
    # 3. Heat Events Tab Data Preparation
    # --------------------------------------------------------------------------
    heat_days_series = [annual_heat_days.get(y, 0) for y in hist_years]
    avg_heat_days = round(statistics.mean(heat_days_series), 1) if heat_days_series else 0.0

    chart_heat_data = {
        'labels': hist_years,
        'heat_days': heat_days_series,
        'average_benchmark': avg_heat_days,
    }

    # Wet months analysis table (Nov - Apr)
    wet_months_summary = []
    for m in [11, 12, 1, 2, 3, 4]:
        name = month_names[m - 1]
        rain_avg = monthly_avg_rain[m - 1]
        dry_spell_avg = monthly_avg_dry_spells[m - 1]
        max_t = monthly_avg_max_t[m - 1]
        wet_months_summary.append({
            'month': name,
            'rainfall_mm': rain_avg,
            'dry_spell_days': dry_spell_avg,
            'max_temp_c': max_t,
            'status': 'Critical Flowering' if m in [1, 2] else ('Planting Onset' if m in [11, 12] else 'Maturity / Harvest'),
        })

    context = {
        'districts': districts,
        'active_district': active_district,
        'sources': sources,
        'stations': stations,
        'active_station': active_station,
        'forecasts': forecasts,
        'forecast_insights': forecast_insights,
        'recent_observations': recent_observations,
        'risk': risk_assessment,
        'wet_months_summary': wet_months_summary,
        'mean_annual_rain': mean_annual_rain,
        'avg_heat_days': avg_heat_days,
        'chart_rainfall_json': json.dumps(chart_rainfall_data),
        'chart_temp_json': json.dumps(chart_temperature_data),
        'chart_heat_json': json.dumps(chart_heat_data),
        'active_nav': 'climate',
    }
    return render(request, 'climate/dashboard.html', context)


@login_required
def sync_station_forecast(request, station_id):
    """
    Triggers live on-demand forecast synchronization from station APIs.
    """
    station = get_object_or_404(WeatherStation, station_id=station_id)
    count, src = fetch_live_forecast_for_station(station, timeout_seconds=6)
    messages.success(request, f"Live synchronization completed for '{station.name}'. Ingested {count} forecast days via {src}.")
    return redirect(f"{reverse('climate:dashboard')}?district={station.district.slug}&station={station.station_id}")
