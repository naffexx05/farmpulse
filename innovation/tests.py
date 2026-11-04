from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from farms.models import Farm, Crop
from innovation.models import SatelliteParcel, ParametricInsurancePolicy


class InnovationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='innovator', password='password123')
        self.crop = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Mzuzu Innovation Hub Farm',
            location_description='Lilongwe, Central Region',
            total_land_ha=Decimal('3.00'),
            cultivated_land_ha=Decimal('2.50'),
            soil_type='sandy_clay_loam',
        )
        self.parcel = SatelliteParcel.objects.create(
            farm=self.farm,
            name='Test Plot A',
            crop=self.crop,
            polygon_geojson=[[33.77, -13.96], [33.78, -13.96], [33.78, -13.97], [33.77, -13.97]],
            centroid_lat=Decimal('-13.965'),
            centroid_lng=Decimal('33.775'),
            calculated_area_ha=Decimal('2.20'),
            mean_ndvi=Decimal('0.71'),
            soil_moisture_pct=Decimal('31.5'),
        )
        self.policy = ParametricInsurancePolicy.objects.create(
            farm=self.farm,
            policy_number='FP-TEST-001',
            crop=self.crop,
            coverage_ha=Decimal('2.00'),
            sum_insured_mwk=Decimal('400000.00'),
            premium_mwk=Decimal('28000.00'),
            trigger_dry_spell_days=14,
            trigger_window_start=date(2024, 12, 15),
            trigger_window_end=date(2025, 1, 30),
            status='active',
            observed_dry_spell_days=6,
        )

    def test_satellite_twin_view(self):
        self.client.login(username='innovator', password='password123')
        response = self.client.get(reverse('innovation:satellite_twin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plot A')
        self.assertContains(response, 'NDVI')
        self.assertEqual(response.context['active_parcel'], self.parcel)

    def test_ussd_simulator_view(self):
        self.client.login(username='innovator', password='password123')
        response = self.client.get(reverse('innovation:ussd_simulator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '*384*77#')

    def test_ussd_api_root_and_submenus(self):
        # Root menu
        r_root = self.client.get(reverse('innovation:ussd_api') + '?text=')
        self.assertEqual(r_root.status_code, 200)
        self.assertTrue(r_root.content.decode('utf-8').startswith('CON FarmPulse'))

        # Option 1: Commodity Prices
        r_prices = self.client.get(reverse('innovation:ussd_api') + '?text=1')
        self.assertEqual(r_prices.status_code, 200)
        self.assertIn('Chimanga', r_prices.content.decode('utf-8'))

        # Option 2: Weather alert
        r_weather = self.client.get(reverse('innovation:ussd_api') + '?text=2')
        self.assertEqual(r_weather.status_code, 200)
        self.assertIn('Lilongwe Weather Alert', r_weather.content.decode('utf-8'))

        # Option 4: Chichewa advisory
        r_adv = self.client.get(reverse('innovation:ussd_api') + '?text=4')
        self.assertEqual(r_adv.status_code, 200)
        self.assertIn('Uphungu wa Nthawi ya Mvula', r_adv.content.decode('utf-8'))

    def test_parametric_insurance_simulation_trigger(self):
        self.client.login(username='innovator', password='password123')
        # Simulate dry spell of 16 days (>= 14 days threshold)
        response = self.client.post(reverse('innovation:parametric_insurance'), {
            'dry_spell_days': 16,
        })
        self.assertEqual(response.status_code, 302)
        self.policy.refresh_from_db()
        self.assertEqual(self.policy.status, 'triggered')
        self.assertEqual(self.policy.payout_mwk, Decimal('400000.00'))
        self.assertTrue(self.policy.transaction_ref.startswith('TX-AIRTEL-MW-'))

    def test_mlimi_advisor_bilingual_view(self):
        self.client.login(username='innovator', password='password123')
        # Chichewa
        res_ch = self.client.get(reverse('innovation:mlimi_advisor') + '?lang=ch')
        self.assertEqual(res_ch.status_code, 200)
        self.assertContains(res_ch, 'Kusamalira Nthaka')

        # English
        res_en = self.client.get(reverse('innovation:mlimi_advisor') + '?lang=en')
        self.assertEqual(res_en.status_code, 200)
        self.assertContains(res_en, 'Soil Health')

    def test_mlimi_chat_api_chichewa_and_english(self):
        self.client.login(username='innovator', password='password123')

        # Test Chichewa planting query
        res_ch = self.client.post(
            reverse('innovation:mlimi_chat_api'),
            data={'message': 'Ndidzale liti chimanga ngati mvula yachedwa?', 'lang': 'ch'},
            content_type='application/json',
        )
        self.assertEqual(res_ch.status_code, 200)
        data_ch = res_ch.json()
        self.assertTrue(data_ch['success'])
        self.assertEqual(data_ch['category'], 'planting_dates')
        self.assertIn('Malangizo', data_ch['reply'])
        self.assertIn('SC 403', data_ch['reply'])
        self.assertTrue(len(data_ch['suggested_followups']) > 0)

        # Test English Break-Even query
        res_en = self.client.post(
            reverse('innovation:mlimi_chat_api'),
            data={'message': 'Is an offered price of MWK 750/kg profitable for my maize crop?', 'lang': 'en'},
            content_type='application/json',
        )
        self.assertEqual(res_en.status_code, 200)
        data_en = res_en.json()
        self.assertTrue(data_en['success'])
        self.assertEqual(data_en['category'], 'break_even_pricing')
        self.assertIn('Economic Verdict', data_en['reply'])
        self.assertIn('750', data_en['reply'])
