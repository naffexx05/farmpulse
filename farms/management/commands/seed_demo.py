from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from farms.models import Crop, Farm


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


class Command(BaseCommand):
    help = 'Seed consistent demo data (crops + one demo farm). Safe to re-run.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--owner',
            default='admin',
            help='Username of the farm owner (defaults to "admin").',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        owner_username = options['owner']

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
        try:
            owner = User.objects.get(username=owner_username)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"User '{owner_username}' does not exist. "
                    f"Create it with 'python manage.py createsuperuser' "
                    f"or pass --owner <username>."
                )
            )
            return

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

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))