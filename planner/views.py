import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from farms.models import Crop, Farm
from .engine import calculate_plan_allocations, simulate_game_shocks
from .models import Plan, PlanItem, PlanAssumption


@login_required
def planner_input(request):
    """
    Crop Planner UI:
    Input farm parameters, select crops, and generate 3 alternative plans:
    - Balanced Portfolio
    - Return-Focused Strategy
    - Risk-Conscious Strategy
    """
    farms = Farm.objects.filter(owner=request.user)
    farm = farms.first()

    if not farm:
        messages.warning(request, "Please register your farm details before creating a crop plan.")
        return redirect('farms:farm_edit')

    all_crops = Crop.objects.all().order_by('name')
    preferred_crop_ids = set(farm.preferred_crops.values_list('id', flat=True))

    # Form defaults from farm facts
    default_land = farm.cultivated_land_ha or farm.total_land_ha or Decimal('2.00')
    default_budget = farm.seasonal_budget_mwk or Decimal('450000.00')
    default_labour = farm.available_labour_persons or 3

    # If parameters submitted via GET or POST, generate plans
    has_generated = 'generate' in request.GET or request.method == 'POST'
    plans_data = None

    if has_generated:
        try:
            land_input = Decimal(request.GET.get('land', str(default_land)))
        except (ValueError, TypeError):
            land_input = default_land

        try:
            budget_input = Decimal(request.GET.get('budget', str(default_budget)))
        except (ValueError, TypeError):
            budget_input = default_budget

        try:
            labour_input = int(request.GET.get('labour', str(default_labour)))
        except (ValueError, TypeError):
            labour_input = default_labour

        selected_slugs = request.GET.getlist('crops')
        if not selected_slugs:
            # Fallback to preferred or standard
            selected_slugs = [c.slug for c in farm.preferred_crops.all()] or ['maize', 'groundnuts']

        selected_crop_objs = list(Crop.objects.filter(slug__in=selected_slugs))

        plans_data = calculate_plan_allocations(
            farm=farm,
            total_land_ha=land_input,
            seasonal_budget_mwk=budget_input,
            available_labour=labour_input,
            selected_crops=selected_crop_objs,
        )

    context = {
        'farm': farm,
        'farms': farms,
        'all_crops': all_crops,
        'preferred_crop_ids': preferred_crop_ids,
        'default_land': default_land,
        'default_budget': default_budget,
        'default_labour': default_labour,
        'plans_data': plans_data,
        'active_nav': 'planner',
    }
    return render(request, 'planner/planner.html', context)


@login_required
def planner_result(request):
    """Direct alias to planner_input with generated state."""
    return redirect('planner:planner_input')


