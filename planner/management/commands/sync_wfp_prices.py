"""
Management command: sync_wfp_prices
Fetches current agricultural input prices from WFP Malawi food price data
published on the Humanitarian Data Exchange (HDX) — no API key required.

Source: WFP / HDX  — Malawi Food Prices (public dataset)
URL: https://data.humdata.org/dataset/wfp-food-prices-for-malawi

Run: python manage.py sync_wfp_prices
Run with dry-run: python manage.py sync_wfp_prices --dry-run
"""

import csv
import io
from collections import defaultdict
from decimal import Decimal

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# ---------------------------------------------------------------------------
# HDX dataset — Malawi food prices (public, no auth required)
# ---------------------------------------------------------------------------
HDX_DATASET_API = (
    'https://data.humdata.org/api/3/action/package_show'
    '?id=wfp-food-prices-for-malawi'
)
# Fallback direct CSV URL (in case HDX API is slow)
HDX_PRICES_CSV = (
    'https://data.humdata.org/dataset/75ecb747-717e-4ce5-b7af-0e13cc95ba63'
    '/resource/da3ed5da-d6ad-4a86-b4bc-b77e74d01ab7/download/wfp_food_prices_mwi.csv'
)

# ---------------------------------------------------------------------------
# Commodity name  ->  (input_category, crop_slug or None)
# None = applies to all crops in that category
# ---------------------------------------------------------------------------
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

# Application rates per hectare (kg) — to convert bag price → MWK/ha
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


def _get_csv_url():
    """
    Resolve the latest CSV download URL.
    Tries the HDX CKAN API first; falls back to the known direct URL.
    The HDX API may return a page URL instead of the CSV — in that case
    we fall back immediately to the direct download URL.
    """
    try:
        resp = requests.get(HDX_DATASET_API, timeout=15)
        data = resp.json()
        if data.get('success'):
            for res in data['result']['resources']:
                url = res.get('url', '')
                # Accept only direct .csv download links (not dataset page links)
                if 'download' in url and url.endswith('.csv'):
                    return url
    except Exception:
        pass
    return HDX_PRICES_CSV   # fallback direct download


def _fetch_latest_prices(csv_url):
    """
    Download CSV, return dict:
      commodity_name -> (price_mwk_per_50kg_bag, date_str)
    Takes the most recent retail MWK observation per commodity.
    Includes browser User-Agent and retries for HDX CDN 202 status.
    """
    import time
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/csv,text/plain,*/*'
    }

    resp = None
    for attempt in range(5):
        try:
            resp = requests.get(csv_url, headers=headers, timeout=35)
            # HDX may return 202 while CDN caches the file
            if resp.status_code == 200 and len(resp.content) > 1000:
                break
            time.sleep(2)
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2)

    if resp is None:
        raise requests.RequestException("No response received from HDX price server.")
    resp.raise_for_status()

    # Collect all retail MWK rows per commodity
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

    # Keep most recent observation per commodity
    latest = {}
    for name, records in by_commodity.items():
        records.sort(key=lambda x: x[0], reverse=True)
        date, price_raw, unit = records[0]

        # Normalise to MWK per 50 kg bag
        if '50' in unit and ('kg' in unit or 'bag' in unit):
            price_per_bag = Decimal(str(price_raw))
        elif unit == 'kg':
            # price per kg — convert to 50 kg bag equivalent
            price_per_bag = Decimal(str(price_raw)) * BAG_KG
        else:
            # unknown unit — skip
            continue

        latest[name] = (price_per_bag, date)

    return latest


class Command(BaseCommand):
    help = (
        'Sync InputCostBenchmark prices from WFP Malawi food prices '
        '(HDX public dataset — no API key required).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview what would be updated without saving.',
        )
        parser.add_argument(
            '--season', type=int, default=2025,
            help='Season year to update (default: 2025)',
        )

    def handle(self, *args, **options):
        from farms.models import Crop
        from planner.models import InputCostBenchmark

        dry_run = options['dry_run']
        season  = options['season']

        self.stdout.write('Resolving HDX dataset URL...')
        csv_url = _get_csv_url()
        self.stdout.write(f'Downloading: {csv_url[:80]}...')

        try:
            prices = _fetch_latest_prices(csv_url)
        except requests.RequestException as exc:
            self.stdout.write(self.style.WARNING(
                f"\n[Offline/Network Notice] Could not connect to HDX price server: {exc}\n"
                "Retaining current verified ADMARC / AGORA seasonal benchmarks in database."
            ))
            return

        self.stdout.write(
            f'Loaded {len(prices)} retail MWK commodity prices from HDX.\n'
        )

        updated = 0
        skipped = 0
        now     = timezone.now()

        for hdx_name, category, specific_slug in COMMODITY_MAP:
            if hdx_name not in prices:
                self.stdout.write(
                    self.style.WARNING(f'  No data for: {hdx_name}')
                )
                continue

            price_per_bag, obs_date = prices[hdx_name]
            target_slugs = [specific_slug] if specific_slug else ALL_CROP_SLUGS

            for slug in target_slugs:
                try:
                    crop = Crop.objects.get(slug=slug)
                except Crop.DoesNotExist:
                    continue

                bags         = _bags_per_ha(category, slug)
                price_per_ha = (price_per_bag * bags).quantize(Decimal('1.00'))

                if bags == 0:
                    self.stdout.write(
                        f'  {hdx_name:30s} -> {crop.name:15s} {category:10s} '
                        f'SKIP (cutting-based crop, no bag rate)'
                    )
                    skipped += 1
                    continue

                self.stdout.write(
                    f'  {hdx_name:30s} -> {crop.name:15s} {category:10s} '
                    f'MWK {price_per_bag:,.0f}/bag x {bags:.1f} = '
                    f'MWK {price_per_ha:,.0f}/ha  [{obs_date}]'
                )

                if not dry_run:
                    rows = InputCostBenchmark.objects.filter(
                        crop=crop,
                        input_category=category,
                        season_year=season,
                    )
                    if rows.exists():
                        rows.update(
                            benchmark_price_mwk_per_ha=price_per_ha,
                            source_note=(
                                f'WFP/HDX Malawi market prices — {hdx_name} '
                                f'(obs. {obs_date})'
                            ),
                            data_source='wfp_vam',
                            last_synced_at=now,
                        )
                        updated += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    No benchmark row found for '
                                f'{crop.name}/{category}/{season} — skipping'
                            )
                        )
                        skipped += 1
                else:
                    skipped += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDry run complete — {skipped} record(s) would be updated. '
                'Run without --dry-run to apply.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\nHDX price sync complete: {updated} benchmark record(s) '
                f'updated for season {season}.'
            ))
