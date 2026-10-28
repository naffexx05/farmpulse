from decimal import Decimal
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from climate.models import District
from farms.models import Crop
from market.models import (
    MarketSource, CropPrice, InputCost, TransportCost,
    MarketHub, DailyMarketPrice, MarketPriceForecast,
)


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


class LiveMarketHubAndForecastingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='hubtester', password='passwordsync')
        self.client = Client()

        self.district_ll = District.objects.create(name='Lilongwe', slug='lilongwe', region='central')
        self.district_bt = District.objects.create(name='Blantyre', slug='blantyre', region='southern')

        self.crop_maize = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop_soya = Crop.objects.create(name='Soybeans', slug='soybeans', category='legume')

        self.rural_hub = MarketHub.objects.create(
            hub_id='AMIS-LL-MITUNDU-TEST',
            name='Mitundu Aggregation Depot',
            district=self.district_ll,
            hub_type='rural_aggregation',
            latitude=Decimal('-14.166700'),
            longitude=Decimal('33.783300'),
            operating_schedule='Tuesdays & Saturdays',
        )

        self.urban_hub = MarketHub.objects.create(
            hub_id='AMIS-BT-LIMBE-TEST',
            name='Limbe Wholesale Hub',
            district=self.district_bt,
            hub_type='urban_wholesale',
            latitude=Decimal('-15.816700'),
            longitude=Decimal('35.050000'),
            operating_schedule='Daily',
        )

    def test_market_hub_creation_and_str(self):
        self.assertEqual(str(self.rural_hub), "Mitundu Aggregation Depot (AMIS-LL-MITUNDU-TEST) — Lilongwe")
        self.assertTrue(self.rural_hub.is_active)

    def test_daily_market_price_spread_properties(self):
        from datetime import date
        quote = DailyMarketPrice.objects.create(
            hub=self.rural_hub,
            crop=self.crop_maize,
            date=date.today(),
            price_farmgate_mwk=Decimal('350.00'),
            price_wholesale_mwk=Decimal('450.00'),
            price_retail_mwk=Decimal('580.00'),
            volume_traded_bags=300,
            price_trend='rising',
        )
        self.assertEqual(quote.wholesale_spread_mwk, Decimal('100.00'))
        self.assertEqual(quote.retail_spread_mwk, Decimal('230.00'))
        self.assertIn('Mitundu', str(quote))

    def test_live_market_feed_ingestion_service(self):
        from market.services import fetch_live_market_feed_for_hub
        result = fetch_live_market_feed_for_hub(self.rural_hub)

        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['quotes_updated'], 0)
        self.assertGreater(result['forecasts_updated'], 0)

        # Check that quotes were generated for maize
        quotes = DailyMarketPrice.objects.filter(hub=self.rural_hub, crop=self.crop_maize)
        self.assertTrue(quotes.exists())

        # Check that 30-day forecast horizons were generated
        forecasts = MarketPriceForecast.objects.filter(hub=self.rural_hub, crop=self.crop_maize)
        self.assertEqual(forecasts.count(), 4)  # 7, 14, 21, 30 days
        self.assertIsNotNone(self.rural_hub.last_sync)

    def test_spatial_arbitrage_computation(self):
        from datetime import date
        from market.services import compute_spatial_arbitrage_for_hub

        # Create low price at rural hub and high price at urban hub
        DailyMarketPrice.objects.create(
            hub=self.rural_hub,
            crop=self.crop_maize,
            date=date.today(),
            price_farmgate_mwk=Decimal('320.00'),
            price_wholesale_mwk=Decimal('400.00'),
            price_retail_mwk=Decimal('500.00'),
        )
        DailyMarketPrice.objects.create(
            hub=self.urban_hub,
            crop=self.crop_maize,
            date=date.today(),
            price_farmgate_mwk=Decimal('440.00'),
            price_wholesale_mwk=Decimal('550.00'),
            price_retail_mwk=Decimal('680.00'),
        )

        arbitrage = compute_spatial_arbitrage_for_hub(self.rural_hub, self.crop_maize)
        self.assertIsNotNone(arbitrage)
        self.assertEqual(arbitrage['destination_hub'], self.urban_hub)
        self.assertEqual(arbitrage['gross_spread'], Decimal('230.00'))  # 550 - 320
        self.assertGreater(arbitrage['net_profit_kg'], Decimal('100.00'))
        self.assertEqual(arbitrage['viability'], 'STRONGLY VIABLE')

    def test_storage_vs_sale_advisory(self):
        from datetime import date, timedelta
        from market.services import calculate_storage_vs_sale_advisory

        DailyMarketPrice.objects.create(
            hub=self.rural_hub,
            crop=self.crop_maize,
            date=date.today(),
            price_farmgate_mwk=Decimal('350.00'),
            price_wholesale_mwk=Decimal('440.00'),
        )
        MarketPriceForecast.objects.create(
            hub=self.rural_hub,
            crop=self.crop_maize,
            target_date=date.today() + timedelta(days=30),
            horizon_days=30,
            projected_farmgate_mwk=Decimal('450.00'),  # +100 MWK increase
            projected_wholesale_mwk=Decimal('550.00'),
            projected_retail_mwk=Decimal('680.00'),
            market_driver='Lean season drawdown',
        )

        advisory = calculate_storage_vs_sale_advisory(self.rural_hub, self.crop_maize)
        self.assertIsNotNone(advisory)
        self.assertEqual(advisory['action'], 'STORE IN HERMETIC BAGS')
        self.assertGreater(advisory['net_storage_benefit_kg'], Decimal('0.00'))

    def test_sync_market_hub_view(self):
        self.client.login(username='hubtester', password='passwordsync')
        url = reverse('market:sync_market_hub', kwargs={'hub_id': self.rural_hub.hub_id})
        response = self.client.get(url + '?crop=maize')

        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('market:dashboard'), response.url)
        self.assertIn(self.rural_hub.hub_id, response.url)

        # Verify prices exist in DB
        self.assertTrue(DailyMarketPrice.objects.filter(hub=self.rural_hub).exists())

    def test_dashboard_renders_live_hub_telemetry(self):
        from market.services import fetch_live_market_feed_for_hub
        fetch_live_market_feed_for_hub(self.rural_hub)
        fetch_live_market_feed_for_hub(self.urban_hub)

        self.client.login(username='hubtester', password='passwordsync')
        response = self.client.get(reverse('market:dashboard') + f'?tab=prices&hub={self.rural_hub.hub_id}&crop=maize')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live AMIS Price Surveillance')
        self.assertContains(response, 'Mitundu Aggregation Depot')
        self.assertContains(response, 'Sync Live API')
        self.assertContains(response, 'Spatial Arbitrage Analysis')
        self.assertContains(response, 'Storage vs. Sale Advisory')
        self.assertIn('market_hubs', response.context)
        self.assertIn('selected_hub', response.context)
        self.assertIn('hub_daily_quotes', response.context)
        self.assertIn('hub_forecasts', response.context)