@login_required
@require_POST
def save_plan(request):
    """
    Saves a generated strategy option to the database (Plan, PlanItem, PlanAssumption).
    """
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        return redirect('farms:farm_edit')

    strategy_type = request.POST.get('strategy_type', 'balanced')
    plan_name = request.POST.get('name', f"{farm.name} {strategy_type.replace('_', ' ').title()} Plan")
    total_land = Decimal(request.POST.get('total_land_ha', '2.00'))
    total_budget = Decimal(request.POST.get('total_budget_mwk', '0.00')) if request.POST.get('total_budget_mwk') else None

    selected_slugs = request.POST.getlist('crop_slugs')
    if not selected_slugs:
        selected_slugs = ['maize', 'groundnuts']

    selected_crops = list(Crop.objects.filter(slug__in=selected_slugs))
    calculation = calculate_plan_allocations(
        farm=farm,
        total_land_ha=total_land,
        seasonal_budget_mwk=total_budget,
        selected_crops=selected_crops,
    )

    chosen_plan_data = next((p for p in calculation['plans'] if p['strategy_type'] == strategy_type), calculation['plans'][0])

    # Create Plan in DB
    plan = Plan.objects.create(
        farm=farm,
        name=plan_name,
        strategy_type=strategy_type,
        status='active',
        total_land_ha=chosen_plan_data['total_land_ha'],
        total_budget_mwk=total_budget,
        total_expected_cost_mwk=chosen_plan_data['total_cost_mwk'],
        total_expected_revenue_mwk=chosen_plan_data['total_revenue_mwk'],
        total_expected_margin_mwk=chosen_plan_data['total_margin_mwk'],
    )

    # Create PlanItems
    for item in chosen_plan_data['items']:
        PlanItem.objects.create(
            plan=plan,
            crop=item['crop'],
            area_ha=item['area_ha'],
            expected_yield_kg_per_ha=item['yield_kg_ha'],
            expected_yield_kg_total=item['yield_total_kg'],
            expected_cost_per_ha_mwk=item['cost_ha_mwk'],
            expected_total_cost_mwk=item['total_cost_mwk'],
            expected_selling_price_mwk_per_kg=item['price_kg_mwk'],
            expected_revenue_mwk=item['revenue_mwk'],
            expected_gross_margin_mwk=item['gross_margin_mwk'],
            break_even_price_mwk_per_kg=item['break_even_price_mwk'],
        )

    # Create Assumptions
    for a in chosen_plan_data['assumptions']:
        PlanAssumption.objects.create(
            plan=plan,
            category=a['category'],
            parameter_name=a['name'],
            value_used=a['value'],
            source_note=a['source'],
        )

    messages.success(request, f"Plan '{plan.name}' saved successfully. You can now stress-test it in the Scenario Simulator!")
    return redirect('planner:plan_detail', pk=plan.pk)


# ==============================================================================
# Game-Like Scenario Simulator 🎮 (Phase 5.7 & 5.8)
# ==============================================================================

@login_required
def scenario_simulator(request):
    """
    Game-Like Scenario Arena:
    Tactile shock dials (Drought, Heat Wave, Price Crash, Fertilizer Spike),
    interactive health bar, profit coin meter, food security gauge, and season performance grade.
    """
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        messages.warning(request, "Please register your farm before running scenario simulations.")
        return redirect('farms:farm_edit')

    # Load baseline from saved active plan or generate a default balanced plan
    saved_plan_id = request.GET.get('plan')
    saved_plan = None
    if saved_plan_id:
        saved_plan = Plan.objects.filter(pk=saved_plan_id, farm__owner=request.user).first()

    if not saved_plan:
        saved_plan = Plan.objects.filter(farm=farm, status='active').first()

    if saved_plan:
        baseline_plan = {
            'title': saved_plan.name,
            'total_land_ha': saved_plan.total_land_ha,
            'total_cost_mwk': saved_plan.total_expected_cost_mwk,
            'total_revenue_mwk': saved_plan.total_expected_revenue_mwk,
            'total_margin_mwk': saved_plan.total_expected_margin_mwk,
            'items': [
                {
                    'crop': item.crop,
                    'area_ha': item.area_ha,
                    'yield_kg_ha': item.expected_yield_kg_per_ha,
                    'total_cost_mwk': item.expected_total_cost_mwk,
                    'price_kg_mwk': item.expected_selling_price_mwk_per_kg,
                    'gross_margin_mwk': item.expected_gross_margin_mwk,
                }
                for item in saved_plan.items.all()
            ]
        }
    else:
        # Generate default balanced plan on the fly
        calc = calculate_plan_allocations(
            farm=farm,
            total_land_ha=farm.cultivated_land_ha or farm.total_land_ha or Decimal('2.00'),
            seasonal_budget_mwk=farm.seasonal_budget_mwk or Decimal('450000.00'),
        )
        baseline_plan = calc['plans'][0]

    # Run default neutral simulation
    initial_sim = simulate_game_shocks(baseline_plan, 0.0, 0.0, 0.0, 0.0)

    # Serialize baseline items for client-side instant game loop
    baseline_json = json.dumps({
        'title': baseline_plan.get('title', 'Baseline Plan'),
        'total_land_ha': float(baseline_plan['total_land_ha']),
        'total_cost_mwk': float(baseline_plan['total_cost_mwk']),
        'total_revenue_mwk': float(baseline_plan['total_revenue_mwk']),
        'total_margin_mwk': float(baseline_plan['total_margin_mwk']),
        'items': [
            {
                'crop_name': i['crop'].name,
                'crop_slug': i['crop'].slug,
                'area_ha': float(i['area_ha']),
                'yield_kg_ha': float(i['yield_kg_ha']),
                'total_cost_mwk': float(i['total_cost_mwk']),
                'price_kg_mwk': float(i['price_kg_mwk']),
                'gross_margin_mwk': float(i['gross_margin_mwk']),
            }
            for i in baseline_plan['items']
        ]
    })

    context = {
        'farm': farm,
        'saved_plan': saved_plan,
        'baseline_plan': baseline_plan,
        'initial_sim': initial_sim,
        'baseline_json': baseline_json,
        'active_nav': 'scenarios',
    }
    return render(request, 'planner/scenario_simulator.html', context)


