from decimal import Decimal
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from climate.models import District, ClimateSource, ClimateRecord
from climate.risk import calculate_climate_risks


class ClimateModelTests(TestCase):
    def setUp(self):
        self.district = District.objects.create(
            name='Lilongwe',
            slug='lilongwe',
            region='central',
            elevation_m=1050,
        )
        self.source = ClimateSource.objects.create(
            name='Test DCCMS Source',
            source_type='historical_observed',
            attribution='Test attribution',
            is_synthetic=True,
        )

    def test_district_str(self):
        self.assertEqual(str(self.district), 'Lilongwe (Central Region)')

    def test_climate_source_str(self):
        self.assertEqual(str(self.source), 'Test DCCMS Source [Synthetic]')

    def test_climate_record_unique_together(self):
        ClimateRecord.objects.create(
            district=self.district,
            source=self.source,
            record_type='historical',
            year=2024,
            month=1,
            rainfall_mm=Decimal('200.0'),
        )
        # Attempting duplicate for same district, year, month, and record_type must raise IntegrityError
        with self.assertRaises(IntegrityError):
            ClimateRecord.objects.create(
                district=self.district,
                source=self.source,
                record_type='historical',
                year=2024,
                month=1,
                rainfall_mm=Decimal('210.0'),
            )


class ClimateRiskScoringTests(TestCase):
    def setUp(self):
        self.district = District.objects.create(
            name='Kasungu',
            slug='kasungu',
            region='central',
            elevation_m=1030,
        )
        self.source = ClimateSource.objects.create(
            name='Test Source',
            source_type='historical_observed',
            attribution='Test attribution',
            is_synthetic=True,
        )

    def test_insufficient_data_state_never_fakes_low_risk(self):
        """CRITICAL: Empty or sparse data must yield 'Insufficient Data', NOT 'Low'."""
        risks = calculate_climate_risks(self.district, records=[])
        self.assertEqual(risks['rainfall']['level'], 'Insufficient Data')
        self.assertEqual(risks['dry_spell']['level'], 'Insufficient Data')
        self.assertEqual(risks['heat']['level'], 'Insufficient Data')
        self.assertEqual(risks['composite']['level'], 'Insufficient Data')
        self.assertIsNone(risks['rainfall']['score'])
        self.assertIsNone(risks['dry_spell']['score'])

    def test_insufficient_data_with_sparse_records(self):
        """Only 2 rainy months recorded must still be Insufficient Data."""
        r1 = ClimateRecord.objects.create(
            district=self.district, source=self.source, record_type='historical',
            year=2024, month=1, rainfall_mm=Decimal('150.0'), dry_spell_days_max=4, temp_max_c=Decimal('27.0')
        )
        r2 = ClimateRecord.objects.create(
            district=self.district, source=self.source, record_type='historical',
            year=2024, month=2, rainfall_mm=Decimal('180.0'), dry_spell_days_max=5, temp_max_c=Decimal('28.0')
        )
        risks = calculate_climate_risks(self.district)
        self.assertEqual(risks['rainfall']['level'], 'Insufficient Data')
        self.assertEqual(risks['dry_spell']['level'], 'Insufficient Data')
        self.assertEqual(risks['heat']['level'], 'Insufficient Data')

    def test_sufficient_data_risk_computation(self):
        """When complete 3-year data exists, computes valid risk levels."""
        records = []
        for year in [2022, 2023, 2024]:
            for m in range(1, 13):
                records.append(ClimateRecord(
                    district=self.district,
                    source=self.source,
                    record_type='historical',
                    year=year,
                    month=m,
                    rainfall_mm=Decimal('180.0') if m in [11, 12, 1, 2, 3] else Decimal('5.0'),
                    dry_spell_days_max=16 if m in [1, 2] else 4,  # high dry spell in Jan/Feb
                    temp_max_c=Decimal('34.0') if m in [10, 11] else Decimal('27.0'),
                    heat_wave_days=6 if m in [10, 11] else 0,
                ))
        ClimateRecord.objects.bulk_create(records)

        risks = calculate_climate_risks(self.district)
        # Jan/Feb dry spells of 16 days should yield High dry spell risk
        self.assertIn(risks['dry_spell']['level'], ['High', 'Medium'])
        self.assertFalse(risks['dry_spell']['is_insufficient'])
        # Heat risk evaluated
        self.assertNotEqual(risks['heat']['level'], 'Insufficient Data')


class ClimateDashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='climatedev', password='password123')
        self.district1 = District.objects.create(
            name='Lilongwe', slug='lilongwe', region='central', elevation_m=1050
        )
        self.district2 = District.objects.create(
            name='Salima', slug='salima', region='central', elevation_m=490
        )
        self.source = ClimateSource.objects.create(
            name='DCCMS Test', source_type='historical_observed',
            attribution='Test DCCMS', is_synthetic=True
        )

        # Create sample records
        ClimateRecord.objects.create(
            district=self.district1, source=self.source, record_type='historical',
            year=2024, month=1, rainfall_mm=Decimal('220.0'), temp_max_c=Decimal('28.5')
        )
        ClimateRecord.objects.create(
            district=self.district1, source=self.source, record_type='outlook',
            year=2024, month=11, rainfall_mm=Decimal('70.0'), temp_max_c=Decimal('29.0')
        )

        self.client = Client()

    def test_login_required(self):
        response = self.client.get(reverse('climate:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_logged_in_user(self):
        self.client.login(username='climatedev', password='password123')
        response = self.client.get(reverse('climate:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Climate Intelligence')
        self.assertContains(response, 'Lilongwe')
        self.assertContains(response, 'Data Provenance')
        self.assertContains(response, 'Historical Observations')
        self.assertContains(response, '2024/25 Official Outlook')
        self.assertContains(response, 'Illustrative Scenario')
        self.assertIn('chart_rainfall_json', response.context)
        self.assertIn('chart_temp_json', response.context)
        self.assertIn('chart_heat_json', response.context)

    def test_district_switching(self):
        self.client.login(username='climatedev', password='password123')
        response = self.client.get(reverse('climate:dashboard') + '?district=salima')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_district'].slug, 'salima')
        self.assertContains(response, 'Salima')
