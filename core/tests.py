import json
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from core.models import UserProfile, get_user_profile
from farms.models import Farm, Season, Planting, Crop
from climate.models import District, ClimateSource, ClimateRecord
from planner.models import Plan, PlanItem


class CoreAndAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='chifundo',
            email='chifundo@farmpulse.mw',
            password='secretpassword123',
            first_name='Chifundo',
            last_name='Banda',
        )
        self.profile = get_user_profile(self.user)

        self.district = District.objects.create(
            name='Lilongwe',
            slug='lilongwe',
            region='central',
            elevation_m=1050,
        )
        self.source = ClimateSource.objects.create(name='DCCMS Test', source_type='historical_observed')

        # Climate records for chart
        for m in range(1, 13):
            ClimateRecord.objects.create(
                district=self.district,
                source=self.source,
                year=2024,
                month=m,
                rainfall_mm=Decimal('120.0') if m in [1, 2, 3, 11, 12] else Decimal('5.0'),
                temp_max_c=Decimal('28.5'),
                temp_min_c=Decimal('16.0'),
                heat_wave_days=2 if m in [10, 11] else 0,
            )

        self.crop1 = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Chitukuko Farm',
            location_description='Lilongwe, Central Region',
            total_land_ha=Decimal('3.50'),
            cultivated_land_ha=Decimal('3.00'),
            irrigation_type='rainfed',
            seasonal_budget_mwk=Decimal('450000.00'),
            available_labour_persons=4,
        )
        self.season = Season.objects.create(
            farm=self.farm,
            name='2024/25 Rainy Season',
            start_date=date(2024, 11, 1),
            end_date=date(2025, 4, 30),
        )
        self.planting = Planting.objects.create(
            season=self.season,
            crop=self.crop1,
            area_ha=Decimal('2.00'),
            yield_kg=Decimal('4500.00'),
            production_cost_mwk=Decimal('280000.00'),
            revenue_mwk=Decimal('1250000.00'),
        )
        self.plan = Plan.objects.create(
            farm=self.farm,
            name='Resilient Plan 2024/25',
            strategy_type='balanced',
            status='active',
            total_land_ha=Decimal('2.50'),
            total_expected_cost_mwk=Decimal('320000.00'),
            total_expected_revenue_mwk=Decimal('1400000.00'),
            total_expected_margin_mwk=Decimal('1080000.00'),
        )
        self.plan_item = PlanItem.objects.create(
            plan=self.plan,
            crop=self.crop1,
            area_ha=Decimal('2.00'),
            expected_yield_kg_per_ha=Decimal('2200.00'),
            expected_yield_kg_total=Decimal('4400.00'),
            expected_cost_per_ha_mwk=Decimal('150000.00'),
            expected_total_cost_mwk=Decimal('300000.00'),
            expected_selling_price_mwk_per_kg=Decimal('318.18'),
            expected_revenue_mwk=Decimal('1400000.00'),
            expected_gross_margin_mwk=Decimal('1100000.00'),
            break_even_price_mwk_per_kg=Decimal('68.18'),
        )

    # 1. Overview Dashboard
    def test_home_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_home_authenticated_renders_dashboard(self):
        self.client.login(username='chifundo', password='secretpassword123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chitukuko Farm')
        self.assertContains(response, 'Good morning, Chifundo')
        self.assertContains(response, 'Climate Risk Overview')
        self.assertContains(response, 'Seasonal Agro-Climatic Profile')
        self.assertContains(response, 'Active Portfolio')
        self.assertEqual(response.context['recent_perf']['yield'], Decimal('4500.00'))

    # 2. Settings Views
    def test_settings_index_tabs(self):
        self.client.login(username='chifundo', password='secretpassword123')
        # Profile tab
        res1 = self.client.get(reverse('settings_index'))
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, 'chifundo@farmpulse.mw')

        # Units tab
        res2 = self.client.get(reverse('settings_index') + '?tab=units')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, 'Land Measurement Unit')

        # Data tab
        res3 = self.client.get(reverse('settings_index') + '?tab=data')
        self.assertEqual(res3.status_code, 200)
        self.assertContains(res3, 'Stored Agricultural Records')

    def test_settings_update_profile(self):
        self.client.login(username='chifundo', password='secretpassword123')
        response = self.client.post(reverse('settings_index'), {
            'action': 'profile',
            'first_name': 'Chifundo',
            'last_name': 'Phiri',
            'email': 'cphiri@farmpulse.mw',
            'phone_number': '+265991002003',
            'preferred_district': 'Kasungu',
            'land_unit': 'ha',
            'yield_unit': 'kg',
            'currency_format': 'standard',
            'share_anonymous_benchmarks': True,
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.last_name, 'Phiri')
        self.assertEqual(self.user.email, 'cphiri@farmpulse.mw')
        self.assertEqual(self.profile.preferred_district, 'Kasungu')

    # 3. Export Data
    def test_export_user_data(self):
        self.client.login(username='chifundo', password='secretpassword123')
        response = self.client.get(reverse('export_user_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(payload['farm']['name'], 'Chitukuko Farm')
        self.assertEqual(len(payload['seasons']), 1)
        self.assertEqual(len(payload['plans']), 1)

    # 4. Search Global
    def test_search_global_query(self):
        self.client.login(username='chifundo', password='secretpassword123')
        # Search Maize
        response = self.client.get(reverse('search_global') + '?q=Maize')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maize')
        self.assertGreaterEqual(response.context['total_count'], 1)

        # Search District
        res_dist = self.client.get(reverse('search_global') + '?q=Lilongwe')
        self.assertEqual(res_dist.status_code, 200)
        self.assertContains(res_dist, 'Lilongwe')

    # 5. Authentication Flows
    def test_login_success_and_failure(self):
        login_url = reverse('accounts:login')
        # Invalid credentials
        res_fail = self.client.post(login_url, {'username': 'chifundo', 'password': 'wrongpassword'})
        self.assertEqual(res_fail.status_code, 200)
        self.assertContains(res_fail, 'Invalid username/email or password')

        # Valid credentials
        res_ok = self.client.post(login_url, {'username': 'chifundo', 'password': 'secretpassword123'})
        self.assertEqual(res_ok.status_code, 302)
        self.assertEqual(res_ok.url, '/')

    def test_registration_flow_creates_user_and_farm(self):
        reg_url = reverse('accounts:register')
        res = self.client.post(reg_url, {
            'username': 'alinafe',
            'email': 'alinafe@demo.mw',
            'password': 'alinafeSecurePass2026',
            'password_confirm': 'alinafeSecurePass2026',
            'farm_name': 'Mwayi Farm',
            'district': 'Salima',
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='alinafe').exists())
        new_farm = Farm.objects.filter(name='Mwayi Farm').first()
        self.assertIsNotNone(new_farm)
        self.assertEqual(new_farm.owner.username, 'alinafe')
        self.assertIn('Salima', new_farm.location_description)

    def test_logout_view(self):
        self.client.login(username='chifundo', password='secretpassword123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_password_reset_page(self):
        reset_url = reverse('accounts:password_reset')
        res_get = self.client.get(reset_url)
        self.assertEqual(res_get.status_code, 200)
        res_post = self.client.post(reset_url, {'email': 'chifundo@farmpulse.mw'})
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(res_post.context['submitted'])