@login_required
def simulate_scenario_api(request):
    """
    JSON API for live scenario calculation when adjusting game sliders or challenge buttons.
    """
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        return JsonResponse({'error': 'No farm registered'}, status=400)

    try:
        rain_delta = float(request.GET.get('rain', 0.0))
        temp_delta = float(request.GET.get('temp', 0.0))
        price_delta = float(request.GET.get('price', 0.0))
        cost_delta = float(request.GET.get('cost', 0.0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid numeric parameters'}, status=400)

    plan_id = request.GET.get('plan')
    saved_plan = Plan.objects.filter(pk=plan_id, farm__owner=request.user).first() if plan_id else None

    if saved_plan:
        baseline_plan = {
            'total_margin_mwk': saved_plan.total_expected_margin_mwk,
            'items': [
                {
                    'crop': item.crop,
                    'area_ha': item.area_ha,
                    'yield_kg_ha': item.expected_yield_kg_per_ha,
                    'total_cost_mwk': item.expected_total_cost_mwk,
                    'price_kg_mwk': item.expected_selling_price_mwk_per_kg,
                    'gross_margin_mwk': item.expected_gross_margin_mwk,
                }
                for item in saved_plan.items.all()
            ]
        }
    else:
        calc = calculate_plan_allocations(
            farm=farm,
            total_land_ha=farm.cultivated_land_ha or farm.total_land_ha or Decimal('2.00'),
            seasonal_budget_mwk=farm.seasonal_budget_mwk or Decimal('450000.00'),
        )
        baseline_plan = calc['plans'][0]

    result = simulate_game_shocks(baseline_plan, rain_delta, temp_delta, price_delta, cost_delta)
    return JsonResponse(result)


# ==============================================================================
# Module 6 Preview: My Plans
# ==============================================================================

@login_required
def plan_list(request):
    plans = Plan.objects.filter(farm__owner=request.user).order_by('-created_at')
    return render(request, 'planner/plan_list.html', {
        'plans': plans,
        'active_nav': 'plans',
    })


@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(Plan, pk=pk, farm__owner=request.user)
    items = plan.items.select_related('crop').all()
    assumptions = plan.assumptions.all()

    return render(request, 'planner/plan_detail.html', {
        'plan': plan,
        'items': items,
        'assumptions': assumptions,
        'active_nav': 'plans',
    })


@login_required
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        name = plan.name
        plan.delete()
        messages.success(request, f"Plan '{name}' was deleted.")
        return redirect('planner:plan_list')

    return render(request, 'farms/confirm_delete.html', {
        'item_type': 'Crop Plan',
        'item_title': plan.name,
        'warning_text': f"This will permanently delete '{plan.name}' and all its crop allocations and assumptions.",
        'cancel_url': 'planner:plan_list',
        'active_nav': 'plans',
    })
