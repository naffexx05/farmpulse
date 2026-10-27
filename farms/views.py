import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FarmForm, PlantingForm, SeasonForm, SeasonReviewForm
from .models import Farm, Planting, Season, SeasonReview


@login_required
def my_farm(request):
    farms = Farm.objects.filter(owner=request.user).prefetch_related('preferred_crops')
    return render(request, 'farms/my_farm.html', {
        'farms': farms,
        'active_nav': 'my_farm',
    })


@login_required
def farm_edit(request):
    farm = Farm.objects.filter(owner=request.user).first()

    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            form.save_m2m()
            messages.success(request, f"Farm '{farm.name}' saved successfully.")
            return redirect('farms:my_farm')
    else:
        form = FarmForm(instance=farm)

    return render(request, 'farms/farm_form.html', {
        'form': form,
        'farm': farm,
        'active_nav': 'my_farm',
    })


# ==============================================================================
# Module 2 — Farm History Views
# ==============================================================================

@login_required
def farm_history(request):
    """
    Timeline table grouped by season, with per-planting financial & yield data,
    per-season totals, KPI summaries, and historical trend charts.
    """
    farm = Farm.objects.filter(owner=request.user).first()

    if not farm:
        return render(request, 'farms/farm_history.html', {
            'farm': None,
            'seasons': [],
            'active_nav': 'farm_history',
        })

    seasons_qs = farm.seasons.prefetch_related('plantings__crop').order_by('-start_date')
    seasons_data = []

    all_plantings = []
    total_area_planted = Decimal('0.00')
    total_historical_cost = Decimal('0.00')
    total_historical_revenue = Decimal('0.00')
    has_any_cost = False
    has_any_revenue = False

    for season in seasons_qs:
        plantings = list(season.plantings.all())
        season_area = Decimal('0.00')
        season_cost = Decimal('0.00')
        season_revenue = Decimal('0.00')
        season_has_cost = False
        season_has_revenue = False

        planting_rows = []
        for p in plantings:
            all_plantings.append(p)
            if p.area_ha is not None:
                season_area += p.area_ha
                total_area_planted += p.area_ha

            if p.production_cost_mwk is not None:
                season_cost += p.production_cost_mwk
                total_historical_cost += p.production_cost_mwk
                season_has_cost = True
                has_any_cost = True

            if p.revenue_mwk is not None:
                season_revenue += p.revenue_mwk
                total_historical_revenue += p.revenue_mwk
                season_has_revenue = True
                has_any_revenue = True

            # Yield per hectare
            yield_per_ha = None
            if p.yield_kg is not None and p.area_ha and p.area_ha > 0:
                yield_per_ha = p.yield_kg / p.area_ha

            planting_rows.append({
                'obj': p,
                'yield_per_ha': yield_per_ha,
                'gross_margin': p.gross_margin_mwk,
            })

        season_margin = None
        if season_has_cost and season_has_revenue:
            season_margin = season_revenue - season_cost

        seasons_data.append({
            'season': season,
            'plantings': planting_rows,
            'total_area': season_area,
            'total_cost': season_cost if season_has_cost else None,
            'total_revenue': season_revenue if season_has_revenue else None,
            'total_margin': season_margin,
            'planting_count': len(planting_rows),
        })

    # Overall KPIs
    total_historical_margin = None
    if has_any_cost and has_any_revenue:
        total_historical_margin = total_historical_revenue - total_historical_cost

    # Prepare Chart Data (chronological order: oldest first)
    chronological_seasons = list(reversed(seasons_data))
    chart_labels = [s['season'].name for s in chronological_seasons]

    # Financial margin & cost chart data
    chart_financials = {
        'labels': chart_labels,
        'costs': [float(s['total_cost'] or 0) for s in chronological_seasons],
        'revenues': [float(s['total_revenue'] or 0) for s in chronological_seasons],
        'margins': [float(s['total_margin'] or 0) for s in chronological_seasons],
    }

    # Yield per hectare trend by crop
    crops_in_history = sorted(list({p.crop.name for p in all_plantings}))
    crop_yield_series = []
    crop_palette = ['#8FCB62', '#4FB7D9', '#F2B441', '#E76A6A', '#C5E78B', '#BDE4F1', '#A8BDB0']

    for idx, crop_name in enumerate(crops_in_history):
        yields = []
        for s in chronological_seasons:
            matching = [p for p in s['plantings'] if p['obj'].crop.name == crop_name]
            if matching and matching[0]['yield_per_ha'] is not None:
                yields.append(round(float(matching[0]['yield_per_ha']), 1))
            else:
                yields.append(None)
        crop_yield_series.append({
            'name': crop_name,
            'data': yields,
            'color': crop_palette[idx % len(crop_palette)],
        })

    # Area distribution by crop (total hectares across all plantings)
    area_by_crop = {}
    for p in all_plantings:
        if p.area_ha:
            area_by_crop[p.crop.name] = area_by_crop.get(p.crop.name, Decimal('0')) + p.area_ha

    chart_area = {
        'labels': list(area_by_crop.keys()),
        'values': [float(v) for v in area_by_crop.values()],
        'colors': crop_palette[:len(area_by_crop)],
    }

    context = {
        'farm': farm,
        'seasons': seasons_data,
        'kpi': {
            'seasons_count': len(seasons_data),
            'plantings_count': len(all_plantings),
            'total_area': total_area_planted,
            'total_cost': total_historical_cost if has_any_cost else None,
            'total_revenue': total_historical_revenue if has_any_revenue else None,
            'total_margin': total_historical_margin,
        },
        'chart_financials_json': json.dumps(chart_financials),
        'chart_yield_json': json.dumps({'labels': chart_labels, 'series': crop_yield_series}),
        'chart_area_json': json.dumps(chart_area),
        'active_nav': 'farm_history',
    }
    return render(request, 'farms/farm_history.html', context)


