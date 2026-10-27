from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from climate.models import District
from farms.models import Crop
from market.models import MarketSource, CropPrice, InputCost, TransportCost


# 12 months sequence: Oct 2023 to Sep 2024
MONTHS_SEQUENCE = [
    (2023, 10), (2023, 11), (2023, 12),
    (2024, 1), (2024, 2), (2024, 3),
    (2024, 4), (2024, 5), (2024, 6),
    (2024, 7), (2024, 8), (2024, 9),
]

# Baseline price schedules (farmgate, wholesale, retail) across the 12 months
CROP_PRICE_PROFILES = {
    'maize': {
        # Jan-Mar: lean season peak; May-Jul: harvest dip; Aug-Oct: post-harvest rise
        'base_fg': [420, 450, 480, 520, 540, 510, 360, 320, 330, 350, 380, 400],
        'base_ws': [540, 580, 620, 670, 700, 660, 470, 420, 430, 460, 500, 520],
        'base_rt': [680, 720, 780, 840, 880, 820, 580, 520, 540, 580, 630, 660],
        'notes': 'Staple grain; prices exhibit steep seasonal volatility between harvest glut and lean window.',
    },
    'groundnuts': {
        'base_fg': [950, 980, 1020, 1080, 1120, 1100, 900, 860, 880, 920, 950, 970],
        'base_ws': [1200, 1250, 1300, 1380, 1420, 1400, 1140, 1080, 1100, 1160, 1200, 1240],
        'base_rt': [1500, 1550, 1620, 1700, 1750, 1720, 1420, 1360, 1380, 1450, 1500, 1550],
        'notes': 'High-value confectionery legume with steady urban retail demand in Lilongwe and Blantyre.',
    },
    'soybeans': {
        'base_fg': [720, 740, 780, 820, 850, 830, 680, 650, 660, 690, 710, 730],
        'base_ws': [920, 950, 1000, 1050, 1080, 1060, 880, 830, 850, 880, 910, 930],
        'base_rt': [1150, 1180, 1240, 1300, 1340, 1320, 1100, 1040, 1060, 1100, 1140, 1160],
        'notes': 'Driven by commercial feed and edible oil millers; lower price seasonality than food maize.',
    },
    'common-beans': {
        'base_fg': [1350, 1400, 1480, 1550, 1600, 1580, 1300, 1220, 1250, 1300, 1340, 1380],
        'base_ws': [1680, 1750, 1850, 1920, 1980, 1950, 1620, 1520, 1560, 1620, 1680, 1720],
        'base_rt': [2100, 2180, 2300, 2380, 2450, 2420, 2020, 1900, 1950, 2020, 2100, 2150],
        'notes': 'Premium legume; high urban consumer willingness-to-pay for red mottled and sugar varieties.',
    },
    'cassava': {
        'base_fg': [280, 290, 310, 330, 340, 330, 270, 250, 260, 270, 280, 290],
        'base_ws': [380, 400, 420, 450, 470, 450, 370, 340, 350, 370, 380, 400],
        'base_rt': [500, 520, 550, 580, 600, 580, 480, 450, 460, 480, 500, 520],
        'notes': 'Root crop priced per kg dried chips (makaka); resilient buffer food security crop.',
    },
    'rice': {
        'base_fg': [1200, 1250, 1300, 1380, 1420, 1400, 1180, 1120, 1140, 1180, 1220, 1250],
        'base_ws': [1520, 1580, 1650, 1740, 1800, 1760, 1480, 1420, 1440, 1500, 1540, 1580],
        'base_rt': [1900, 1980, 2050, 2150, 2220, 2180, 1850, 1780, 1800, 1880, 1920, 1960],
        'notes': 'Aromatic Kilombero rice; commanding consistent price premiums across wholesale distributors.',
    },
    'sorghum': {
        'base_fg': [400, 420, 440, 470, 490, 480, 390, 370, 380, 400, 410, 420],
        'base_ws': [520, 550, 570, 610, 630, 620, 510, 480, 490, 520, 530, 550],
        'base_rt': [660, 690, 720, 760, 790, 780, 640, 610, 620, 650, 670, 690],
        'notes': 'Drought security crop; active industrial brewing procurement and local flour processing.',
    },
    'tobacco': {
        # Tobacco auction floors operate primarily April - August. Rest of year has missing values!
        'base_fg': [None, None, None, None, None, None, 2200, 2450, 2600, 2750, None, None],
        'base_ws': [None, None, None, None, None, None, 2900, 3200, 3450, 3600, None, None],
        'base_rt': [None, None, None, None, None, None, None, None, None, None, None, None],
        'notes': 'Auction floor trading (Kanengo Lilongwe, Chinkhoma Kasungu). No domestic consumer retail.',
    },
}

