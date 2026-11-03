import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from farms.models import Crop, Farm
from market.models import MarketSource, CropPrice, InputCost
from planner.engine import get_crop_benchmarks, calculate_plan_allocations, simulate_game_shocks
from planner.models import Plan, PlanItem, PlanAssumption


class PlannerEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='plannerdev', password='password123')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Mzuzu Trial Farm',
            total_land_ha=Decimal('3.00'),
            cultivated_land_ha=Decimal('2.50'),
            seasonal_budget_mwk=Decimal('600000.00'),
        )
        self.crop_maize = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop_gnuts = Crop.objects.create(name='Groundnuts', slug='groundnuts', category='legume')

    def test_get_crop_benchmarks_and_breakeven(self):
        bm = get_crop_benchmarks(self.crop_maize, self.farm)
        self.assertGreater(bm['yield_kg_ha'], Decimal('0'))
        self.assertGreater(bm['cost_ha_mwk'], Decimal('0'))
        self.assertGreater(bm['price_kg_mwk'], Decimal('0'))
        # Break-even price must equal Cost / Yield
        expected_be = round(bm['cost_ha_mwk'] / bm['yield_kg_ha'], 2)
        self.assertEqual(bm['break_even_price_mwk'], expected_be)

    def test_calculate_plan_allocations_generates_three_strategies(self):
        result = calculate_plan_allocations(
            farm=self.farm,
            total_land_ha=Decimal('2.00'),
            seasonal_budget_mwk=Decimal('500000.00'),
            selected_crops=[self.crop_maize, self.crop_gnuts],
        )
        plans = result['plans']
        self.assertEqual(len(plans), 3)

        strategies = [p['strategy_type'] for p in plans]
        self.assertIn('balanced', strategies)
        self.assertIn('return_focused', strategies)
        self.assertIn('risk_conscious', strategies)

        # Check math on balanced plan
        balanced = next(p for p in plans if p['strategy_type'] == 'balanced')
        self.assertEqual(
            balanced['total_margin_mwk'],
            balanced['total_revenue_mwk'] - balanced['total_cost_mwk']
        )
        self.assertEqual(len(balanced['items']), 2)

    def test_budget_warning_when_deficit_exists(self):
        # Very tiny budget of MWK 50,000 against 2 ha (costs ~800k)
        result = calculate_plan_allocations(
            farm=self.farm,
            total_land_ha=Decimal('2.00'),
            seasonal_budget_mwk=Decimal('50000.00'),
            selected_crops=[self.crop_maize, self.crop_gnuts],
        )
        for p in result['plans']:
            self.assertIsNotNone(p['budget_warning'])
            self.assertIn('exceeds available seasonal budget', p['budget_warning'])


class ScenarioGameEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gamedev', password='password123')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Game Farm',
            total_land_ha=Decimal('2.00'),
        )
        self.crop_maize = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop_gnuts = Crop.objects.create(name='Groundnuts', slug='groundnuts', category='legume')

        calc = calculate_plan_allocations(
            farm=self.farm,
            total_land_ha=Decimal('2.00'),
            selected_crops=[self.crop_maize, self.crop_gnuts],
        )
        self.baseline_plan = calc['plans'][0]

    def test_drought_shock_simulation(self):
        """Under a -30% drought shock, maize yield drops and margin falls."""
        sim = simulate_game_shocks(
            self.baseline_plan,
            rainfall_delta_pct=-30.0,
            temp_delta_c=1.5,
            price_delta_pct=10.0,
            input_cost_delta_pct=0.0,
        )
        self.assertIn(sim['grade'], ['A', 'B', 'C', 'F'])
        self.assertLessEqual(sim['resilience_score'], 100)
        self.assertGreaterEqual(sim['resilience_score'], 5)
        self.assertLess(sim['total_sim_margin'], float(self.baseline_plan['total_margin_mwk']))
        self.assertTrue(len(sim['sim_items']) == 2)

    def test_bumper_shock_simulation(self):
        """+20% rain with -30% price slump."""
        sim = simulate_game_shocks(
            self.baseline_plan,
            rainfall_delta_pct=20.0,
            temp_delta_c=0.0,
            price_delta_pct=-30.0,
            input_cost_delta_pct=0.0,
        )
        self.assertIsNotNone(sim['commentary'])
        self.assertIsNotNone(sim['health_status'])


class PlannerViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewfarmer', password='password123')
        self.farm = Farm.objects.create(
            owner=self.user,
            name='Chikondi North',
            total_land_ha=Decimal('2.50'),
            cultivated_land_ha=Decimal('2.00'),
            seasonal_budget_mwk=Decimal('450000.00'),
        )
        self.crop1 = Crop.objects.create(name='Maize', slug='maize', category='cereal')
        self.crop2 = Crop.objects.create(name='Groundnuts', slug='groundnuts', category='legume')
        self.farm.preferred_crops.set([self.crop1, self.crop2])

        self.client = Client()

    def test_planner_input_get(self):
        self.client.login(username='viewfarmer', password='password123')
        response = self.client.get(reverse('planner:planner_input'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crop Planner')
        self.assertContains(response, 'Chikondi North')

    def test_planner_input_generate(self):
        self.client.login(username='viewfarmer', password='password123')
        response = self.client.get(reverse('planner:planner_input') + '?generate=1&land=2.00&crops=maize&crops=groundnuts')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Balanced Strategy')
        self.assertContains(response, 'Return-Focused Strategy')
        self.assertContains(response, 'Risk-Conscious Strategy')
        self.assertContains(response, 'Break-Even Price')

    def test_save_plan_view(self):
        self.client.login(username='viewfarmer', password='password123')
        response = self.client.post(reverse('planner:save_plan'), {
            'strategy_type': 'balanced',
            'name': '2024/25 Test Plan',
            'total_land_ha': '2.00',
            'total_budget_mwk': '450000.00',
            'crop_slugs': ['maize', 'groundnuts'],
        })
        self.assertEqual(response.status_code, 302)
        plan = Plan.objects.filter(name='2024/25 Test Plan').first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.items.count(), 2)
        self.assertTrue(plan.assumptions.exists())

    def test_save_custom_plan_from_field_splitter(self):
        self.client.login(username='viewfarmer', password='password123')
        custom_payload = json.dumps([
            {'slug': 'maize', 'area_ha': 1.2},
            {'slug': 'groundnuts', 'area_ha': 0.8},
        ])
        response = self.client.post(reverse('planner:save_plan'), {
            'custom_allocations_json': custom_payload,
            'name': 'Custom Splitter Test Plan',
            'total_budget_mwk': '450000.00',
        })
        self.assertEqual(response.status_code, 302)
        plan = Plan.objects.filter(name='Custom Splitter Test Plan').first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.strategy_type, 'custom')
        self.assertEqual(plan.total_land_ha, Decimal('2.00'))
        self.assertEqual(plan.items.count(), 2)
        self.assertTrue(plan.total_expected_cost_mwk > 0)
        self.assertTrue(plan.total_expected_revenue_mwk > 0)
        self.assertTrue(plan.assumptions.exists())

    def test_scenario_simulator_view(self):
        self.client.login(username='viewfarmer', password='password123')
        response = self.client.get(reverse('planner:scenario_simulator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seasonal Risk Analysis')
        self.assertContains(response, 'Resilience')
        self.assertContains(response, 'Net Farm Cashflow')
        self.assertContains(response, 'Food Security')
        self.assertContains(response, 'El Niño Drought')

    def test_simulate_scenario_api(self):
        self.client.login(username='viewfarmer', password='password123')
        response = self.client.get(reverse('planner:simulate_scenario_api') + '?rain=-20&temp=1.5&price=10&cost=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('resilience_score', data)
        self.assertIn('grade', data)
        self.assertIn('total_sim_margin', data)
        self.assertIn('sim_items', data)

    def test_plan_list_and_detail(self):
        self.client.login(username='viewfarmer', password='password123')
        plan = Plan.objects.create(
            farm=self.farm,
            name='Saved Harvest Plan',
            total_land_ha=Decimal('2.00'),
            total_expected_cost_mwk=Decimal('300000.00'),
            total_expected_revenue_mwk=Decimal('800000.00'),
            total_expected_margin_mwk=Decimal('500000.00'),
        )
        list_resp = self.client.get(reverse('planner:plan_list'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, 'Saved Harvest Plan')

        detail_resp = self.client.get(reverse('planner:plan_detail', kwargs={'pk': plan.pk}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'Saved Harvest Plan')
        self.assertContains(detail_resp, 'Run Risk Analysis')
