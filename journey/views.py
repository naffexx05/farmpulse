from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
import datetime

from farms.models import Farm, Crop
from planner.models import Plan
from .models import SeasonJourney, FarmActivityLog, JourneyCheckIn, HarvestRecord
from .engine import generate_advisory


def _get_farmer_farms(user):
    return Farm.objects.filter(owner=user)


def _get_journey_or_404(pk, user):
    journey = get_object_or_404(SeasonJourney, pk=pk)
    if journey.farm.owner != user:
        from django.http import Http404
        raise Http404
    return journey


@login_required
def journey_list(request):
    farms = _get_farmer_farms(request.user)
    journeys = SeasonJourney.objects.filter(farm__in=farms).select_related('farm', 'plan')
    active = journeys.filter(status='active')
    completed = journeys.filter(status='completed')
    abandoned = journeys.filter(status='abandoned')
    plans_without_journey = Plan.objects.filter(
        farm__in=farms
    ).exclude(journeys__status='active')
    context = {
        'active_nav': 'journey',
        'active_journeys': active,
        'completed_journeys': completed,
        'abandoned_journeys': abandoned,
        'plans_without_journey': plans_without_journey,
    }
    return render(request, 'journey/journey_list.html', context)


@login_required
def activate_journey(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id, farm__owner=request.user)
    if request.method == 'POST':
        existing = SeasonJourney.objects.filter(farm=plan.farm, status='active').first()
        if existing:
            messages.warning(
                request,
                f"{plan.farm.name} already has an active Season Journey. "
                "Complete or abandon it before starting a new one."
            )
            return redirect('journey:detail', pk=existing.pk)
        season_label = request.POST.get('season_label', '2025/26')
        expected_plant_date = request.POST.get('expected_plant_date') or None
        expected_harvest_date = request.POST.get('expected_harvest_date') or None
        journey = SeasonJourney.objects.create(
            farm=plan.farm,
            plan=plan,
            season_label=season_label,
            expected_plant_date=expected_plant_date,
            expected_harvest_date=expected_harvest_date,
            status='active',
        )
        messages.success(
            request,
            f"Season Journey activated for {plan.farm.name}. "
            "Record your first activity and check in weekly."
        )
        return redirect('journey:detail', pk=journey.pk)
    context = {
        'active_nav': 'journey',
        'plan': plan,
    }
    return render(request, 'journey/activate.html', context)


@login_required
def journey_detail(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    recent_activities = journey.activities.all()[:5]
    latest_checkin = journey.checkins.first()
    harvest_records = journey.harvest_records.select_related('crop').all()
    all_stages = [
        ('prep', 'Land Prep'),
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative'),
        ('flowering', 'Flowering'),
        ('grain_fill', 'Grain Fill'),
        ('maturity', 'Maturity'),
        ('harvest', 'Harvest'),
    ]
    current_stage_key = latest_checkin.stage if latest_checkin else 'prep'
    stage_keys = [s[0] for s in all_stages]
    current_stage_index = stage_keys.index(current_stage_key) if current_stage_key in stage_keys else 0
    total_expenses = journey.activities.filter(is_income=False).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    total_income = journey.activities.filter(is_income=True).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    net_balance = total_income - total_expenses
    planned_cost = journey.plan.total_expected_cost_mwk if journey.plan else 0
    planned_margin = journey.plan.total_expected_margin_mwk if journey.plan else 0
    days_since_checkin = None
    if latest_checkin:
        delta = timezone.now() - latest_checkin.checked_in_at
        days_since_checkin = delta.days
    checkin_due = days_since_checkin is None or days_since_checkin >= 7
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'recent_activities': recent_activities,
        'latest_checkin': latest_checkin,
        'harvest_records': harvest_records,
        'all_stages': all_stages,
        'current_stage_index': current_stage_index,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_balance': net_balance,
        'planned_cost': planned_cost,
        'planned_margin': planned_margin,
        'checkin_due': checkin_due,
        'days_since_checkin': days_since_checkin,
    }
    return render(request, 'journey/journey_detail.html', context)