INPUT_COSTS_DATA = [
    # Maize
    {'crop_slug': 'maize', 'cat': 'seed', 'item': 'Hybrid Maize SC403 (25 kg)', 'unit': '25 kg bag', 'unit_cost': 55000, 'rate': 1, 'ha_cost': 55000},
    {'crop_slug': 'maize', 'cat': 'fertilizer_basal', 'item': 'Basal Fertiliser NPK 23:10:5 (50 kg)', 'unit': '50 kg bag', 'unit_cost': 92000, 'rate': 2, 'ha_cost': 184000},
    {'crop_slug': 'maize', 'cat': 'fertilizer_top', 'item': 'Top Dressing Urea (50 kg)', 'unit': '50 kg bag', 'unit_cost': 88000, 'rate': 2, 'ha_cost': 176000},
    {'crop_slug': 'maize', 'cat': 'chemical', 'item': 'Fall Armyworm Insecticide (Ampligo/Belt)', 'unit': '250 ml pack', 'unit_cost': 18000, 'rate': 2, 'ha_cost': 36000},
    {'crop_slug': 'maize', 'cat': 'labour', 'item': 'Land Prep, Ridging & Planting Labour', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 24, 'ha_cost': 84000},
    {'crop_slug': 'maize', 'cat': 'labour', 'item': 'Weeding, Fertiliser Application & Harvesting', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 28, 'ha_cost': 98000},

    # Groundnuts
    {'crop_slug': 'groundnuts', 'cat': 'seed', 'item': 'Certified CG7 Seed (80 kg)', 'unit': '80 kg bag', 'unit_cost': 115000, 'rate': 1, 'ha_cost': 115000},
    {'crop_slug': 'groundnuts', 'cat': 'fertilizer_basal', 'item': 'Agricultural Gypsum (Calcium sulphate)', 'unit': '50 kg bag', 'unit_cost': 38000, 'rate': 2, 'ha_cost': 76000},
    {'crop_slug': 'groundnuts', 'cat': 'chemical', 'item': 'Early Leaf Spot Fungicide (Mancozeb)', 'unit': '1 kg pack', 'unit_cost': 16000, 'rate': 2, 'ha_cost': 32000},
    {'crop_slug': 'groundnuts', 'cat': 'labour', 'item': 'Ridging, Planting & Double Weeding', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 26, 'ha_cost': 91000},
    {'crop_slug': 'groundnuts', 'cat': 'labour', 'item': 'Harvesting, Lifting, Plucking & Stripping', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 32, 'ha_cost': 112000},

    # Soybeans
    {'crop_slug': 'soybeans', 'cat': 'seed', 'item': 'Certified Tikolore Seed (60 kg)', 'unit': '60 kg pack', 'unit_cost': 85000, 'rate': 1, 'ha_cost': 85000},
    {'crop_slug': 'soybeans', 'cat': 'chemical', 'item': 'Rhizobium Bio-Inoculant', 'unit': 'packet', 'unit_cost': 7500, 'rate': 4, 'ha_cost': 30000},
    {'crop_slug': 'soybeans', 'cat': 'labour', 'item': 'Field Operations (Planting, Weeding, Thrashing)', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 35, 'ha_cost': 122500},

    # Common beans
    {'crop_slug': 'common-beans', 'cat': 'seed', 'item': 'Certified Kholophethe / Sugar Seed (60 kg)', 'unit': '60 kg pack', 'unit_cost': 110000, 'rate': 1, 'ha_cost': 110000},
    {'crop_slug': 'common-beans', 'cat': 'fertilizer_basal', 'item': 'NPK Basal Blend (50 kg)', 'unit': '50 kg bag', 'unit_cost': 92000, 'rate': 1, 'ha_cost': 92000},
    {'crop_slug': 'common-beans', 'cat': 'labour', 'item': 'Hand Weeding, Staking & Pod Harvesting', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 30, 'ha_cost': 105000},

    # Cassava
    {'crop_slug': 'cassava', 'cat': 'seed', 'item': 'Disease-Free Cassava Cuttings (Manyokola)', 'unit': 'bundles', 'unit_cost': 2500, 'rate': 40, 'ha_cost': 100000},
    {'crop_slug': 'cassava', 'cat': 'labour', 'item': 'Mound Formation & Weeding', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 32, 'ha_cost': 112000},

    # Rice
    {'crop_slug': 'rice', 'cat': 'seed', 'item': 'Certified Kilombero Paddy Seed (50 kg)', 'unit': '50 kg pack', 'unit_cost': 75000, 'rate': 1, 'ha_cost': 75000},
    {'crop_slug': 'rice', 'cat': 'fertilizer_basal', 'item': 'Basal D-Compound (50 kg)', 'unit': '50 kg bag', 'unit_cost': 92000, 'rate': 2, 'ha_cost': 184000},
    {'crop_slug': 'rice', 'cat': 'fertilizer_top', 'item': 'Urea Top Dressing (50 kg)', 'unit': '50 kg bag', 'unit_cost': 88000, 'rate': 2, 'ha_cost': 176000},
    {'crop_slug': 'rice', 'cat': 'labour', 'item': 'Nursery, Bunding, Transplanting & Thrashing', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 48, 'ha_cost': 168000},

    # Sorghum
    {'crop_slug': 'sorghum', 'cat': 'seed', 'item': 'Improved Sorghum Seed Pilira 1 (10 kg)', 'unit': '10 kg pack', 'unit_cost': 22000, 'rate': 1, 'ha_cost': 22000},
    {'crop_slug': 'sorghum', 'cat': 'labour', 'item': 'Planting, Thinning, Bird Scaring & Harvest', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 28, 'ha_cost': 98000},

    # Tobacco
    {'crop_slug': 'tobacco', 'cat': 'seed', 'item': 'Flue/Burley Seed & Nursery Trays', 'unit': 'packet/set', 'unit_cost': 45000, 'rate': 1, 'ha_cost': 45000},
    {'crop_slug': 'tobacco', 'cat': 'fertilizer_basal', 'item': 'Tobacco Basal Compound C (50 kg)', 'unit': '50 kg bag', 'unit_cost': 98000, 'rate': 3, 'ha_cost': 294000},
    {'crop_slug': 'tobacco', 'cat': 'fertilizer_top', 'item': 'CAN (Calcium Ammonium Nitrate) (50 kg)', 'unit': '50 kg bag', 'unit_cost': 86000, 'rate': 2, 'ha_cost': 172000},
    {'crop_slug': 'tobacco', 'cat': 'labour', 'item': 'Nursery, Transplant, De-suckering, Curing & Grading', 'unit': 'man-days', 'unit_cost': 3500, 'rate': 65, 'ha_cost': 227500},
]

