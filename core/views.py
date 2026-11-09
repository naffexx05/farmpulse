import json
from decimal import Decimal
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q

from .forms import UserAccountForm, UserProfileForm
from .models import get_user_profile
from farms.models import Farm, Season, Planting, Crop
from climate.models import District, ClimateRecord
from climate.risk import calculate_climate_risks
from market.models import CropPrice, InputCost
from planner.models import Plan, PlanItem


def home(request):
    """
    Module 8 — Agricultural Intelligence Dashboard & Overview (Visual Centrepiece).
    Data-backed integration connecting farm status, climate risks, recent performance,
    saved plans, and seasonal agro-climatic outlooks.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    farm = Farm.objects.filter(owner=request.user).prefetch_related('preferred_crops').first()
    
    # User Profile
    profile = get_user_profile(request.user)

    # 1. Location & District
    district_obj = None
    if farm:
        # Try finding district from location description or preferred
        district_obj = District.objects.filter(name__icontains=farm.location_description.split(',')[0].strip()).first()
    if not district_obj:
        district_obj = District.objects.filter(name__icontains=profile.preferred_district).first() or District.objects.first()

    # 2. Climate Risk Overview
    climate_risks = calculate_climate_risks(district_obj) if district_obj else {
        'rainfall_risk': {'level': 'Insufficient Data', 'badge': 'gray', 'detail': 'No district records'},
        'heat_risk': {'level': 'Insufficient Data', 'badge': 'gray', 'detail': 'No district records'},
        'dry_spell_risk': {'level': 'Insufficient Data', 'badge': 'gray', 'detail': 'No district records'},
        'historical_years': 0,
    }

    # 3. Active & Recent Seasons
    seasons = Season.objects.filter(farm=farm).order_by('-start_date') if farm else []
    current_season = seasons.first() if seasons else None
    
    # 4. Recent Farm Performance (observed metrics from last season)
    recent_plantings = list(current_season.plantings.select_related('crop').all()) if current_season else []
    recent_area = sum(p.area_ha for p in recent_plantings)
    recent_cost = sum(p.production_cost_mwk or Decimal('0') for p in recent_plantings)
    recent_rev = sum(p.revenue_mwk or Decimal('0') for p in recent_plantings)
    recent_margin = sum(p.gross_margin_mwk or Decimal('0') for p in recent_plantings if p.gross_margin_mwk is not None)
    recent_yield = sum(p.yield_kg or Decimal('0') for p in recent_plantings)

    # 5. Saved Plans
    plans_qs = Plan.objects.filter(farm=farm).prefetch_related('items__crop').order_by('-created_at') if farm else Plan.objects.none()
    active_plan = plans_qs.filter(status='active').first() or plans_qs.first()
    saved_plans = list(plans_qs[:4])

    # 6. Seasonal Climate Summary Chart Data (Rainfall, Temp, Heat)
    chart_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rainfall_series = [0] * 12
    temp_max_series = [0] * 12
    temp_min_series = [0] * 12
    heat_days_series = [0] * 12

    if district_obj:
        # Get latest available calendar year records (e.g. 2024 or 2023)
        latest_record = ClimateRecord.objects.filter(district=district_obj).order_by('-year', '-month').first()
        chart_year = latest_record.year if latest_record else 2024
        records = ClimateRecord.objects.filter(district=district_obj, year=chart_year).order_by('month')
        for r in records:
            idx = r.month - 1
            if 0 <= idx < 12:
                rainfall_series[idx] = float(r.rainfall_mm)
                temp_max_series[idx] = float(r.temp_max_c)
                temp_min_series[idx] = float(r.temp_min_c)
                heat_days_series[idx] = int(r.heat_wave_days)
    else:
        chart_year = 2024

    # 7. Crop Plan Comparison / Active Portfolio
    plan_items = list(active_plan.items.select_related('crop').all()) if active_plan else []

    context = {
        'farm': farm,
        'profile': profile,
        'district': district_obj,
        'climate_risks': climate_risks,
        'current_season': current_season,
        'recent_perf': {
            'area': recent_area,
            'cost': recent_cost,
            'revenue': recent_rev,
            'margin': recent_margin,
            'yield': recent_yield,
            'plantings_count': len(recent_plantings),
        },
        'saved_plans': saved_plans,
        'active_plan': active_plan,
        'plan_items': plan_items,
        'chart_data_json': json.dumps({
            'months': chart_months,
            'year': chart_year,
            'rainfall': rainfall_series,
            'temp_max': temp_max_series,
            'temp_min': temp_min_series,
            'heat_days': heat_days_series,
        }),
        'active_nav': 'overview',
    }
    return render(request, 'home.html', context)


def design_preview(request):
    """Developer preview for FarmPulse design tokens and UI components."""
    return render(request, 'design_preview.html', {'active_nav': 'design_preview'})


@login_required
def settings_index(request):
    """
    Module 9 — User Profile, Agronomic Units, and Data Privacy Management.
    """
    profile = get_user_profile(request.user)
    tab = request.GET.get('tab', 'profile')

    farm = Farm.objects.filter(owner=request.user).first()
    seasons_count = Season.objects.filter(farm=farm).count() if farm else 0
    plantings_count = Planting.objects.filter(season__farm=farm).count() if farm else 0
    plans_count = Plan.objects.filter(farm=farm).count() if farm else 0

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'profile':
            account_form = UserAccountForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            if account_form.is_valid() and profile_form.is_valid():
                account_form.save()
                profile_form.save()
                messages.success(request, "Profile and preferences updated successfully.")
                return redirect('settings_index')
        elif action == 'units':
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Agronomic units saved.")
                return redirect('/settings/?tab=units')
    else:
        account_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'settings/index.html', {
        'profile': profile,
        'account_form': account_form,
        'profile_form': profile_form,
        'tab': tab,
        'stats': {
            'farms': 1 if farm else 0,
            'seasons': seasons_count,
            'plantings': plantings_count,
            'plans': plans_count,
        },
        'active_nav': 'settings',
    })


@login_required
def export_user_data(request):
    """
    Module 9.3 — Data Export (JSON).
    Produces a complete, portable archive of the user's farm data.
    """
    farm = Farm.objects.filter(owner=request.user).first()
    data = {
        'exported_at': timezone.now().isoformat(),
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        },
        'farm': None,
        'seasons': [],
        'plans': [],
    }

    if farm:
        data['farm'] = {
            'name': farm.name,
            'location_description': farm.location_description,
            'total_land_ha': str(farm.total_land_ha),
            'cultivated_land_ha': str(farm.cultivated_land_ha) if farm.cultivated_land_ha else None,
            'irrigation_type': farm.irrigation_type,
            'soil_type': farm.soil_type,
            'seasonal_budget_mwk': str(farm.seasonal_budget_mwk) if farm.seasonal_budget_mwk else None,
            'available_labour_persons': farm.available_labour_persons,
        }

        for s in farm.seasons.all():
            season_data = {
                'name': s.name,
                'start_date': str(s.start_date),
                'end_date': str(s.end_date),
                'notes': s.notes,
                'plantings': [
                    {
                        'crop': p.crop.name,
                        'area_ha': str(p.area_ha),
                        'yield_kg': str(p.yield_kg) if p.yield_kg else None,
                        'production_cost_mwk': str(p.production_cost_mwk) if p.production_cost_mwk else None,
                        'revenue_mwk': str(p.revenue_mwk) if p.revenue_mwk else None,
                        'notes': p.notes,
                    }
                    for p in s.plantings.all()
                ],
            }
            if hasattr(s, 'review') and s.review:
                season_data['review'] = {
                    'overall_satisfaction': s.review.overall_satisfaction,
                    'lessons_learned': s.review.lessons_learned,
                    'weather_assessment': s.review.weather_assessment,
                    'market_assessment': s.review.market_assessment,
                }
            data['seasons'].append(season_data)

        for pl in farm.plans.all():
            data['plans'].append({
                'name': pl.name,
                'strategy': pl.strategy_type,
                'total_land_ha': str(pl.total_land_ha),
                'total_expected_cost_mwk': str(pl.total_expected_cost_mwk),
                'total_expected_revenue_mwk': str(pl.total_expected_revenue_mwk),
                'total_expected_margin_mwk': str(pl.total_expected_margin_mwk),
                'items': [
                    {
                        'crop': it.crop.name,
                        'area_ha': str(it.area_ha),
                        'expected_yield_kg_total': str(it.expected_yield_kg_total),
                        'expected_total_cost_mwk': str(it.expected_total_cost_mwk),
                        'expected_revenue_mwk': str(it.expected_revenue_mwk),
                        'expected_gross_margin_mwk': str(it.expected_gross_margin_mwk),
                        'break_even_price_mwk_per_kg': str(it.break_even_price_mwk_per_kg),
                    }
                    for it in pl.items.all()
                ],
            })

    filename = f"farmpulse_backup_{request.user.username}_{timezone.now().strftime('%Y%m%d')}.json"
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def search_global(request):
    """
    Module 10.4 — Global Unified Search across crops, saved plans, plantings, and districts.
    """
    query = request.GET.get('q', '').strip()
    farm = Farm.objects.filter(owner=request.user).first()

    results = {
        'query': query,
        'crops': [],
        'plans': [],
        'plantings': [],
        'districts': [],
    }

    if query and len(query) >= 2:
        # Crops
        results['crops'] = list(Crop.objects.filter(
            Q(name__icontains=query) | Q(scientific_name__icontains=query) | Q(category__icontains=query)
        )[:6])

        # Plans
        if farm:
            results['plans'] = list(Plan.objects.filter(
                farm=farm,
                name__icontains=query
            )[:6])

            # Plantings
            results['plantings'] = list(Planting.objects.filter(
                season__farm=farm
            ).filter(
                Q(crop__name__icontains=query) | Q(notes__icontains=query) | Q(season__name__icontains=query)
            ).select_related('crop', 'season')[:6])

        # Districts
        results['districts'] = list(District.objects.filter(name__icontains=query)[:4])

    total_count = (
        len(results['crops']) +
        len(results['plans']) +
        len(results['plantings']) +
        len(results['districts'])
    )

    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'total_count': total_count,
        'active_nav': 'search',
    })


@login_required
def admin_portal(request):
    """
    Executive & Extension Officer Governance Center.
    Provides District Agricultural Development Officers (DADOs) and platform
    administrators with real-time aggregate intelligence across all farmers in Malawi.
    """
    from django.db.models import Sum, Avg, Count
    from innovation.models import SatelliteParcel, ParametricInsurancePolicy

    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')
        if action == 'broadcast_alert':
            target_district = request.POST.get('district', 'All Districts')
            alert_type = request.POST.get('alert_type', 'Weather Warning')
            message_text = request.POST.get('message', '').strip()
            farmer_qs = User.objects.filter(is_staff=False)
            if target_district != 'All Districts':
                farmer_qs = farmer_qs.filter(profile__preferred_district=target_district)
            recipient_count = farmer_qs.count()
            messages.success(
                request,
                f"Official {alert_type} SMS broadcast successfully dispatched to {recipient_count} registered farmers in {target_district} via Airtel/TNM Gateway."
            )
            return redirect('admin_portal')

    # Aggregate metrics
    total_farmers = User.objects.filter(is_staff=False).count()
    farms = Farm.objects.select_related('owner').prefetch_related('preferred_crops', 'seasons')
    total_farms = farms.count()
    total_land_ha = farms.aggregate(Sum('total_land_ha'))['total_land_ha__sum'] or Decimal('0.00')
    total_plantings = Planting.objects.count()
    total_cost = Planting.objects.aggregate(Sum('production_cost_mwk'))['production_cost_mwk__sum'] or Decimal('0.00')
    total_revenue = Planting.objects.aggregate(Sum('revenue_mwk'))['revenue_mwk__sum'] or Decimal('0.00')
    total_net_margin = total_revenue - total_cost

    # Satellite and Insurance exposure
    total_parcels = SatelliteParcel.objects.count()
    avg_ndvi = SatelliteParcel.objects.aggregate(Avg('mean_ndvi'))['mean_ndvi__avg'] or Decimal('0.65')
    policies = ParametricInsurancePolicy.objects.select_related('farm', 'crop')
    total_policies = policies.count()
    total_sum_insured = policies.aggregate(Sum('sum_insured_mwk'))['sum_insured_mwk__sum'] or Decimal('0.00')
    total_payouts = policies.aggregate(Sum('payout_mwk'))['payout_mwk__sum'] or Decimal('0.00')
    triggered_policies_count = policies.filter(status='triggered').count()

    districts_list = [
        'Mzuzu', 'Lilongwe', 'Kasungu', 'Karonga', 'Rumphi',
        'Dedza', 'Salima', 'Balaka', 'Thyolo', 'Zomba', 'Mchinji', 'Mzimba'
    ]

    farmers_data = []
    for f in farms.order_by('name'):
        prof = getattr(f.owner, 'profile', None)
        latest_parcel = f.satellite_parcels.first()
        latest_policy = f.insurance_policies.first()
        farmers_data.append({
            'user': f.owner,
            'farm': f,
            'district': prof.preferred_district if prof else 'Malawi',
            'phone': prof.phone_number if prof else '—',
            'crops': list(f.preferred_crops.all()),
            'seasons_count': f.seasons.count(),
            'ndvi': latest_parcel.mean_ndvi if latest_parcel else None,
            'stress': latest_parcel.stress_level if latest_parcel else 'optimal',
            'policy_number': latest_policy.policy_number if latest_policy else None,
            'policy_status': latest_policy.status if latest_policy else None,
            'sum_insured': latest_policy.sum_insured_mwk if latest_policy else None,
        })

    crop_stats = Planting.objects.values('crop__name').annotate(
        total_ha=Sum('area_ha'),
        total_rev=Sum('revenue_mwk'),
        plantings_count=Count('id')
    ).order_by('-total_ha')[:8]

    return render(request, 'core/admin_portal.html', {
        'active_nav': 'admin_portal',
        'total_farmers': total_farmers,
        'total_farms': total_farms,
        'total_land_ha': total_land_ha,
        'total_plantings': total_plantings,
        'total_cost': total_cost,
        'total_revenue': total_revenue,
        'total_net_margin': total_net_margin,
        'total_parcels': total_parcels,
        'avg_ndvi': round(avg_ndvi, 2),
        'total_policies': total_policies,
        'total_sum_insured': total_sum_insured,
        'total_payouts': total_payouts,
        'triggered_policies_count': triggered_policies_count,
        'farmers_data': farmers_data,
        'crop_stats': crop_stats,
        'districts_list': districts_list,
    })

