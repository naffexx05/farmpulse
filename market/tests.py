from decimal import Decimal
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from climate.models import District
from farms.models import Crop
from market.models import MarketSource, CropPrice, InputCost, TransportCost


class MarketModelTests(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.district = District.objects.create(name='Lilongwe', slug='lilongwe', region='central')
        self.source = MarketSource.objects.create(
            name='Test AMIS Source',
            attribution='Test Survey',
            is_synthetic=True,
        )

    def test_cropprice_spread_calculations(self):
        price = CropPrice.objects.create(
            crop=self.crop,
            source=self.source,
            year=2024,
            month=5,
            price_farmgate_mwk=Decimal('350.00'),
            price_wholesale_mwk=Decimal('480.00'),
            price_retail_mwk=Decimal('620.00'),
        )
        self.assertEqual(price.wholesale_spread_mwk, Decimal('130.00'))
        self.assertEqual(price.retail_spread_mwk, Decimal('270.00'))

    def test_cropprice_spread_none_when_values_missing(self):
        price = CropPrice.objects.create(
            crop=self.crop,
            source=self.source,
            year=2024,
            month=6,
            price_farmgate_mwk=Decimal('360.00'),
            price_wholesale_mwk=None,
            price_retail_mwk=None,
        )
        self.assertIsNone(price.wholesale_spread_mwk)
        self.assertIsNone(price.retail_spread_mwk)

    def test_cropprice_unique_constraint(self):
        CropPrice.objects.create(
            crop=self.crop,
            district=self.district,
            source=self.source,
            year=2024,
            month=7,
            price_farmgate_mwk=Decimal('340.00'),
        )
        with self.assertRaises(IntegrityError):
            CropPrice.objects.create(
                crop=self.crop,
                district=self.district,
                source=self.source,
                year=2024,
                month=7,
                price_farmgate_mwk=Decimal('350.00'),
            )

    def test_input_cost_creation(self):
        cost = InputCost.objects.create(
            crop=self.crop,
            source=self.source,
            year=2024,
            category='seed',
            item_name='Certified SC403 25kg',
            unit='25 kg bag',
            cost_per_unit_mwk=Decimal('55000.00'),
            units_per_ha_recommended=Decimal('1.00'),
            cost_per_ha_mwk=Decimal('55000.00'),
        )
        self.assertIn('SC403', str(cost))
        self.assertEqual(cost.cost_per_ha_mwk, Decimal('55000.00'))

    def test_transport_cost_creation(self):
        t = TransportCost.objects.create(
            from_location='Lilongwe West',
            to_market='Mitundu',
            distance_km=18,
            cost_per_50kg_bag_mwk=Decimal('1500.00'),
            road_condition='seasonal_earth',
        )
        self.assertEqual(t.cost_per_50kg_bag_mwk, Decimal('1500.00'))


class MarketDashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='marketuser', password='password123')
        self.crop1 = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop2 = Crop.objects.create(name='Groundnuts', slug='groundnuts', category='legume')
        self.source = MarketSource.objects.create(
            name='Test AMIS',
            attribution='Test Attribution',
            is_synthetic=True,
        )

        CropPrice.objects.create(
            crop=self.crop1, source=self.source, year=2024, month=5,
            price_farmgate_mwk=Decimal('350.00'),
            price_wholesale_mwk=Decimal('480.00'),
            price_retail_mwk=Decimal('600.00'),
        )
        CropPrice.objects.create(
            crop=self.crop2, source=self.source, year=2024, month=5,
            price_farmgate_mwk=Decimal('900.00'),
            price_wholesale_mwk=Decimal('1200.00'),
            price_retail_mwk=Decimal('1500.00'),
        )

        self.client = Client()

    def test_login_required(self):
        response = self.client.get(reverse('market:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_prices_tab(self):
        self.client.login(username='marketuser', password='password123')
        response = self.client.get(reverse('market:dashboard') + '?tab=prices&crop=maize')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Market Intelligence')
        self.assertContains(response, 'Farmgate')
        self.assertContains(response, 'Wholesale')
        self.assertContains(response, 'Retail')
        self.assertContains(response, 'Maize')
        self.assertIn('chart_price_json', response.context)

    def test_dashboard_inputs_tab(self):
        self.client.login(username='marketuser', password='password123')
        response = self.client.get(reverse('market:dashboard') + '?tab=inputs')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_tab'], 'inputs')
        self.assertContains(response, 'Itemized Input Costs')

    def test_dashboard_transport_tab(self):
        self.client.login(username='marketuser', password='password123')
        response = self.client.get(reverse('market:dashboard') + '?tab=transport')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_tab'], 'transport')
        self.assertContains(response, 'Transport &amp; Freight Rates')