TRANSPORT_ROUTES = [
    {
        'from': 'Rural Farmgate (Lilongwe West)',
        'to': 'Mitundu Assembly Market',
        'distance_km': 18,
        'cost_50kg': Decimal('1500.00'),
        'cost_ton_km': Decimal('1660.00'),
        'road': 'seasonal_earth',
        'notes': 'Feeder earth road. Transports grain via pick-up trucks and ox-carts during harvest.',
    },
    {
        'from': 'Mitundu Assembly Market',
        'to': 'Lilongwe Central Wholesale (Mchesi)',
        'distance_km': 35,
        'cost_50kg': Decimal('1800.00'),
        'cost_ton_km': Decimal('1028.00'),
        'road': 'good_tarred',
        'notes': 'Paved M1 highway access. 5-ton and 10-ton lorries.',
    },
    {
        'from': 'Rural Kasungu (Chulu)',
        'to': 'Kasungu Boma Grain Depot',
        'distance_km': 28,
        'cost_50kg': Decimal('2000.00'),
        'cost_ton_km': Decimal('1428.00'),
        'road': 'seasonal_earth',
        'notes': 'Sandy tracks during wet season; standard rate per bag.',
    },
    {
        'from': 'Kasungu Boma Hub',
        'to': 'Lilongwe Terminal Produce Hub',
        'distance_km': 130,
        'cost_50kg': Decimal('3800.00'),
        'cost_ton_km': Decimal('584.00'),
        'road': 'good_tarred',
        'notes': 'Long-haul inter-district bulk logistics.',
    },
    {
        'from': 'Salima Lakeshore (Chipoka)',
        'to': 'Lilongwe Urban Market',
        'distance_km': 115,
        'cost_50kg': Decimal('3500.00'),
        'cost_ton_km': Decimal('608.00'),
        'road': 'good_tarred',
        'notes': 'Transport for lakeshore rice, cassava chips, and fish products into the capital.',
    },
    {
        'from': 'Shire Highlands (Mulanje/Thyolo)',
        'to': 'Blantyre Limbe Produce Market',
        'distance_km': 65,
        'cost_50kg': Decimal('2600.00'),
        'cost_ton_km': Decimal('800.00'),
        'road': 'good_tarred',
        'notes': 'High-volume southern trading route.',
    },
]


