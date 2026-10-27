from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from farms.models import Crop, Farm, Season, Planting


CROPS = [
    {
        'name': 'Maize',
        'slug': 'maize',
        'category': 'cereal',
        'scientific_name': 'Zea mays',
        'typical_cycle_days': 120,
        'notes': 'Staple food crop; the most widely grown cereal in Malawi.',
    },
    {
        'name': 'Groundnuts',
        'slug': 'groundnuts',
        'category': 'legume',
        'scientific_name': 'Arachis hypogaea',
        'typical_cycle_days': 130,
        'notes': 'Important cash and food crop; fixes nitrogen in the soil.',
    },
    {
        'name': 'Soybeans',
        'slug': 'soybeans',
        'category': 'legume',
        'scientific_name': 'Glycine max',
        'typical_cycle_days': 110,
        'notes': 'Valuable for soil health and protein; growing market demand.',
    },
    {
        'name': 'Common beans',
        'slug': 'common-beans',
        'category': 'legume',
        'scientific_name': 'Phaseolus vulgaris',
        'typical_cycle_days': 90,
        'notes': 'Short-cycle legume; often intercropped with maize.',
    },
    {
        'name': 'Cassava',
        'slug': 'cassava',
        'category': 'other',
        'scientific_name': 'Manihot esculenta',
        'typical_cycle_days': 300,
        'notes': 'Drought-tolerant root crop; long cycle.',
    },
    {
        'name': 'Rice',
        'slug': 'rice',
        'category': 'cereal',
        'scientific_name': 'Oryza sativa',
        'typical_cycle_days': 140,
        'notes': 'Mostly grown in wetland areas along lake shores.',
    },
    {
        'name': 'Sorghum',
        'slug': 'sorghum',
        'category': 'cereal',
        'scientific_name': 'Sorghum bicolor',
        'typical_cycle_days': 120,
        'notes': 'Drought-tolerant cereal; often grown in drier areas.',
    },
    {
        'name': 'Tobacco',
        'slug': 'tobacco',
        'category': 'cash_crop',
        'scientific_name': 'Nicotiana tabacum',
        'typical_cycle_days': 150,
        'notes': 'Major export crop; requires substantial inputs and labour.',
    },
]

DEMO_FARM = {
    'name': 'Chikondi Farm',
    'location_description': 'Lilongwe District, Central Region',
    'total_land_ha': '2.50',
    'cultivated_land_ha': '2.00',
    'irrigation_type': 'rainfed',
    'soil_type': 'unknown',
    'seasonal_budget_mwk': '450000.00',
    'available_labour_persons': 3,
}

PREFERRED_CROP_SLUGS = ['maize', 'groundnuts']

