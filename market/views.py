import json
import statistics
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from farms.models import Crop
from .models import (
    MarketSource, CropPrice, InputCost, TransportCost,
    MarketHub, DailyMarketPrice, MarketPriceForecast,
)
from .services import (
    fetch_live_market_feed_for_hub,
    compute_spatial_arbitrage_for_hub,
    calculate_storage_vs_sale_advisory,
)


@login_required
def sync_market_hub(request, hub_id):
    """
    On-demand synchronization of real-time price surveillance quotes and
    30-day forward forecasts for an agricultural market hub.
    """
    hub = get_object_or_404(MarketHub, hub_id=hub_id)
    crop_slug = request.GET.get('crop', 'maize')

    try:
        result = fetch_live_market_feed_for_hub(hub)
        messages.success(
            request,
            f"Successfully updated live AMIS market quotes ({result['quotes_updated']} price points) "
            f"and 30-day projection curves ({result['forecasts_updated']} forecast horizons) for {hub.name}."
        )
    except Exception as e:
        messages.error(request, f"Could not sync live feed for {hub.name}: {e}")

    redirect_url = reverse('market:dashboard') + f"?tab=prices&hub={hub.hub_id}&crop={crop_slug}"
    return redirect(redirect_url)


@login_required
def market_dashboard(request):
    """
    Market Intelligence Dashboard:
    - Tier 1: Real-time telemetry price quotes and 30-day forward price forecasts by Market Hub.
    - Tier 2: Spatial market arbitrage engine and hermetic bag storage economic advisory.
    - Tier 3: 12-month historical price surveillance across Farmgate, Wholesale, and Retail.
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
    # LIVE MARKET HUBS & TELEMETRY STREAM
    # =========================================================================
    market_hubs = list(MarketHub.objects.filter(is_active=True).select_related('district').order_by('name'))
    selected_hub_id = request.GET.get('hub')
    selected_hub = None
    if market_hubs:
        if selected_hub_id:
            selected_hub = next((h for h in market_hubs if h.hub_id == selected_hub_id), None)
        if not selected_hub:
            selected_hub = market_hubs[0]

    hub_daily_quotes = []
    hub_forecasts = []
    arbitrage_insight = None
    storage_advisory = None

    if selected_hub and selected_crop:
        # Latest daily quotes for the selected hub
        hub_daily_quotes = list(
            DailyMarketPrice.objects.filter(hub=selected_hub)
            .select_related('crop')
            .order_by('-date', 'crop__name')[:12]
        )
        # 30-day forward forecasts for this hub and selected crop
        hub_forecasts = list(
            MarketPriceForecast.objects.filter(hub=selected_hub, crop=selected_crop)
            .order_by('target_date')[:6]
        )
        # Compute spatial market arbitrage viability
        arbitrage_insight = compute_spatial_arbitrage_for_hub(selected_hub, selected_crop)
        # Compute hermetic storage advisory
        storage_advisory = calculate_storage_vs_sale_advisory(selected_hub, selected_crop)

    # =========================================================================
    # TAB 1: PRICES & HISTORICAL TREND DATA
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
        'market_hubs': market_hubs,
        'selected_hub': selected_hub,
        'hub_daily_quotes': hub_daily_quotes,
        'hub_forecasts': hub_forecasts,
        'arbitrage_insight': arbitrage_insight,
        'storage_advisory': storage_advisory,
        'selected_crop_prices': list(reversed(selected_crop_prices)),
        'all_crops_latest_prices': all_crops_latest_prices,
        'variance_stats': variance_stats,
        'chart_price_json': chart_price_json,
        'input_costs_by_crop': input_costs_by_crop,
        'transport_routes': transport_routes,
        'active_nav': 'market',
    }
    return render(request, 'market/dashboard.html', context)


@login_required
def ticker_api(request):
    """
    JSON endpoint for the market price ticker strip on the home dashboard.
    Returns the most recent wholesale (or farmgate) price for each crop,
    along with a synthetic week-on-week change for display purposes.
    """
    from django.http import JsonResponse
    from django.db.models import Max

    crops = Crop.objects.all().order_by('name')
    prices = []
    for crop in crops:
        latest = (
            CropPrice.objects
            .filter(crop=crop)
            .order_by('-year', '-month')
            .first()
        )
        if not latest:
            continue
        price = (
            latest.price_wholesale_mwk
            or latest.price_farmgate_mwk
            or latest.price_retail_mwk
        )
        if not price:
            continue

        # Synthetic week-on-week change (use previous month record if available)
        prev = (
            CropPrice.objects
            .filter(crop=crop)
            .exclude(pk=latest.pk)
            .order_by('-year', '-month')
            .first()
        )
        change = 0.0
        if prev:
            prev_price = (
                prev.price_wholesale_mwk
                or prev.price_farmgate_mwk
                or prev.price_retail_mwk
            )
            if prev_price and prev_price > 0:
                change = round(float((price - prev_price) / prev_price * 100), 1)

        prices.append({
            'crop': crop.name,
            'price': float(price),
            'change': change,
        })

    return JsonResponse({'prices': prices})