class Command(BaseCommand):
    help = 'Seed 12 months of prices for 8 crops × 3 market types, input costs, and transport rates.'

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Market Sources
        source_amis, _ = MarketSource.objects.get_or_create(
            name='Ministry of Agriculture AMIS & Market Price Monitor (Synthetic Survey)',
            defaults={
                'attribution': 'Synthetic calibration based on Agricultural Market Information System (AMIS) weekly commodity price surveys in major Malawian trading hubs (2023–2024).',
                'citation_url': 'https://www.amis.gov.mw',
                'is_synthetic': True,
            }
        )

        source_inputs, _ = MarketSource.objects.get_or_create(
            name='National Agro-Dealers Association & AISAM Survey (2024 Benchmark)',
            defaults={
                'attribution': 'Itemized agronomic inputs and commercial fertilizer benchmarks compiled across certified agro-input dealers in Central Region, Malawi.',
                'is_synthetic': True,
            }
        )

        crop_map = {c.slug: c for c in Crop.objects.all()}
        created_prices = 0

        # 2. Crop Prices (12 months × 8 crops)
        for crop_slug, profile in CROP_PRICE_PROFILES.items():
            crop = crop_map.get(crop_slug)
            if not crop:
                continue

            for idx, (year, month) in enumerate(MONTHS_SEQUENCE):
                fg = profile['base_fg'][idx]
                ws = profile['base_ws'][idx]
                rt = profile['base_rt'][idx]

                _, created = CropPrice.objects.get_or_create(
                    crop=crop,
                    district=None,  # National average benchmark
                    year=year,
                    month=month,
                    defaults={
                        'source': source_amis,
                        'price_farmgate_mwk': Decimal(str(fg)) if fg is not None else None,
                        'price_wholesale_mwk': Decimal(str(ws)) if ws is not None else None,
                        'price_retail_mwk': Decimal(str(rt)) if rt is not None else None,
                        'market_name': 'National Average Benchmark',
                        'notes': profile['notes'],
                    }
                )
                if created:
                    created_prices += 1

        # 3. Input Costs
        created_inputs = 0
        for item in INPUT_COSTS_DATA:
            crop = crop_map.get(item['crop_slug'])
            if not crop:
                continue

            _, created = InputCost.objects.get_or_create(
                crop=crop,
                item_name=item['item'],
                defaults={
                    'source': source_inputs,
                    'year': 2024,
                    'category': item['cat'],
                    'unit': item['unit'],
                    'cost_per_unit_mwk': Decimal(str(item['unit_cost'])),
                    'units_per_ha_recommended': Decimal(str(item['rate'])),
                    'cost_per_ha_mwk': Decimal(str(item['ha_cost'])),
                }
            )
            if created:
                created_inputs += 1

        # 4. Transport Tariffs
        created_transports = 0
        for route in TRANSPORT_ROUTES:
            _, created = TransportCost.objects.get_or_create(
                from_location=route['from'],
                to_market=route['to'],
                defaults={
                    'distance_km': route['distance_km'],
                    'cost_per_50kg_bag_mwk': route['cost_50kg'],
                    'cost_per_ton_km_mwk': route['cost_ton_km'],
                    'road_condition': route['road'],
                    'notes': route['notes'],
                }
            )
            if created:
                created_transports += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded Market Intelligence: {created_prices} price records, {created_inputs} input items, {created_transports} transport tariffs."
            )
        )