SEASONS_DATA = [
    {
        'name': '2023/24 Rainy Season',
        'start_date': date(2023, 11, 15),
        'end_date': date(2024, 4, 30),
        'notes': 'Normal onset of rains in late November. Mid-season dry spells in February, but overall good harvest.',
        'plantings': [
            {
                'crop_slug': 'maize',
                'area_ha': Decimal('1.20'),
                'planting_date': date(2023, 11, 20),
                'harvest_date': date(2024, 4, 10),
                'yield_kg': Decimal('2400.00'),
                'production_cost_mwk': Decimal('210000.00'),
                'selling_price_mwk_per_kg': Decimal('350.00'),
                'revenue_mwk': Decimal('840000.00'),
                'notes': 'Hybrid seed variety SC403. Top-dressed with Urea.',
            },
            {
                'crop_slug': 'groundnuts',
                'area_ha': Decimal('0.80'),
                'planting_date': date(2023, 12, 1),
                'harvest_date': date(2024, 4, 20),
                'yield_kg': Decimal('950.00'),
                'production_cost_mwk': Decimal('140000.00'),
                'selling_price_mwk_per_kg': Decimal('900.00'),
                'revenue_mwk': Decimal('855000.00'),
                'notes': 'CG7 variety. Excellent market price achieved in Lilongwe.',
            },
        ],
    },
    {
        'name': '2024/25 Rainy Season',
        'start_date': date(2024, 11, 10),
        'end_date': date(2025, 5, 5),
        'notes': 'Current season. Favourable early rainfall and strong crop establishment.',
        'plantings': [
            {
                'crop_slug': 'maize',
                'area_ha': Decimal('1.00'),
                'planting_date': date(2024, 11, 18),
                'harvest_date': date(2025, 4, 12),
                'yield_kg': Decimal('2100.00'),
                'production_cost_mwk': Decimal('230000.00'),
                'selling_price_mwk_per_kg': Decimal('400.00'),
                'revenue_mwk': Decimal('840000.00'),
                'notes': 'Acreage adjusted to diversify into soybeans.',
            },
            {
                'crop_slug': 'soybeans',
                'area_ha': Decimal('0.80'),
                'planting_date': date(2024, 12, 5),
                'harvest_date': date(2025, 4, 25),
                'yield_kg': Decimal('820.00'),
                'production_cost_mwk': Decimal('125000.00'),
                'selling_price_mwk_per_kg': None,
                'revenue_mwk': None,
                'notes': 'Harvested and bagged. Grain in storage awaiting peak market prices.',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed consistent demo data (crops, farm, seasons, plantings). Safe to re-run.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--owner',
            default=None,
            help='Username of the farm owner (defaults to first user or creates admin).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        owner_username = options.get('owner')

        # --- Crops ----------------------------------------------------------
        created_crops = 0
        for data in CROPS:
            _, created = Crop.objects.get_or_create(slug=data['slug'], defaults=data)
            if created:
                created_crops += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Crops: {created_crops} created, {len(CROPS) - created_crops} already existed.'
            )
        )

        # --- Owner ----------------------------------------------------------
        if owner_username:
            owner = User.objects.filter(username=owner_username).first()
            if not owner:
                self.stderr.write(self.style.ERROR(f"User '{owner_username}' does not exist."))
                return
        else:
            owner = User.objects.first()
            if not owner:
                owner = User.objects.create_superuser('admin', 'admin@farmpulse.mw', 'admin123')
                self.stdout.write(self.style.SUCCESS("Created default superuser 'admin'."))

        self.stdout.write(self.style.SUCCESS(f"Seeding farm data for user: {owner.username}"))

        # --- Farm -----------------------------------------------------------
        farm, farm_created = Farm.objects.get_or_create(
            owner=owner,
            name=DEMO_FARM['name'],
            defaults=DEMO_FARM,
        )

        preferred = Crop.objects.filter(slug__in=PREFERRED_CROP_SLUGS)
        farm.preferred_crops.set(preferred)

        if farm_created:
            self.stdout.write(self.style.SUCCESS(f"Farm '{farm.name}' created for {owner.username}."))
        else:
            self.stdout.write(
                self.style.WARNING(f"Farm '{farm.name}' already existed for {owner.username} — left as-is.")
            )

        # --- Seasons & Plantings --------------------------------------------
        crop_map = {c.slug: c for c in Crop.objects.all()}
        created_seasons = 0
        created_plantings = 0

        for s_data in SEASONS_DATA:
            season, s_created = Season.objects.get_or_create(
                farm=farm,
                name=s_data['name'],
                defaults={
                    'start_date': s_data['start_date'],
                    'end_date': s_data['end_date'],
                    'notes': s_data['notes'],
                },
            )
            if s_created:
                created_seasons += 1

            for p_data in s_data['plantings']:
                crop = crop_map.get(p_data['crop_slug'])
                if not crop:
                    continue
                planting, p_created = Planting.objects.get_or_create(
                    season=season,
                    crop=crop,
                    planting_date=p_data['planting_date'],
                    defaults={
                        'area_ha': p_data['area_ha'],
                        'harvest_date': p_data['harvest_date'],
                        'yield_kg': p_data['yield_kg'],
                        'production_cost_mwk': p_data['production_cost_mwk'],
                        'selling_price_mwk_per_kg': p_data['selling_price_mwk_per_kg'],
                        'revenue_mwk': p_data['revenue_mwk'],
                        'notes': p_data['notes'],
                    },
                )
                if p_created:
                    created_plantings += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seasons: {created_seasons} created. Plantings: {created_plantings} created.'
            )
        )
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
