import json
import statistics
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from farms.models import Crop
from .models import MarketSource, CropPrice, InputCost, TransportCost


@login_required
def market_dashboard(request):
    """
    Market Intelligence Dashboard:
    - Tab 1 (Prices): 12-month prices for 8 crops with strictly distinguished
      Farmgate (Amber), Wholesale (Green), and Retail (Blue) price points.
    - Tab 2 (Inputs): Certified seeds, basal/top fertilizers, and field labour costs per ha.
    - Tab 3 (Transport): Logistics freight tariffs to assembly and wholesale markets.
    """
    active_tab = request.GET.get('tab', 'prices')
    crops = Crop.objects.all().order_by('name')

    # Selected crop for price trend analysis (default to Maize or query param)
    crop_slug = request.GET.get('crop', 'maize')
    selected_crop = Crop.objects.filter(slug=crop_slug).first() or crops.first()

    sources = MarketSource.objects.all()

    # =========================================================================
    # TAB 1: PRICES & PRICE TREND DATA
    # =========================================================================
    # All 12-month prices for the selected crop ordered chronologically
    selected_crop_prices = list(
        CropPrice.objects.filter(crop=selected_crop)
        .select_related('source', 'district')
        .order_by('year', 'month')
    )

    month_labels = [f"{p.year}-{p.month:02d}" for p in selected_crop_prices]
    fg_series = [float(p.price_farmgate_mwk) if p.price_farmgate_mwk is not None else None for p in selected_crop_prices]
    ws_series = [float(p.price_wholesale_mwk) if p.price_wholesale_mwk is not None else None for p in selected_crop_prices]
    rt_series = [float(p.price_retail_mwk) if p.price_retail_mwk is not None else None for p in selected_crop_prices]

    # Calculate price spread and seasonal pattern statistics for selected crop
    valid_fg = [v for v in fg_series if v is not None]
    valid_ws = [v for v in ws_series if v is not None]

    variance_stats = {
        'avg_farmgate': round(statistics.mean(valid_fg), 1) if valid_fg else None,
        'max_farmgate': max(valid_fg) if valid_fg else None,
        'min_farmgate': min(valid_fg) if valid_fg else None,
        'avg_wholesale': round(statistics.mean(valid_ws), 1) if valid_ws else None,
        'wholesale_margin_pct': None,
        'latest_farmgate': valid_fg[-1] if valid_fg else None,
        'latest_wholesale': valid_ws[-1] if valid_ws else None,
    }
    if variance_stats['avg_farmgate'] and variance_stats['avg_wholesale']:
        spread = variance_stats['avg_wholesale'] - variance_stats['avg_farmgate']
        variance_stats['wholesale_margin_pct'] = round((spread / variance_stats['avg_farmgate']) * 100, 1)

    # Summary table across all crops (latest available price row for each crop)
    all_crops_latest_prices = []
    for c in crops:
        latest = CropPrice.objects.filter(crop=c).order_by('-year', '-month').first()
        prev = CropPrice.objects.filter(crop=c).order_by('-year', '-month')[1:2].first()

        change_pct = None
        if latest and prev and latest.price_farmgate_mwk and prev.price_farmgate_mwk:
            diff = latest.price_farmgate_mwk - prev.price_farmgate_mwk
            change_pct = round((diff / prev.price_farmgate_mwk) * Decimal('100'), 1)

        all_crops_latest_prices.append({
            'crop': c,
            'latest': latest,
            'change_pct': change_pct,
        })

    chart_price_json = json.dumps({
        'crop_name': selected_crop.name if selected_crop else '',
        'labels': month_labels,
        'farmgate': fg_series,
        'wholesale': ws_series,
        'retail': rt_series,
    })

    # =========================================================================
    # TAB 2: INPUTS & COSTS DATA
    # =========================================================================
    # Group inputs by crop
    input_costs_by_crop = []
    for c in crops:
        items = list(InputCost.objects.filter(crop=c).select_related('source'))
        total_ha_cost = sum(i.cost_per_ha_mwk for i in items)
        if items:
            input_costs_by_crop.append({
                'crop': c,
                'items': items,
                'total_ha_cost': total_ha_cost,
            })

    # =========================================================================
    # TAB 3: TRANSPORT TARIFFS DATA
    # =========================================================================
    transport_routes = list(TransportCost.objects.all())

    context = {
        'active_tab': active_tab,
        'crops': crops,
        'selected_crop': selected_crop,
        'sources': sources,
        'selected_crop_prices': list(reversed(selected_crop_prices)),  # newest month first in table
        'all_crops_latest_prices': all_crops_latest_prices,
        'variance_stats': variance_stats,
        'chart_price_json': chart_price_json,
        'input_costs_by_crop': input_costs_by_crop,
        'transport_routes': transport_routes,
        'active_nav': 'market',
    }
    return render(request, 'market/dashboard.html', context)
