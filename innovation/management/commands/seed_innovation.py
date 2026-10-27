from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from farms.models import Farm, Crop
from innovation.models import SatelliteParcel, ParametricInsurancePolicy


class Command(BaseCommand):
    help = "Seed initial demonstration satellite parcels and parametric insurance policy."

    def handle(self, *args, **options):
        farm = Farm.objects.first()
        if not farm:
            self.stdout.write(self.style.WARNING("No farm exists. Run seed_demo first."))
            return

        maize = Crop.objects.filter(slug='maize').first() or Crop.objects.first()

        # 1. Seed Satellite Parcel (Lilongwe agricultural test plot)
        # GeoJSON coordinates for a ~2.4 ha rectangular plot in Nathenje / Lilongwe
        coords = [
            [33.7725, -13.9610],
            [33.7760, -13.9612],
            [33.7758, -13.9645],
            [33.7722, -13.9642],
            [33.7725, -13.9610],
        ]

        parcel, created = SatelliteParcel.objects.get_or_create(
            farm=farm,
            name="Lilongwe East Main Field (Parcel #1)",
            defaults={
                'crop': maize,
                'polygon_geojson': coords,
                'centroid_lat': Decimal('-13.9627'),
                'centroid_lng': Decimal('33.7741'),
                'calculated_area_ha': Decimal('2.45'),
                'mean_ndvi': Decimal('0.68'),
                'soil_moisture_pct': Decimal('29.4'),
                'stress_level': 'optimal',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Satellite Parcel: {parcel.name}"))
        else:
            self.stdout.write(f"Satellite Parcel already exists: {parcel.name}")

        # 2. Seed Parametric Insurance Policy
        policy, pol_created = ParametricInsurancePolicy.objects.get_or_create(
            farm=farm,
            policy_number="FP-MW-2024-0891",
            defaults={
                'crop': maize,
                'coverage_ha': Decimal('2.00'),
                'sum_insured_mwk': Decimal('500000.00'),
                'premium_mwk': Decimal('35000.00'),
                'trigger_dry_spell_days': 14,
                'trigger_window_start': date(2024, 12, 15),
                'trigger_window_end': date(2025, 1, 30),
                'status': 'active',
                'observed_dry_spell_days': 8,
                'payout_mwk': Decimal('0.00'),
                'mobile_money_provider': 'Airtel Money',
                'payout_recipient_phone': '+265 99 712 3456',
            }
        )
        if pol_created:
            self.stdout.write(self.style.SUCCESS(f"Created Parametric Policy: {policy.policy_number}"))
        else:
            self.stdout.write(f"Parametric Policy already exists: {policy.policy_number}")
