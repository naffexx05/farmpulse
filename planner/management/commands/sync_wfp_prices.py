"""
Management command: sync_wfp_prices
Fetches current agricultural input prices from the WFP VAM Data Bridges API
and updates InputCostBenchmark records for Malawi.

WFP VAM Data Bridges: https://databridges.vam.wfp.org
Register free to get CLIENT_ID and CLIENT_SECRET, then add to .env:
    WFP_CLIENT_ID=your-client-id
    WFP_CLIENT_SECRET=your-client-secret

Run: python manage.py sync_wfp_prices
Run with dry-run: python manage.py sync_wfp_prices --dry-run

WFP commodity IDs for Malawi inputs (from VAM commodity catalogue):
  - Fertilizer (urea)          -> maps to top_dress / basal_fert
  - Fertilizer (NPK compound)  -> maps to basal_fert
  - Seeds (maize)              -> maps to seed for maize
  - Seeds (groundnuts)         -> maps to seed for groundnuts
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

import requests

# ---------------------------------------------------------------------------
# WFP VAM API constants
# ---------------------------------------------------------------------------
WFP_TOKEN_URL  = 'https://api.wfp.org/token'
WFP_PRICES_URL = 'https://api.wfp.org/vam-data-bridges/2.0/MarketPrices/PriceMonthly'

# Malawi country ISO3 code in WFP VAM
MALAWI_ISO3 = 'MWI'

# WFP commodity name substrings -> (input_category, crop_slug or None)
# None means the price applies to ALL crops for that category
WFP_COMMODITY_MAP = [
    # Fertiliser (urea / CAN) -> top_dress for all crops
    ('urea',                    'top_dress',  None),
    ('can ',                    'top_dress',  None),
    ('calcium ammonium nitrate','top_dress',  None),
    # NPK / compound fertiliser -> basal_fert for all crops
    ('npk',                     'basal_fert', None),
    ('compound d',              'basal_fert', None),
    ('compound b',              'basal_fert', None),
    # Seeds
    ('seed maize',              'seed',       'maize'),
    ('maize seed',              'seed',       'maize'),
    ('groundnut seed',          'seed',       'groundnuts'),
    ('soybean seed',            'seed',       'soybeans'),
]

# Crop slugs that should receive the category updates when crop_slug is None
ALL_CROP_SLUGS = ['maize', 'groundnuts', 'soybeans', 'common-beans', 'cassava', 'tobacco']

# Bags are typically 50 kg. WFP prices are per unit (bag). Convert to MWK/ha.
# Application rates per hectare (kg):
#   - Urea/CAN top-dress: 100 kg/ha = 2 bags
#   - NPK basal:          100 kg/ha = 2 bags
#   - Maize seed:          25 kg/ha = 0.5 bag (50 kg bag)
#   - Groundnut seed:      80 kg/ha = 1.6 bags
#   - Soybean seed:        80 kg/ha = 1.6 bags
BAG_KG = 50  # standard 50 kg bag
APPLICATION_RATES_KG_PER_HA = {
    'top_dress': 100,
    'basal_fert': 100,
    ('seed', 'maize'):       25,
    ('seed', 'groundnuts'):  80,
    ('seed', 'soybeans'):    80,
    ('seed', 'common-beans'): 60,
}


def _bags_per_ha(category, crop_slug):
    """Return how many 50 kg bags are needed per hectare."""
    key = (category, crop_slug) if category == 'seed' else category
    kg = APPLICATION_RATES_KG_PER_HA.get(key, 100)
    return kg / BAG_KG


def _get_token(client_id, client_secret):
    """Obtain OAuth2 bearer token from WFP API gateway."""
    resp = requests.post(
        WFP_TOKEN_URL,
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'vamdatabridges_read',
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _fetch_prices(token, country_iso3):
    """Fetch the latest monthly prices for the given country."""
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'CountryCode': country_iso3,
        'page': 1,
        'format': 'json',
    }
    prices = []
    while True:
        resp = requests.get(WFP_PRICES_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items = data.get('items') or data.get('data') or []
        prices.extend(items)
        # Pagination
        total = data.get('totalItems', len(items))
        page_size = data.get('pageSize', len(items)) or 50
        if params['page'] * page_size >= total:
            break
        params['page'] += 1
    return prices


def _match_commodity(commodity_name):
    """Return (input_category, crop_slug_or_None) if commodity is relevant."""
    name_lower = commodity_name.lower()
    for keyword, category, crop_slug in WFP_COMMODITY_MAP:
        if keyword in name_lower:
            return category, crop_slug
    return None, None


class Command(BaseCommand):
    help = (
        'Sync InputCostBenchmark prices from WFP VAM Data Bridges API (Malawi). '
        'Requires WFP_CLIENT_ID and WFP_CLIENT_SECRET in settings/.env.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be updated without saving to the database.',
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

        client_id     = getattr(settings, 'WFP_CLIENT_ID', '')
        client_secret = getattr(settings, 'WFP_CLIENT_SECRET', '')

        if not client_id or not client_secret or \
           client_id == 'PASTE_YOUR_CLIENT_ID_HERE':
            raise CommandError(
                'WFP credentials not configured.\n'
                'Edit your .env file and set:\n'
                '  WFP_CLIENT_ID=<your-client-id>\n'
                '  WFP_CLIENT_SECRET=<your-client-secret>\n'
                'Register free at: https://databridges.vam.wfp.org'
            )

        self.stdout.write('Authenticating with WFP VAM Data Bridges...')
        try:
            token = _get_token(client_id, client_secret)
        except requests.RequestException as e:
            raise CommandError(f'Authentication failed: {e}')

        self.stdout.write('Fetching market prices for Malawi...')
        try:
            raw_prices = _fetch_prices(token, MALAWI_ISO3)
        except requests.RequestException as e:
            raise CommandError(f'Price fetch failed: {e}')

        self.stdout.write(f'Received {len(raw_prices)} price records from WFP VAM.')

        # Group by commodity — take the most recent observation per commodity
        latest = {}  # commodity_name -> price_mwk_per_bag
        for record in raw_prices:
            commodity = record.get('commodityName') or record.get('commodity', {}).get('name', '')
            price     = record.get('price') or record.get('priceValue')
            currency  = record.get('currencyName') or record.get('currency', {}).get('name', 'MWK')
            unit      = record.get('unitName') or record.get('unit', {}).get('name', '').lower()

            if not commodity or price is None:
                continue
            if 'mwk' not in currency.lower() and 'malawi' not in currency.lower():
                continue  # skip non-MWK prices
            if '50' not in unit and 'bag' not in unit and 'kg' not in unit:
                continue  # only process bag/kg units

            # Normalise to MWK per 50kg bag
            price_decimal = Decimal(str(price))
            if 'kg' in unit and '50' not in unit:
                # price per kg — multiply by 50
                price_per_bag = price_decimal * 50
            else:
                price_per_bag = price_decimal

            key = commodity.lower().strip()
            if key not in latest or price_per_bag > latest[key]:
                latest[key] = price_per_bag

        if not latest:
            self.stdout.write(self.style.WARNING(
                'No matching MWK bag prices found in the WFP data. '
                'This can happen if WFP VAM currently has no Malawi input price data. '
                'Benchmark prices from ADMARC/AGORA are unchanged.'
            ))
            return

        updated = 0
        skipped = 0
        now     = timezone.now()

        for commodity_name, price_per_bag in latest.items():
            category, specific_crop_slug = _match_commodity(commodity_name)
            if not category:
                continue

            target_slugs = [specific_crop_slug] if specific_crop_slug else ALL_CROP_SLUGS

            for slug in target_slugs:
                try:
                    crop = Crop.objects.get(slug=slug)
                except Crop.DoesNotExist:
                    continue

                bags = _bags_per_ha(category, slug)
                price_per_ha = price_per_bag * Decimal(str(bags))

                self.stdout.write(
                    f'  {commodity_name[:40]:40s} -> {crop.name:15s} {category:10s} '
                    f'MWK {price_per_bag:,.0f}/bag x {bags:.1f} = MWK {price_per_ha:,.0f}/ha'
                )

                if not dry_run:
                    InputCostBenchmark.objects.filter(
                        crop=crop,
                        input_category=category,
                        season_year=season,
                    ).update(
                        benchmark_price_mwk_per_ha=price_per_ha.quantize(Decimal('1.00')),
                        source_note=f'WFP VAM Data Bridges — {commodity_name[:80]}',
                        data_source='wfp_vam',
                        last_synced_at=now,
                    )
                    updated += 1
                else:
                    skipped += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDry run complete. {skipped} record(s) would be updated. '
                'Run without --dry-run to apply.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\nWFP VAM price sync complete: {updated} benchmark record(s) updated for season {season}.'
            ))

