import csv
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from farms.models import Crop, Farm
from .engine import calculate_plan_allocations, get_crop_benchmarks, simulate_game_shocks
from .models import Plan, PlanItem, PlanAssumption, InputCostBenchmark, SeasonalInputCost

CURRENT_SEASON = 2025


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

    crops_benchmarks = {}
    for c in all_crops:
        bm = get_crop_benchmarks(c, farm)
        crops_benchmarks[c.slug] = {
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'category': c.get_category_display(),
            'yield_kg_ha': float(bm['yield_kg_ha']),
            'cost_ha_mwk': float(bm['cost_ha_mwk']),
            'price_kg_mwk': float(bm['price_kg_mwk']),
            'break_even_price_mwk': float(bm['break_even_price_mwk']),
            'is_staple': c.slug in ['maize', 'cassava', 'sorghum', 'rice'],
            'drought_resilience': 'High' if c.slug in ['cassava', 'sorghum', 'groundnuts'] else ('Moderate' if c.slug in ['soybeans', 'common-beans'] else 'Standard'),
            'color': {
                'maize': '#8FCB62',
                'groundnuts': '#F2B441',
                'soybeans': '#4FB7D9',
                'common-beans': '#C084FC',
                'cassava': '#34D399',
                'rice': '#38BDF8',
                'sorghum': '#FB923C',
                'tobacco': '#A3E635',
            }.get(c.slug, '#8FCB62'),
        }


    # -- Input Cost Ledger --------------------------------------------------
    CURRENT_SEASON = 2025
    INPUT_CATEGORIES = [
        ('seed',       'Seed / Planting Material'),
        ('basal_fert', 'Basal Fertiliser'),
        ('top_dress',  'Top Dressing'),
        ('labour',     'Labour'),
        ('herbicide',  'Herbicide / Pesticide'),
        ('transport',  'Transport to Market'),
    ]
    benchmarks_qs = InputCostBenchmark.objects.filter(season_year=CURRENT_SEASON).select_related('crop')
    benchmarks_by_crop = {}
    for _b in benchmarks_qs:
        benchmarks_by_crop.setdefault(_b.crop.slug, {})[_b.input_category] = {
            'description': _b.description,
            'price': float(_b.benchmark_price_mwk_per_ha),
        }
    farmer_overrides = {}
    if farm:
        for sic in SeasonalInputCost.objects.filter(farm=farm, season_year=CURRENT_SEASON).select_related('crop'):
            farmer_overrides[sic.crop.slug] = {
                'seed':       float(sic.seed_cost_mwk_per_ha or 0),
                'basal_fert': float(sic.basal_fert_cost_mwk_per_ha or 0),
                'top_dress':  float(sic.top_dress_cost_mwk_per_ha or 0),
                'labour':     float(sic.labour_cost_mwk_per_ha or 0),
                'herbicide':  float(sic.herbicide_cost_mwk_per_ha or 0),
                'transport':  float(sic.transport_cost_mwk_per_ha or 0),
            }
    latest_benchmark = benchmarks_qs.filter(last_synced_at__isnull=False).order_by('-last_synced_at').first()
    last_synced_date = latest_benchmark.last_synced_at.strftime('%d %b %Y, %H:%M') if latest_benchmark else "2025/26 Season"
    data_source_display = "WFP / HDX Market Surveillance" if (latest_benchmark and latest_benchmark.data_source == 'wfp_vam') else "ADMARC / AGORA 2025 Benchmark"

    input_ledger_json = json.dumps({
        'categories': INPUT_CATEGORIES,
        'benchmarks': benchmarks_by_crop,
        'farmer_overrides': farmer_overrides,
        'season_year': CURRENT_SEASON,
    })

    context = {
        'farm': farm,
        'farms': farms,
        'all_crops': all_crops,
        'preferred_crop_ids': preferred_crop_ids,
        'default_land': default_land,
        'default_budget': default_budget,
        'default_labour': default_labour,
        'plans_data': plans_data,
        'crops_benchmarks_json': json.dumps(crops_benchmarks),
        'input_ledger_json': input_ledger_json,
        'last_synced_date': last_synced_date,
        'data_source_display': data_source_display,
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
    Saves a generated strategy option or custom field allocation to the database (Plan, PlanItem, PlanAssumption).
    """
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        return redirect('farms:farm_edit')

    # Support interactive custom field allocations
    custom_allocations_raw = request.POST.get('custom_allocations_json')
    if custom_allocations_raw:
        try:
            alloc_data = json.loads(custom_allocations_raw)
            plan_name = request.POST.get('name') or f"{farm.name} Custom Field Plan"
            total_budget = Decimal(request.POST.get('total_budget_mwk', '0.00')) if request.POST.get('total_budget_mwk') else None

            plan_items_to_create = []
            total_land = Decimal('0.00')
            total_cost = Decimal('0.00')
            total_rev = Decimal('0.00')

            for entry in alloc_data:
                slug = entry.get('slug')
                area_ha = Decimal(str(entry.get('area_ha', '0.00')))
                if area_ha <= 0:
                    continue
                crop = Crop.objects.filter(slug=slug).first()
                if not crop:
                    continue
                bm = get_crop_benchmarks(crop, farm)
                cost_item = area_ha * bm['cost_ha_mwk']
                yield_total = area_ha * bm['yield_kg_ha']
                rev_item = yield_total * bm['price_kg_mwk']
                margin_item = rev_item - cost_item
                be_price = cost_item / yield_total if yield_total > 0 else Decimal('0.00')

                total_land += area_ha
                total_cost += cost_item
                total_rev += rev_item

                plan_items_to_create.append({
                    'crop': crop,
                    'area_ha': area_ha,
                    'yield_kg_ha': bm['yield_kg_ha'],
                    'yield_total_kg': yield_total,
                    'cost_ha_mwk': bm['cost_ha_mwk'],
                    'total_cost_mwk': cost_item,
                    'price_kg_mwk': bm['price_kg_mwk'],
                    'revenue_mwk': rev_item,
                    'gross_margin_mwk': margin_item,
                    'break_even_price_mwk': round(be_price, 2),
                    'bm': bm,
                })

            if plan_items_to_create:
                total_margin = total_rev - total_cost
                plan = Plan.objects.create(
                    farm=farm,
                    name=plan_name,
                    strategy_type='custom',
                    status='active',
                    total_land_ha=total_land,
                    total_budget_mwk=total_budget,
                    total_expected_cost_mwk=round(total_cost, 2),
                    total_expected_revenue_mwk=round(total_rev, 2),
                    total_expected_margin_mwk=round(total_margin, 2),
                    notes="Configured via interactive Field Land Splitter canvas.",
                )

                for item in plan_items_to_create:
                    PlanItem.objects.create(
                        plan=plan,
                        crop=item['crop'],
                        area_ha=item['area_ha'],
                        expected_yield_kg_per_ha=item['yield_kg_ha'],
                        expected_yield_kg_total=round(item['yield_total_kg'], 1),
                        expected_cost_per_ha_mwk=round(item['cost_ha_mwk'], 2),
                        expected_total_cost_mwk=round(item['total_cost_mwk'], 2),
                        expected_selling_price_mwk_per_kg=round(item['price_kg_mwk'], 2),
                        expected_revenue_mwk=round(item['revenue_mwk'], 2),
                        expected_gross_margin_mwk=round(item['gross_margin_mwk'], 2),
                        break_even_price_mwk_per_kg=item['break_even_price_mwk'],
                    )
                    PlanAssumption.objects.create(
                        plan=plan,
                        category='yield',
                        parameter_name=f"{item['crop'].name} Yield Baseline",
                        value_used=f"{item['yield_kg_ha']} kg/ha",
                        source_note=item['bm']['yield_source'],
                    )
                    PlanAssumption.objects.create(
                        plan=plan,
                        category='price',
                        parameter_name=f"{item['crop'].name} Price Baseline",
                        value_used=f"{item['price_kg_mwk']} MWK/kg",
                        source_note=item['bm']['price_source'],
                    )

                messages.success(request, f"Custom plan '{plan.name}' saved successfully with {total_land} ha allocated!")
                return redirect('planner:plan_detail', pk=plan.pk)
        except Exception as e:
            messages.error(request, f"Failed to save custom plan: {str(e)}")
            return redirect('planner:planner_input')

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
# Game-Like Scenario Simulator ðŸŽ® (Phase 5.7 & 5.8)
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
        calc = calculate_plan_allocations(
            farm=farm,
            total_land_ha=farm.cultivated_land_ha or farm.total_land_ha or Decimal('2.00'),
            seasonal_budget_mwk=farm.seasonal_budget_mwk or Decimal('450000.00'),
        )
        baseline_plan = calc['plans'][0]

    initial_sim = simulate_game_shocks(baseline_plan, 0.0, 0.0, 0.0, 0.0)

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
# Module 6: My Plans (List, Detail, Compare, Duplicate, CSV Export, Delete)
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
def plan_compare(request):
    """
    Phase 6.3 Compare view: side-by-side comparison of 2 or 3 saved plans.
    """
    all_user_plans = Plan.objects.filter(farm__owner=request.user).order_by('-created_at')

    # Get selected plan IDs
    ids_param = request.GET.get('ids', '')
    plan_ids = []
    if ids_param:
        plan_ids = [int(i.strip()) for i in ids_param.split(',') if i.strip().isdigit()]
    elif 'id' in request.GET:
        plan_ids = [int(i) for i in request.GET.getlist('id') if i.isdigit()]

    if not plan_ids and all_user_plans.count() >= 2:
        plan_ids = list(all_user_plans[:3].values_list('id', flat=True))

    selected_plans = list(
        Plan.objects.filter(id__in=plan_ids, farm__owner=request.user)
        .prefetch_related('items__crop')
    )

    all_crop_names = sorted(list({
        item.crop.name
        for p in selected_plans
        for item in p.items.all()
    }))

    crop_comparison = []
    for crop_name in all_crop_names:
        row = {'crop_name': crop_name, 'plans': []}
        for p in selected_plans:
            matching = next((item for item in p.items.all() if item.crop.name == crop_name), None)
            row['plans'].append(matching)
        crop_comparison.append(row)

    return render(request, 'planner/plan_compare.html', {
        'all_user_plans': all_user_plans,
        'selected_plans': selected_plans,
        'crop_comparison': crop_comparison,
        'active_nav': 'plans',
    })


@login_required
def plan_duplicate(request, pk):
    """Phase 6.4 Duplicate plan action."""
    plan = get_object_or_404(Plan, pk=pk, farm__owner=request.user)
    new_plan = Plan.objects.create(
        farm=plan.farm,
        name=f"Copy of {plan.name}",
        strategy_type=plan.strategy_type,
        status='draft',
        total_land_ha=plan.total_land_ha,
        total_budget_mwk=plan.total_budget_mwk,
        total_expected_cost_mwk=plan.total_expected_cost_mwk,
        total_expected_revenue_mwk=plan.total_expected_revenue_mwk,
        total_expected_margin_mwk=plan.total_expected_margin_mwk,
        notes=plan.notes,
    )
    for item in plan.items.all():
        PlanItem.objects.create(
            plan=new_plan,
            crop=item.crop,
            area_ha=item.area_ha,
            expected_yield_kg_per_ha=item.expected_yield_kg_per_ha,
            expected_yield_kg_total=item.expected_yield_kg_total,
            expected_cost_per_ha_mwk=item.expected_cost_per_ha_mwk,
            expected_total_cost_mwk=item.expected_total_cost_mwk,
            expected_selling_price_mwk_per_kg=item.expected_selling_price_mwk_per_kg,
            expected_revenue_mwk=item.expected_revenue_mwk,
            expected_gross_margin_mwk=item.expected_gross_margin_mwk,
            break_even_price_mwk_per_kg=item.break_even_price_mwk_per_kg,
        )
    for a in plan.assumptions.all():
        PlanAssumption.objects.create(
            plan=new_plan,
            category=a.category,
            parameter_name=a.parameter_name,
            value_used=a.value_used,
            source_note=a.source_note,
        )
    messages.success(request, f"Plan duplicated as '{new_plan.name}'.")
    return redirect('planner:plan_detail', pk=new_plan.pk)


@login_required
def plan_export_csv(request, pk):
    """Phase 6.4 CSV Export action."""
    plan = get_object_or_404(Plan, pk=pk, farm__owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="farmpulse_plan_{plan.pk}.csv"'

    writer = csv.writer(response)
    writer.writerow(['FarmPulse Malawi â€” Strategic Crop Plan Export'])
    writer.writerow(['Plan Name', plan.name])
    writer.writerow(['Farm', plan.farm.name])
    writer.writerow(['Strategy', plan.get_strategy_type_display()])
    writer.writerow(['Total Land (ha)', plan.total_land_ha])
    writer.writerow(['Total Cost (MWK)', plan.total_expected_cost_mwk])
    writer.writerow(['Total Revenue (MWK)', plan.total_expected_revenue_mwk])
    writer.writerow(['Expected Net Margin (MWK)', plan.total_expected_margin_mwk])
    writer.writerow([])
    writer.writerow([
        'Crop', 'Area (ha)', 'Yield (kg/ha)', 'Total Yield (kg)',
        'Cost/ha (MWK)', 'Total Cost (MWK)', 'Selling Price (MWK/kg)',
        'Revenue (MWK)', 'Gross Margin (MWK)', 'Break-Even Price (MWK/kg)'
    ])
    for item in plan.items.select_related('crop').all():
        writer.writerow([
            item.crop.name,
            item.area_ha,
            item.expected_yield_kg_per_ha,
            item.expected_yield_kg_total,
            item.expected_cost_per_ha_mwk,
            item.expected_total_cost_mwk,
            item.expected_selling_price_mwk_per_kg,
            item.expected_revenue_mwk,
            item.expected_gross_margin_mwk,
            item.break_even_price_mwk_per_kg,
        ])
    writer.writerow([])
    writer.writerow(['Category', 'Parameter', 'Value', 'Source'])
    for a in plan.assumptions.all():
        writer.writerow([a.get_category_display(), a.parameter_name, a.value_used, a.source_note])

    return response


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


@login_required
@require_POST
def save_input_costs(request):
    """
    AJAX endpoint: saves farmer-adjusted input prices for a given crop/season.
    Accepts JSON body: { crop_slug, seed, basal_fert, top_dress, labour, herbicide, transport }
    Returns JSON: { ok, total_per_ha }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    crop_slug = data.get('crop_slug', '').strip()
    season_year = int(data.get('season_year', 2025))

    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        return JsonResponse({'ok': False, 'error': 'No farm registered'}, status=403)

    try:
        crop = Crop.objects.get(slug=crop_slug)
    except Crop.DoesNotExist:
        return JsonResponse({'ok': False, 'error': f'Crop not found: {crop_slug}'}, status=404)

    def _decimal(key):
        val = data.get(key)
        if val is None or str(val).strip() == '':
            return None
        try:
            return Decimal(str(val))
        except Exception:
            return None

    obj, _ = SeasonalInputCost.objects.update_or_create(
        farm=farm,
        crop=crop,
        season_year=season_year,
        defaults={
            'seed_cost_mwk_per_ha':       _decimal('seed'),
            'basal_fert_cost_mwk_per_ha': _decimal('basal_fert'),
            'top_dress_cost_mwk_per_ha':  _decimal('top_dress'),
            'labour_cost_mwk_per_ha':     _decimal('labour'),
            'herbicide_cost_mwk_per_ha':  _decimal('herbicide'),
            'transport_cost_mwk_per_ha':  _decimal('transport'),
        }
    )

    return JsonResponse({
        'ok': True,
        'total_per_ha': float(obj.total_cost_per_ha()),
        'crop_slug': crop_slug,
    })


@login_required
def sync_input_prices(request):
    """
    AJAX / Web endpoint: Synchronizes InputCostBenchmark records with
    live WFP/HDX market price surveillance.
    Returns refreshed benchmark data for live JS ledger re-rendering.
    """
    from .sync_service import execute_hdx_price_sync

    result = execute_hdx_price_sync(season_year=CURRENT_SEASON, dry_run=False)

    # Fetch refreshed benchmarks
    benchmarks_qs = InputCostBenchmark.objects.filter(season_year=CURRENT_SEASON).select_related('crop')
    benchmarks_by_crop = {}
    for _b in benchmarks_qs:
        benchmarks_by_crop.setdefault(_b.crop.slug, {})[_b.input_category] = {
            'description': _b.description,
            'price': float(_b.benchmark_price_mwk_per_ha),
        }

    return JsonResponse({
        'ok': result['ok'],
        'status': result.get('status', 'synced'),
        'updated': result.get('updated', 0),
        'source': result.get('source', 'ADMARC Benchmark'),
        'timestamp': result.get('timestamp', ''),
        'message': result.get('message', 'Market prices updated.'),
        'benchmarks': benchmarks_by_crop,
    })
