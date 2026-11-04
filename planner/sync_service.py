"""
Service module: planner.sync_service
Encapsulates real-time synchronization of agricultural input prices from
the Humanitarian Data Exchange (HDX) / WFP public market price feed for Malawi.

Can be invoked via:
1. Management command: python manage.py sync_wfp_prices
2. Web UI endpoint: POST /planner/sync-input-prices/
3. Scheduled background automation
"""

import csv
import io
import time
from collections import defaultdict
from decimal import Decimal

import requests
from django.utils import timezone
from farms.models import Crop
from planner.models import InputCostBenchmark

# ---------------------------------------------------------------------------
# HDX dataset — Malawi food prices (public, no auth required)
# ---------------------------------------------------------------------------
HDX_DATASET_API = (
    'https://data.humdata.org/api/3/action/package_show'
    '?id=wfp-food-prices-for-malawi'
)
HDX_PRICES_CSV = (
    'https://data.humdata.org/dataset/75ecb747-717e-4ce5-b7af-0e13cc95ba63'
    '/resource/da3ed5da-d6ad-4a86-b4bc-b77e74d01ab7/download/wfp_food_prices_mwi.csv'
)

COMMODITY_MAP = [
    # Fertiliser → top_dress
    ('Fertilizer (CAN)',        'top_dress',  None),
    ('Fertilizer (urea)',       'top_dress',  None),
    # Fertiliser → basal_fert
    ('Fertilizer (D compound)', 'basal_fert', None),
    ('Fertilizer (NPK)',        'basal_fert', None),
    # Seeds
    ('Maize (seed)',            'seed',       'maize'),
]

ALL_CROP_SLUGS = [
    'maize', 'groundnuts', 'soybeans', 'common-beans', 'cassava', 'tobacco'
]

BAG_KG = 50
APPLICATION_RATES_KG_PER_HA = {
    'top_dress':              100,   # 2 × 50 kg bags
    'basal_fert':             100,   # 2 × 50 kg bags
    ('seed', 'maize'):         25,   # 0.5 × 50 kg bag (hybrid)
    ('seed', 'groundnuts'):    80,   # 1.6 bags
    ('seed', 'soybeans'):      80,   # 1.6 bags
    ('seed', 'common-beans'):  60,   # 1.2 bags
    ('seed', 'cassava'):        0,   # cuttings, not bags
    ('seed', 'tobacco'):        0,   # nursery, not bags
}


def _bags_per_ha(category, crop_slug):
    key = (category, crop_slug) if category == 'seed' else category
    kg  = APPLICATION_RATES_KG_PER_HA.get(key, 100)
    return Decimal(str(kg)) / Decimal(str(BAG_KG))


def get_hdx_csv_url():
    """Resolve the latest CSV download URL from the HDX CKAN API."""
    try:
        resp = requests.get(HDX_DATASET_API, timeout=12)
        data = resp.json()
        if data.get('success'):
            for res in data['result']['resources']:
                url = res.get('url', '')
                if 'download' in url and url.endswith('.csv'):
                    return url
    except Exception:
        pass
    return HDX_PRICES_CSV


def fetch_latest_hdx_prices(csv_url):
    """
    Download CSV, return dict:
      commodity_name -> (price_mwk_per_50kg_bag, date_str)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FarmPulse-Malawi/2.5',
        'Accept': 'text/csv,application/csv,text/plain,*/*'
    }

    resp = None
    for attempt in range(4):
        try:
            resp = requests.get(csv_url, headers=headers, timeout=25)
            if resp.status_code == 200 and len(resp.content) > 1000:
                break
            time.sleep(2)
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(2)

    if resp is None:
        raise requests.RequestException("No response received from HDX price server.")
    resp.raise_for_status()

    by_commodity = defaultdict(list)
    reader = csv.DictReader(io.StringIO(resp.text))
    for row in reader:
        if (row.get('currency', '').upper() != 'MWK'
                or row.get('pricetype', '').lower() != 'retail'):
            continue
        commodity = row.get('commodity', '').strip()
        price     = row.get('price', '').strip()
        date      = row.get('date', '').strip()
        unit      = row.get('unit', '').strip().lower()
        if not commodity or not price or not date:
            continue
        by_commodity[commodity].append((date, float(price), unit))

    latest = {}
    for name, records in by_commodity.items():
        records.sort(key=lambda x: x[0], reverse=True)
        date, price_raw, unit = records[0]

        if '50' in unit and ('kg' in unit or 'bag' in unit):
            price_per_bag = Decimal(str(price_raw))
        elif unit == 'kg':
            price_per_bag = Decimal(str(price_raw)) * BAG_KG
        else:
            continue

        latest[name] = (price_per_bag, date)

    return latest


def execute_hdx_price_sync(season_year=2025, dry_run=False):
    """
    Main synchronization routine. Returns a structured result dict.
    Gracefully handles network offline/DNS conditions by preserving
    active ADMARC / AGORA benchmarks.
    """
    csv_url = get_hdx_csv_url()
    try:
        prices = fetch_latest_hdx_prices(csv_url)
    except requests.RequestException as exc:
        return {
            'ok': False,
            'status': 'offline',
            'message': f'Market feed offline or unreachable: {exc}',
            'updated': 0,
            'source': 'ADMARC / AGORA 2025 Benchmark (Preserved)',
            'timestamp': timezone.now().strftime('%d %b %Y, %H:%M'),
        }

    updated = 0
    skipped = 0
    now = timezone.now()
    details = []

    for hdx_name, category, specific_slug in COMMODITY_MAP:
        if hdx_name not in prices:
            continue

        price_per_bag, obs_date = prices[hdx_name]
        target_slugs = [specific_slug] if specific_slug else ALL_CROP_SLUGS

        for slug in target_slugs:
            try:
                crop = Crop.objects.get(slug=slug)
            except Crop.DoesNotExist:
                continue

            bags = _bags_per_ha(category, slug)
            if bags == 0:
                skipped += 1
                continue

            price_per_ha = (price_per_bag * bags).quantize(Decimal('1.00'))

            details.append({
                'crop_slug': slug,
                'category': category,
                'price_per_ha': float(price_per_ha),
                'price_per_bag': float(price_per_bag),
                'obs_date': obs_date,
            })

            if not dry_run:
                rows = InputCostBenchmark.objects.filter(
                    crop=crop,
                    input_category=category,
                    season_year=season_year,
                )
                if rows.exists():
                    rows.update(
                        benchmark_price_mwk_per_ha=price_per_ha,
                        source_note=f'WFP/HDX Market Feed — {hdx_name} (obs. {obs_date})',
                        data_source='wfp_vam',
                        last_synced_at=now,
                    )
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1

    return {
        'ok': True,
        'status': 'synced',
        'updated': updated,
        'skipped': skipped,
        'timestamp': now.strftime('%d %b %Y, %H:%M'),
        'source': 'WFP / HDX Real Market Feed',
        'details': details,
    }