@login_required
def activity_log(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    activities = journey.activities.all()
    expense_by_category = (
        activities.filter(is_income=False)
        .values('category')
        .annotate(total=Sum('amount_mwk'))
        .order_by('-total')
    )
    total_expenses = activities.filter(is_income=False).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    total_income = activities.filter(is_income=True).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    net = total_income - total_expenses
    category_map = dict(FarmActivityLog.CATEGORY_CHOICES)
    expense_rows = []
    for row in expense_by_category:
        expense_rows.append({
            'category': row['category'],
            'label': category_map.get(row['category'], row['category']),
            'total': row['total'],
        })
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'activities': activities,
        'expense_by_category': expense_rows,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net': net,
    }
    return render(request, 'journey/activity_log.html', context)


@login_required
def add_activity(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    crops = Crop.objects.all()
    if request.method == 'POST':
        category = request.POST.get('category')
        activity_date = request.POST.get('activity_date')
        description = request.POST.get('description', '').strip()
        amount_mwk = request.POST.get('amount_mwk', '0') or '0'
        is_income = request.POST.get('is_income') == '1'
        crop_id = request.POST.get('crop') or None
        quantity = request.POST.get('quantity') or None
        unit = request.POST.get('unit', '')
        product_name = request.POST.get('product_name', '')
        notes = request.POST.get('notes', '')
        if not description or not activity_date or not category:
            messages.error(request, "Please fill in category, date, and description.")
        else:
            crop = Crop.objects.filter(pk=crop_id).first() if crop_id else None
            FarmActivityLog.objects.create(
                farm=journey.farm,
                journey=journey,
                category=category,
                activity_date=activity_date,
                description=description,
                amount_mwk=amount_mwk,
                is_income=is_income,
                crop=crop,
                quantity=quantity,
                unit=unit,
                product_name=product_name,
                notes=notes,
            )
            messages.success(request, "Activity recorded successfully.")
            return redirect('journey:activity_log', pk=journey.pk)
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'categories': FarmActivityLog.CATEGORY_CHOICES,
        'crops': crops,
        'today': datetime.date.today().isoformat(),
    }
    return render(request, 'journey/add_activity.html', context)


@login_required
def delete_activity(request, log_id):
    log = get_object_or_404(FarmActivityLog, pk=log_id)
    if log.farm.owner != request.user:
        from django.http import Http404
        raise Http404
    journey_pk = log.journey.pk if log.journey else None
    log.delete()
    messages.success(request, "Activity deleted.")
    if journey_pk:
        return redirect('journey:activity_log', pk=journey_pk)
    return redirect('journey:journey_list')


@login_required
def checkin(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    if request.method == 'POST':
        stage = request.POST.get('stage', 'vegetative')
        pest_pressure = request.POST.get('pest_pressure', 'none')
        disease_pressure = request.POST.get('disease_pressure', 'none')
        moisture_score = int(request.POST.get('moisture_score', 3))
        canopy_cover_pct = int(request.POST.get('canopy_cover_pct', 50))
        notes = request.POST.get('notes', '')
        week_number = journey.week_number
        advisory = generate_advisory(
            stage, pest_pressure, disease_pressure, moisture_score, week_number
        )
        JourneyCheckIn.objects.create(
            journey=journey,
            week_number=week_number,
            stage=stage,
            pest_pressure=pest_pressure,
            disease_pressure=disease_pressure,
            moisture_score=moisture_score,
            canopy_cover_pct=canopy_cover_pct,
            advisory=advisory,
            notes=notes,
        )
        messages.success(
            request,
            f"Week {week_number} check-in recorded. See your advisory below."
        )
        return redirect('journey:detail', pk=journey.pk)
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'growth_stages': JourneyCheckIn.GROWTH_STAGES,
        'pressure_levels': JourneyCheckIn.PRESSURE_LEVELS,
        'moisture_labels': {
            1: 'Very Dry',
            2: 'Dry',
            3: 'Adequate',
            4: 'Moist',
            5: 'Waterlogged',
        },
    }
    return render(request, 'journey/checkin.html', context)