@login_required
def season_create(request):
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        messages.warning(request, "Please register your farm before recording seasons.")
        return redirect('farms:farm_edit')

    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid():
            season = form.save(commit=False)
            season.farm = farm
            season.save()
            messages.success(request, f"Season '{season.name}' added successfully.")
            return redirect('farms:farm_history')
    else:
        form = SeasonForm()

    return render(request, 'farms/season_form.html', {
        'form': form,
        'is_edit': False,
        'active_nav': 'farm_history',
    })


@login_required
def season_edit(request, pk):
    season = get_object_or_404(Season, pk=pk, farm__owner=request.user)

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            messages.success(request, f"Season '{season.name}' updated successfully.")
            return redirect('farms:farm_history')
    else:
        form = SeasonForm(instance=season)

    return render(request, 'farms/season_form.html', {
        'form': form,
        'season': season,
        'is_edit': True,
        'active_nav': 'farm_history',
    })


@login_required
def season_delete(request, pk):
    season = get_object_or_404(Season, pk=pk, farm__owner=request.user)

    if request.method == 'POST':
        name = season.name
        season.delete()
        messages.success(request, f"Season '{name}' and all associated plantings were deleted.")
        return redirect('farms:farm_history')

    return render(request, 'farms/confirm_delete.html', {
        'item_type': 'Season',
        'item_title': season.name,
        'warning_text': f"This will permanently delete '{season.name}' and all {season.plantings.count()} planting record(s) inside it.",
        'cancel_url': 'farms:farm_history',
        'active_nav': 'farm_history',
    })


@login_required
def planting_create(request):
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        messages.warning(request, "Please register your farm before recording plantings.")
        return redirect('farms:farm_edit')

    if not farm.seasons.exists():
        messages.warning(request, "Please create at least one growing season before recording plantings.")
        return redirect('farms:season_create')

    initial = {}
    season_id = request.GET.get('season')
    if season_id:
        initial['season'] = season_id

    if request.method == 'POST':
        form = PlantingForm(request.POST, farm=farm)
        if form.is_valid():
            planting = form.save(commit=False)
            # Double check season belongs to user's farm
            if planting.season.farm != farm:
                messages.error(request, "Invalid season selected.")
                return redirect('farms:farm_history')
            planting.save()
            messages.success(request, f"Planting of {planting.crop.name} added to {planting.season.name}.")
            return redirect('farms:farm_history')
    else:
        form = PlantingForm(farm=farm, initial=initial)

    return render(request, 'farms/planting_form.html', {
        'form': form,
        'is_edit': False,
        'active_nav': 'farm_history',
    })


@login_required
def planting_edit(request, pk):
    planting = get_object_or_404(Planting, pk=pk, season__farm__owner=request.user)
    farm = planting.season.farm

    if request.method == 'POST':
        form = PlantingForm(request.POST, instance=planting, farm=farm)
        if form.is_valid():
            planting = form.save(commit=False)
            if planting.season.farm != farm:
                messages.error(request, "Invalid season selected.")
                return redirect('farms:farm_history')
            planting.save()
            messages.success(request, f"Planting of {planting.crop.name} updated successfully.")
            return redirect('farms:farm_history')
    else:
        form = PlantingForm(instance=planting, farm=farm)

    return render(request, 'farms/planting_form.html', {
        'form': form,
        'planting': planting,
        'is_edit': True,
        'active_nav': 'farm_history',
    })


