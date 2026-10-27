import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FarmForm, PlantingForm, SeasonForm
from .models import Farm, Planting, Season


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