@login_required
def log_harvest(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    plan_items = journey.plan.items.select_related('crop').all() if journey.plan else []
    if request.method == 'POST':
        crop_ids = request.POST.getlist('crop_id')
        for crop_id in crop_ids:
            crop = Crop.objects.filter(pk=crop_id).first()
            if not crop:
                continue
            area = request.POST.get(f'area_{crop_id}', '0') or '0'
            yield_kg = request.POST.get(f'yield_{crop_id}', '0') or '0'
            bags = request.POST.get(f'bags_{crop_id}', '0') or '0'
            price = request.POST.get(f'price_{crop_id}', '0') or '0'
            revenue = request.POST.get(f'revenue_{crop_id}', '0') or '0'
            harvest_date = request.POST.get(f'date_{crop_id}', datetime.date.today().isoformat())
            notes = request.POST.get(f'notes_{crop_id}', '')
            HarvestRecord.objects.create(
                journey=journey,
                crop=crop,
                actual_area_ha=area,
                actual_yield_kg=yield_kg,
                bags_50kg=bags,
                selling_price_mwk=price,
                actual_revenue_mwk=revenue,
                notes=notes,
                harvested_at=harvest_date,
            )
        total_revenue = sum(
            float(request.POST.get(f'revenue_{cid}', 0) or 0)
            for cid in crop_ids
        )
        if total_revenue > 0:
            FarmActivityLog.objects.create(
                farm=journey.farm,
                journey=journey,
                category='sale',
                activity_date=datetime.date.today(),
                description='Crop sale — harvest proceeds',
                amount_mwk=total_revenue,
                is_income=True,
            )
        journey.actual_harvest_date = datetime.date.today()
        journey.status = 'completed'
        journey.save()
        messages.success(request, "Harvest recorded. Your Season Journey is now complete.")
        return redirect('journey:review', pk=journey.pk)
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'plan_items': plan_items,
        'today': datetime.date.today().isoformat(),
    }
    return render(request, 'journey/harvest.html', context)


@login_required
def season_review(request, pk):
    journey = _get_journey_or_404(pk, request.user)
    harvest_records = journey.harvest_records.select_related('crop').all()
    activities = journey.activities.all()
    checkins = journey.checkins.all()
    total_expenses = activities.filter(is_income=False).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    total_income = activities.filter(is_income=True).aggregate(
        total=Sum('amount_mwk'))['total'] or 0
    actual_net = total_income - total_expenses
    planned_cost = journey.plan.total_expected_cost_mwk if journey.plan else 0
    planned_margin = journey.plan.total_expected_margin_mwk if journey.plan else 0
    comparison_rows = []
    if journey.plan:
        for item in journey.plan.items.select_related('crop').all():
            hr = harvest_records.filter(crop=item.crop).first()
            planned_yield_kg = float(getattr(item, 'expected_yield_kg', 0) or 0)
            actual_yield_kg = float(hr.actual_yield_kg) if hr else 0
            accuracy = 0
            if planned_yield_kg > 0 and actual_yield_kg > 0:
                accuracy = min(100, round((actual_yield_kg / planned_yield_kg) * 100))
            comparison_rows.append({
                'crop': item.crop.name,
                'planned_ha': float(item.area_ha),
                'actual_ha': float(hr.actual_area_ha) if hr else 0,
                'planned_yield_kg': planned_yield_kg,
                'actual_yield_kg': actual_yield_kg,
                'actual_revenue': float(hr.actual_revenue_mwk) if hr else 0,
                'accuracy': accuracy,
            })
    if comparison_rows:
        accuracy_scores = [r['accuracy'] for r in comparison_rows if r['planned_yield_kg'] > 0]
        plan_accuracy = round(sum(accuracy_scores) / len(accuracy_scores)) if accuracy_scores else 0
    else:
        plan_accuracy = 0
    duration_days = None
    if journey.actual_harvest_date and journey.expected_plant_date:
        duration_days = (journey.actual_harvest_date - journey.expected_plant_date).days
    context = {
        'active_nav': 'journey',
        'journey': journey,
        'harvest_records': harvest_records,
        'activities': activities,
        'checkins': checkins,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'actual_net': actual_net,
        'planned_cost': planned_cost,
        'planned_margin': planned_margin,
        'comparison_rows': comparison_rows,
        'plan_accuracy': plan_accuracy,
        'duration_days': duration_days,
        'checkin_count': checkins.count(),
    }
    return render(request, 'journey/season_review.html', context)
