"""
journey/management/commands/seed_demo_journey.py
Seeds a realistic demo Season Journey for naffe's Chikondi Farm.
Run with: python manage.py seed_demo_journey
"""
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from farms.models import Farm, Crop
from planner.models import Plan
from journey.models import SeasonJourney, FarmActivityLog, JourneyCheckIn

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo Season Journey data for naffe'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='naffe')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User naffe not found. Run seed_farmers first.'))
            return

        farm = Farm.objects.filter(owner=user).first()
        if not farm:
            self.stdout.write(self.style.ERROR('No farm found for naffe.'))
            return

        plan = Plan.objects.filter(farm=farm).first()

        # Remove old demo journeys for this farm to keep clean
        SeasonJourney.objects.filter(farm=farm, season_label='2025/26').delete()

        # Create active journey
        today = datetime.date.today()
        journey = SeasonJourney.objects.create(
            farm=farm,
            plan=plan,
            season_label='2025/26',
            status='active',
            expected_plant_date=today - datetime.timedelta(days=42),
            expected_harvest_date=today + datetime.timedelta(days=90),
            notes='Demo journey seeded for exhibition.',
        )

        # Backdate activated_at via queryset to simulate 42 days ago
        from django.utils import timezone
        SeasonJourney.objects.filter(pk=journey.pk).update(
            activated_at=timezone.now() - datetime.timedelta(days=42)
        )
        journey.refresh_from_db()

        # Get a maize crop
        maize = Crop.objects.filter(name__icontains='maize').first()
        beans = Crop.objects.filter(name__icontains='bean').first()

        # Seed activity log entries
        activities = [
            {
                'category': 'land_prep', 'activity_date': today - datetime.timedelta(days=50),
                'description': 'Hired tractor for ploughing and harrowing',
                'amount_mwk': 85000, 'is_income': False, 'product_name': 'Tractor hire',
                'quantity': 1, 'unit': 'days',
            },
            {
                'category': 'input', 'activity_date': today - datetime.timedelta(days=45),
                'description': 'Purchased D-Compound basal fertiliser',
                'amount_mwk': 62000, 'is_income': False, 'product_name': 'Optichem D-Compound',
                'quantity': 2, 'unit': 'bags', 'crop': maize,
            },
            {
                'category': 'input', 'activity_date': today - datetime.timedelta(days=43),
                'description': 'Purchased SC403 hybrid maize seed',
                'amount_mwk': 24000, 'is_income': False, 'product_name': 'SC403 Seed',
                'quantity': 2, 'unit': 'kg', 'crop': maize,
            },
            {
                'category': 'planting', 'activity_date': today - datetime.timedelta(days=40),
                'description': 'Planted maize — 1.5 ha at 75cm x 30cm spacing',
                'amount_mwk': 15000, 'is_income': False,
                'quantity': 1.5, 'unit': 'hectares', 'crop': maize,
            },
            {
                'category': 'labour', 'activity_date': today - datetime.timedelta(days=28),
                'description': 'Hired casual labour for first weeding',
                'amount_mwk': 12000, 'is_income': False,
                'quantity': 4, 'unit': 'days',
            },
            {
                'category': 'input', 'activity_date': today - datetime.timedelta(days=14),
                'description': 'Purchased CAN top-dress fertiliser',
                'amount_mwk': 55000, 'is_income': False, 'product_name': 'CAN 23%N',
                'quantity': 2, 'unit': 'bags', 'crop': maize,
            },
            {
                'category': 'management', 'activity_date': today - datetime.timedelta(days=14),
                'description': 'Applied CAN top-dress fertiliser at knee height',
                'amount_mwk': 8000, 'is_income': False,
                'quantity': 1.5, 'unit': 'hectares', 'crop': maize,
            },
            {
                'category': 'pest', 'activity_date': today - datetime.timedelta(days=7),
                'description': 'Scouted and spot-treated Fall Armyworm with Emamectin',
                'amount_mwk': 9500, 'is_income': False, 'product_name': 'Emamectin 1.9EC',
                'quantity': 500, 'unit': 'ml', 'crop': maize,
            },
        ]

        for a in activities:
            crop = a.pop('crop', None)
            FarmActivityLog.objects.create(
                farm=farm, journey=journey, **a, crop=crop
            )

        # Seed weekly check-ins
        checkins = [
            {
                'week_number': 1, 'stage': 'prep', 'pest_pressure': 'none',
                'disease_pressure': 'none', 'moisture_score': 3, 'canopy_cover_pct': 0,
                'notes': 'Field ploughed and harrowed. Basal fertiliser applied.',
                'days_ago': 42,
            },
            {
                'week_number': 2, 'stage': 'germination', 'pest_pressure': 'none',
                'disease_pressure': 'none', 'moisture_score': 4, 'canopy_cover_pct': 15,
                'notes': 'Good germination — 90% emergence. Received 35mm rainfall.',
                'days_ago': 35,
            },
            {
                'week_number': 3, 'stage': 'germination', 'pest_pressure': 'light',
                'disease_pressure': 'none', 'moisture_score': 3, 'canopy_cover_pct': 25,
                'notes': 'Noticed some FAW egg masses. Monitoring closely.',
                'days_ago': 28,
            },
            {
                'week_number': 4, 'stage': 'vegetative', 'pest_pressure': 'moderate',
                'disease_pressure': 'none', 'moisture_score': 3, 'canopy_cover_pct': 40,
                'notes': 'First weeding complete. FAW larvae found. Applied Emamectin.',
                'days_ago': 21,
            },
            {
                'week_number': 5, 'stage': 'vegetative', 'pest_pressure': 'light',
                'disease_pressure': 'none', 'moisture_score': 2, 'canopy_cover_pct': 55,
                'notes': 'Dry spell. Soil moisture dropping. CAN applied at knee height.',
                'days_ago': 14,
            },
            {
                'week_number': 6, 'stage': 'vegetative', 'pest_pressure': 'none',
                'disease_pressure': 'none', 'moisture_score': 3, 'canopy_cover_pct': 70,
                'notes': 'Received 28mm rain. Crop looking healthy. Good canopy cover.',
                'days_ago': 7,
            },
        ]

        from journey.engine import generate_advisory
        from django.utils import timezone as tz

        for c in checkins:
            days_ago = c.pop('days_ago')
            advisory = generate_advisory(
                c['stage'], c['pest_pressure'], c['disease_pressure'],
                c['moisture_score'], c['week_number']
            )
            ci = JourneyCheckIn.objects.create(
                journey=journey, advisory=advisory, **c
            )
            JourneyCheckIn.objects.filter(pk=ci.pk).update(
                checked_in_at=tz.now() - datetime.timedelta(days=days_ago)
            )

        total_spent = sum(a.get('amount_mwk', 0) for a in activities)
        self.stdout.write(self.style.SUCCESS(
            f'Demo journey seeded for {farm.name}. '
            f'{len(activities)} activities (MWK {total_spent:,} spent), '
            f'{len(checkins)} check-ins recorded.'
        ))