@login_required
def planting_delete(request, pk):
    planting = get_object_or_404(Planting, pk=pk, season__farm__owner=request.user)

    if request.method == 'POST':
        crop_name = planting.crop.name
        season_name = planting.season.name
        planting.delete()
        messages.success(request, f"Planting of {crop_name} in {season_name} was deleted.")
        return redirect('farms:farm_history')

    return render(request, 'farms/confirm_delete.html', {
        'item_type': 'Planting',
        'item_title': f"{planting.crop.name} ({planting.area_ha} ha in {planting.season.name})",
        'warning_text': f"This will permanently delete this planting record, including its yield and financial history.",
        'cancel_url': 'farms:farm_history',
        'active_nav': 'farm_history',
    })



# ==============================================================================
# Module 7 — Season Review Views
# ==============================================================================

@login_required
def season_review_index(request):
    """
    Overview list of seasons for the user's farm, displaying review status,
    satisfaction ratings, and planned-vs-actual progress.
    """
    farm = Farm.objects.filter(owner=request.user).first()
    if not farm:
        return render(request, 'farms/season_review_index.html', {
            'farm': None,
            'seasons_data': [],
            'active_nav': 'season_review',
        })

    seasons = Season.objects.filter(farm=farm).prefetch_related('plantings__crop', 'review').order_by('-start_date')
    seasons_data = []

    for s in seasons:
        plantings = list(s.plantings.all())
        total_area = sum(p.area_ha for p in plantings)
        total_rev = sum(p.revenue_mwk or Decimal('0') for p in plantings)
        total_cost = sum(p.production_cost_mwk or Decimal('0') for p in plantings)
        total_margin = sum(p.gross_margin_mwk or Decimal('0') for p in plantings if p.gross_margin_mwk is not None)
        has_review = hasattr(s, 'review') and s.review is not None

        seasons_data.append({
            'season': s,
            'planting_count': len(plantings),
            'total_area': total_area,
            'total_rev': total_rev,
            'total_cost': total_cost,
            'total_margin': total_margin,
            'has_review': has_review,
            'review': s.review if has_review else None,
        })

    return render(request, 'farms/season_review_index.html', {
        'farm': farm,
        'seasons_data': seasons_data,
        'active_nav': 'season_review',
    })


