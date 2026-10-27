from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from farms.models import Crop, Farm, Planting, Season


class PlantingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testfarmer', password='password123')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Test Farm',
            location_description='Lilongwe',
            total_land_ha=Decimal('5.00'),
        )
        self.crop = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.season = Season.objects.create(
            farm=self.farm,
            name='2024/25 Season',
            start_date=date(2024, 11, 1),
            end_date=date(2025, 4, 30),
        )

    def test_gross_margin_calculation(self):
        planting = Planting.objects.create(
            season=self.season,
            crop=self.crop,
            area_ha=Decimal('1.00'),
            production_cost_mwk=Decimal('200000.00'),
            revenue_mwk=Decimal('550000.00'),
        )
        self.assertEqual(planting.gross_margin_mwk, Decimal('350000.00'))

    def test_gross_margin_none_when_revenue_missing(self):
        planting = Planting.objects.create(
            season=self.season,
            crop=self.crop,
            area_ha=Decimal('1.00'),
            production_cost_mwk=Decimal('200000.00'),
            revenue_mwk=None,
        )
        self.assertIsNone(planting.gross_margin_mwk)

    def test_gross_margin_none_when_cost_missing(self):
        planting = Planting.objects.create(
            season=self.season,
            crop=self.crop,
            area_ha=Decimal('1.00'),
            production_cost_mwk=None,
            revenue_mwk=Decimal('500000.00'),
        )
        self.assertIsNone(planting.gross_margin_mwk)

    def test_season_date_validation(self):
        invalid_season = Season(
            farm=self.farm,
            name='Invalid Season',
            start_date=date(2025, 5, 1),
            end_date=date(2025, 4, 1),  # end before start
        )
        with self.assertRaises(ValidationError):
            invalid_season.full_clean()

    def test_planting_date_validation(self):
        invalid_planting = Planting(
            season=self.season,
            crop=self.crop,
            area_ha=Decimal('1.00'),
            planting_date=date(2025, 1, 10),
            harvest_date=date(2025, 1, 5),  # harvest before planting
        )
        with self.assertRaises(ValidationError):
            invalid_planting.full_clean()


class FarmHistoryViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='farmer1', password='password123')
        self.user2 = User.objects.create_user(username='farmer2', password='password123')

        self.farm1 = Farm.objects.create(
            owner=self.user1,
            name='Green Fields',
            location_description='Lilongwe',
            total_land_ha=Decimal('4.00'),
        )
        self.crop1 = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop2 = Crop.objects.create(name='Groundnuts', slug='groundnuts', category='legume')

        self.season1 = Season.objects.create(
            farm=self.farm1,
            name='2023/24 Rainy Season',
            start_date=date(2023, 11, 1),
            end_date=date(2024, 4, 30),
        )
        self.planting1 = Planting.objects.create(
            season=self.season1,
            crop=self.crop1,
            area_ha=Decimal('1.50'),
            planting_date=date(2023, 11, 15),
            harvest_date=date(2024, 4, 10),
            yield_kg=Decimal('3000.00'),
            production_cost_mwk=Decimal('250000.00'),
            selling_price_mwk_per_kg=Decimal('300.00'),
            revenue_mwk=Decimal('900000.00'),
        )
        self.planting2 = Planting.objects.create(
            season=self.season1,
            crop=self.crop2,
            area_ha=Decimal('0.80'),
            planting_date=date(2023, 12, 1),
            harvest_date=date(2024, 4, 20),
            yield_kg=Decimal('800.00'),
            production_cost_mwk=Decimal('120000.00'),
            selling_price_mwk_per_kg=None,
            revenue_mwk=None,  # missing revenue
        )

        self.client = Client()

    def test_login_required_for_farm_history(self):
        response = self.client.get(reverse('farms:farm_history'))
        self.assertEqual(response.status_code, 302)

    def test_farm_history_read_page(self):
        self.client.login(username='farmer1', password='password123')
        response = self.client.get(reverse('farms:farm_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Farm History')
        self.assertContains(response, '2023/24 Rainy Season')
        self.assertContains(response, 'Maize')
        self.assertContains(response, 'Groundnuts')
        self.assertContains(response, '900,000')
        # Check missing data marker
        self.assertContains(response, '—')
        # Check chart JSON passed in context
        self.assertIn('chart_financials_json', response.context)
        self.assertIn('chart_yield_json', response.context)
        self.assertIn('chart_area_json', response.context)

    def test_season_create_view(self):
        self.client.login(username='farmer1', password='password123')
        response = self.client.post(reverse('farms:season_create'), {
            'name': '2025 Winter Irrigated',
            'start_date': '2025-05-01',
            'end_date': '2025-09-30',
            'notes': 'Test notes',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Season.objects.filter(name='2025 Winter Irrigated', farm=self.farm1).exists())

    def test_season_edit_view(self):
        self.client.login(username='farmer1', password='password123')
        url = reverse('farms:season_edit', kwargs={'pk': self.season1.pk})
        response = self.client.post(url, {
            'name': '2023/24 Updated Season',
            'start_date': '2023-11-01',
            'end_date': '2024-04-30',
            'notes': 'Updated notes',
        })
        self.assertEqual(response.status_code, 302)
        self.season1.refresh_from_db()
        self.assertEqual(self.season1.name, '2023/24 Updated Season')

    def test_season_delete_view(self):
        self.client.login(username='farmer1', password='password123')
        url = reverse('farms:season_delete', kwargs={'pk': self.season1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Season.objects.filter(pk=self.season1.pk).exists())
        # Associated plantings should also be cascade deleted
        self.assertFalse(Planting.objects.filter(pk=self.planting1.pk).exists())

    def test_multi_tenant_isolation_season(self):
        # User 2 should NOT be able to edit or delete User 1's season
        self.client.login(username='farmer2', password='password123')
        edit_url = reverse('farms:season_edit', kwargs={'pk': self.season1.pk})
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

        delete_url = reverse('farms:season_delete', kwargs={'pk': self.season1.pk})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Season.objects.filter(pk=self.season1.pk).exists())

    def test_planting_create_view(self):
        self.client.login(username='farmer1', password='password123')
        response = self.client.post(reverse('farms:planting_create'), {
            'season': self.season1.pk,
            'crop': self.crop1.pk,
            'area_ha': '1.00',
            'planting_date': '2023-11-20',
            'harvest_date': '2024-04-05',
            'yield_kg': '2200.00',
            'production_cost_mwk': '180000.00',
            'selling_price_mwk_per_kg': '350.00',
            'revenue_mwk': '770000.00',
            'notes': 'New planting test',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Planting.objects.filter(notes='New planting test').exists())

    def test_planting_edit_view(self):
        self.client.login(username='farmer1', password='password123')
        url = reverse('farms:planting_edit', kwargs={'pk': self.planting1.pk})
        response = self.client.post(url, {
            'season': self.season1.pk,
            'crop': self.crop1.pk,
            'area_ha': '1.60',
            'planting_date': '2023-11-15',
            'harvest_date': '2024-04-10',
            'yield_kg': '3200.00',
            'production_cost_mwk': '260000.00',
            'selling_price_mwk_per_kg': '320.00',
            'revenue_mwk': '1024000.00',
            'notes': 'Updated yield',
        })
        self.assertEqual(response.status_code, 302)
        self.planting1.refresh_from_db()
        self.assertEqual(self.planting1.area_ha, Decimal('1.60'))
        self.assertEqual(self.planting1.revenue_mwk, Decimal('1024000.00'))

    def test_planting_delete_view(self):
        self.client.login(username='farmer1', password='password123')
        url = reverse('farms:planting_delete', kwargs={'pk': self.planting1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Planting.objects.filter(pk=self.planting1.pk).exists())

    def test_multi_tenant_isolation_planting(self):
        # User 2 should NOT be able to edit or delete User 1's planting
        self.client.login(username='farmer2', password='password123')
        edit_url = reverse('farms:planting_edit', kwargs={'pk': self.planting1.pk})
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

        delete_url = reverse('farms:planting_delete', kwargs={'pk': self.planting1.pk})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Planting.objects.filter(pk=self.planting1.pk).exists())