@login_required
def season_review_detail(request, season_id):
    """
    Side-by-side comparison of Planned targets vs Actual outcomes for a season.
    Pulls benchmarks from planner.Plan and actual outcomes from plantings.
    """
    season = get_object_or_404(Season, pk=season_id, farm__owner=request.user)
    review = getattr(season, 'review', None)
    plantings = list(season.plantings.select_related('crop').all())

    # Actuals
    actual_area = sum(p.area_ha for p in plantings)
    actual_yield = sum(p.yield_kg or Decimal('0') for p in plantings)
    actual_cost = sum(p.production_cost_mwk or Decimal('0') for p in plantings)
    actual_rev = sum(p.revenue_mwk or Decimal('0') for p in plantings)
    actual_margin = sum(p.gross_margin_mwk or Decimal('0') for p in plantings if p.gross_margin_mwk is not None)

    # Planned
    plan = review.associated_plan if review else None
    planned_items = list(plan.items.select_related('crop').all()) if plan else []

    planned_area = plan.total_land_ha if plan else Decimal('0')
    planned_yield = sum(it.expected_yield_kg_total for it in planned_items) if planned_items else Decimal('0')
    planned_cost = plan.total_expected_cost_mwk if plan else Decimal('0')
    planned_rev = plan.total_expected_revenue_mwk if plan else Decimal('0')
    planned_margin = plan.total_expected_margin_mwk if plan else Decimal('0')

    # Overall Variances
    def calc_delta(actual, planned):
        diff = actual - planned
        pct = (diff / planned * 100) if (planned and planned != 0) else None
        return diff, pct

    area_diff, area_pct = calc_delta(actual_area, planned_area) if plan else (None, None)
    yield_diff, yield_pct = calc_delta(actual_yield, planned_yield) if plan else (None, None)
    cost_diff, cost_pct = calc_delta(actual_cost, planned_cost) if plan else (None, None)
    rev_diff, rev_pct = calc_delta(actual_rev, planned_rev) if plan else (None, None)
    margin_diff, margin_pct = calc_delta(actual_margin, planned_margin) if plan else (None, None)

    # Per-Crop Comparison Grid
    crops_map = {}
    for it in planned_items:
        crops_map[it.crop.id] = {
            'crop': it.crop,
            'planned_area': it.area_ha,
            'planned_yield': it.expected_yield_kg_total,
            'planned_cost': it.expected_total_cost_mwk,
            'planned_rev': it.expected_revenue_mwk,
            'planned_margin': it.expected_gross_margin_mwk,
            'actual_area': Decimal('0'),
            'actual_yield': Decimal('0'),
            'actual_cost': Decimal('0'),
            'actual_rev': Decimal('0'),
            'actual_margin': Decimal('0'),
            'has_actual': False,
            'has_planned': True,
        }

    for p in plantings:
        cid = p.crop.id
        if cid not in crops_map:
            crops_map[cid] = {
                'crop': p.crop,
                'planned_area': Decimal('0'),
                'planned_yield': Decimal('0'),
                'planned_cost': Decimal('0'),
                'planned_rev': Decimal('0'),
                'planned_margin': Decimal('0'),
                'actual_area': Decimal('0'),
                'actual_yield': Decimal('0'),
                'actual_cost': Decimal('0'),
                'actual_rev': Decimal('0'),
                'actual_margin': Decimal('0'),
                'has_actual': True,
                'has_planned': False,
            }
        c_entry = crops_map[cid]
        c_entry['has_actual'] = True
        c_entry['actual_area'] += p.area_ha
        c_entry['actual_yield'] += (p.yield_kg or Decimal('0'))
        c_entry['actual_cost'] += (p.production_cost_mwk or Decimal('0'))
        c_entry['actual_rev'] += (p.revenue_mwk or Decimal('0'))
        c_entry['actual_margin'] += (p.gross_margin_mwk or Decimal('0'))

    crop_comparisons = []
    for item in crops_map.values():
        c_p_area = item['planned_area']
        c_a_area = item['actual_area']
        c_p_yield = item['planned_yield']
        c_a_yield = item['actual_yield']
        c_p_cost = item['planned_cost']
        c_a_cost = item['actual_cost']
        c_p_rev = item['planned_rev']
        c_a_rev = item['actual_rev']
        c_p_margin = item['planned_margin']
        c_a_margin = item['actual_margin']

        item['area_diff'] = c_a_area - c_p_area if item['has_planned'] and item['has_actual'] else None
        item['margin_diff'] = c_a_margin - c_p_margin if item['has_planned'] and item['has_actual'] else None
        item['margin_pct'] = ((c_a_margin - c_p_margin) / abs(c_p_margin) * 100) if (item['has_planned'] and item['has_actual'] and c_p_margin != 0) else None
        crop_comparisons.append(item)

    # Chart data
    chart_labels = [c['crop'].name for c in crop_comparisons]
    chart_planned_margin = [float(c['planned_margin']) for c in crop_comparisons]
    chart_actual_margin = [float(c['actual_margin']) for c in crop_comparisons]

    return render(request, 'farms/season_review_detail.html', {
        'season': season,
        'review': review,
        'plan': plan,
        'plantings': plantings,
        'crop_comparisons': crop_comparisons,
        'totals': {
            'actual_area': actual_area,
            'planned_area': planned_area,
            'area_diff': area_diff,
            'area_pct': area_pct,
            'actual_yield': actual_yield,
            'planned_yield': planned_yield,
            'yield_diff': yield_diff,
            'yield_pct': yield_pct,
            'actual_cost': actual_cost,
            'planned_cost': planned_cost,
            'cost_diff': cost_diff,
            'cost_pct': cost_pct,
            'actual_rev': actual_rev,
            'planned_rev': planned_rev,
            'rev_diff': rev_diff,
            'rev_pct': rev_pct,
            'actual_margin': actual_margin,
            'planned_margin': planned_margin,
            'margin_diff': margin_diff,
            'margin_pct': margin_pct,
        },
        'chart_labels_json': json.dumps(chart_labels),
        'chart_planned_json': json.dumps(chart_planned_margin),
        'chart_actual_json': json.dumps(chart_actual_margin),
        'active_nav': 'season_review',
    })


@login_required
def season_review_edit(request, season_id):
    """Create or update qualitative notes, satisfaction score, and linked plan for a season."""
    season = get_object_or_404(Season, pk=season_id, farm__owner=request.user)
    review = getattr(season, 'review', None)

    if request.method == 'POST':
        form = SeasonReviewForm(request.POST, instance=review, farm=season.farm)
        if form.is_valid():
            review_obj = form.save(commit=False)
            review_obj.season = season
            review_obj.save()
            messages.success(request, f"Season review for '{season.name}' saved.")
            return redirect('farms:season_review_detail', season_id=season.id)
    else:
        form = SeasonReviewForm(instance=review, farm=season.farm)

    return render(request, 'farms/season_review_form.html', {
        'form': form,
        'season': season,
        'review': review,
        'is_edit': review is not None,
        'active_nav': 'season_review',
    })
