"""
Management command: seed_demo_plans
Seeds realistic demonstration plans and a completed season review for the demo farmer.
Ensures that /plans/, /plans/compare/, and /season-review/ present rich, institutional data
during national stakeholder presentations.

Run: python manage.py seed_demo_plans
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from farms.models import Farm, Crop, Season, SeasonReview, Planting
from planner.models import Plan, PlanItem, PlanAssumption


class Command(BaseCommand):
    help = "Seed demonstration crop plans and season review for presentation."

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No user found in database. Create a user first."))
            return

        farm = Farm.objects.filter(owner=user).first()
        if not farm:
            farm = Farm.objects.create(
                owner=user,
                name="Chikondi Model Farm",
                location_description="Lilongwe District, Central Region (Chitedze EPA)",
                latitude=Decimal("-13.9833"),
                longitude=Decimal("33.6500"),
                total_land_ha=Decimal("2.50"),
                cultivated_land_ha=Decimal("2.50"),
                soil_type="Sandy Loam",
                seasonal_budget_mwk=Decimal("450000.00"),
                available_labour_persons=3,
            )
            self.stdout.write(self.style.SUCCESS(f"Created demo farm: {farm.name}"))

        # Fetch required crops
        try:
            maize = Crop.objects.get(slug='maize')
            soybeans = Crop.objects.get(slug='soybeans')
            groundnuts = Crop.objects.get(slug='groundnuts')
            beans = Crop.objects.get(slug='common-beans')
        except Crop.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Required crop missing: {e}"))
            return

        # ─── Plan 1: Commercial Grain & Oilseed Portfolio ─────────────────────
        plan1, created1 = Plan.objects.get_or_create(
            farm=farm,
            name="2025/26 Commercial Grain & Oilseed Portfolio",
            defaults={
                'strategy_type': 'balanced',
                'status': 'active',
                'total_land_ha': Decimal("2.50"),
                'total_budget_mwk': Decimal("450000.00"),
                'total_expected_cost_mwk': Decimal("382500.00"),
                'total_expected_revenue_mwk': Decimal("1875000.00"),
                'total_expected_margin_mwk': Decimal("1492500.00"),
                'notes': (
                    "Optimized for Central Plateau agro-ecological zone. "
                    "Allocates 1.5 ha to SC403 hybrid maize and 1.0 ha to Tikolore soybeans "
                    "with guaranteed ADMARC and processor off-taker contracts."
                )
            }
        )

        if created1 or not plan1.items.exists():
            plan1.items.all().delete()
            # Item 1: Maize (1.5 ha)
            PlanItem.objects.create(
                plan=plan1,
                crop=maize,
                area_ha=Decimal("1.50"),
                expected_yield_kg_per_ha=Decimal("3200.00"),
                expected_yield_kg_total=Decimal("4800.00"),
                expected_cost_per_ha_mwk=Decimal("152000.00"),
                expected_total_cost_mwk=Decimal("228000.00"),
                expected_selling_price_mwk_per_kg=Decimal("280.00"),
                expected_revenue_mwk=Decimal("1344000.00"),
                expected_gross_margin_mwk=Decimal("1116000.00"),
                break_even_price_mwk_per_kg=Decimal("47.50"),
                notes="Certified hybrid seed with 23:21:0 basal and CAN split top-dressing."
            )
            # Item 2: Soybeans (1.0 ha)
            PlanItem.objects.create(
                plan=plan1,
                crop=soybeans,
                area_ha=Decimal("1.00"),
                expected_yield_kg_per_ha=Decimal("1600.00"),
                expected_yield_kg_total=Decimal("1600.00"),
                expected_cost_per_ha_mwk=Decimal("154500.00"),
                expected_total_cost_mwk=Decimal("154500.00"),
                expected_selling_price_mwk_per_kg=Decimal("331.88"),
                expected_revenue_mwk=Decimal("531000.00"),
                expected_gross_margin_mwk=Decimal("376500.00"),
                break_even_price_mwk_per_kg=Decimal("96.56"),
                notes="Inoculated with Rhizobium bio-fertilizer to reduce basal nitrogen requirement."
            )

            # Assumptions
            PlanAssumption.objects.get_or_create(
                plan=plan1,
                parameter_name="Commercial Maize Price (AMIS Chinkhoma)",
                defaults={'value_used': Decimal("280.00"), 'source_note': "AMIS Price Bulletin October 2025"}
            )
            PlanAssumption.objects.get_or_create(
                plan=plan1,
                parameter_name="Soybean Processing Benchmark (SOYCO/ADMARC)",
                defaults={'value_used': Decimal("331.88"), 'source_note': "ADMARC Contract Pricing 2025"}
            )

        # ─── Plan 2: Climate-Resilient Legume Diversification ──────────────────
        plan2, created2 = Plan.objects.get_or_create(
            farm=farm,
            name="2025/26 Climate-Resilient Legume Diversification",
            defaults={
                'strategy_type': 'risk_conscious',
                'status': 'draft',
                'total_land_ha': Decimal("2.50"),
                'total_budget_mwk': Decimal("450000.00"),
                'total_expected_cost_mwk': Decimal("318000.00"),
                'total_expected_revenue_mwk': Decimal("1542000.00"),
                'total_expected_margin_mwk': Decimal("1224000.00"),
                'notes': (
                    "Low-input, high-resilience strategy designed for potential El Niño dry spells. "
                    "Diverts land into biological nitrogen-fixing legumes (CG7 groundnuts & beans), "
                    "cutting chemical fertilizer expenditure by 38% while guaranteeing 2,800 kg staple food reserve."
                )
            }
        )
        if plan2.strategy_type != 'risk_conscious':
            plan2.strategy_type = 'risk_conscious'
            plan2.save()

        if created2 or not plan2.items.exists():
            plan2.items.all().delete()
            # Maize (1.0 ha)
            PlanItem.objects.create(
                plan=plan2,
                crop=maize,
                area_ha=Decimal("1.00"),
                expected_yield_kg_per_ha=Decimal("2800.00"),
                expected_yield_kg_total=Decimal("2800.00"),
                expected_cost_per_ha_mwk=Decimal("135000.00"),
                expected_total_cost_mwk=Decimal("135000.00"),
                expected_selling_price_mwk_per_kg=Decimal("280.00"),
                expected_revenue_mwk=Decimal("784000.00"),
                expected_gross_margin_mwk=Decimal("649000.00"),
                break_even_price_mwk_per_kg=Decimal("48.21"),
                notes="Household subsistence buffer plus modest local market surplus."
            )
            # Groundnuts (0.80 ha)
            PlanItem.objects.create(
                plan=plan2,
                crop=groundnuts,
                area_ha=Decimal("0.80"),
                expected_yield_kg_per_ha=Decimal("1200.00"),
                expected_yield_kg_total=Decimal("960.00"),
                expected_cost_per_ha_mwk=Decimal("122000.00"),
                expected_total_cost_mwk=Decimal("97600.00"),
                expected_selling_price_mwk_per_kg=Decimal("450.00"),
                expected_revenue_mwk=Decimal("432000.00"),
                expected_gross_margin_mwk=Decimal("334400.00"),
                break_even_price_mwk_per_kg=Decimal("101.67"),
                notes="CG7 certified drought-tolerant confectionery grade groundnut."
            )
            # Common Beans (0.70 ha)
            PlanItem.objects.create(
                plan=plan2,
                crop=beans,
                area_ha=Decimal("0.70"),
                expected_yield_kg_per_ha=Decimal("1100.00"),
                expected_yield_kg_total=Decimal("770.00"),
                expected_cost_per_ha_mwk=Decimal("122000.00"),
                expected_total_cost_mwk=Decimal("85400.00"),
                expected_selling_price_mwk_per_kg=Decimal("423.38"),
                expected_revenue_mwk=Decimal("326000.00"),
                expected_gross_margin_mwk=Decimal("240600.00"),
                break_even_price_mwk_per_kg=Decimal("110.91"),
                notes="Early-maturing bush beans for rapid mid-season harvest and cash flow."
            )

        # ─── Plan 3: Commercial Return-Focused Strategy ──────────────────────
        plan3, created3 = Plan.objects.get_or_create(
            farm=farm,
            name="2025/26 Commercial High-Return Strategy",
            defaults={
                'strategy_type': 'return_focused',
                'status': 'active',
                'total_land_ha': Decimal("2.50"),
                'total_budget_mwk': Decimal("450000.00"),
                'total_expected_cost_mwk': Decimal("353750.00"),
                'total_expected_revenue_mwk': Decimal("2038750.00"),
                'total_expected_margin_mwk': Decimal("1685000.00"),
                'notes': (
                    "High-return commercial allocation maximizing processor demand for Tikolore soybeans "
                    "and export-quality CG7 groundnuts, while retaining a 0.5 ha hybrid maize buffer for food safety."
                )
            }
        )

        if created3 or not plan3.items.exists():
            plan3.items.all().delete()
            # Soybeans (1.20 ha)
            PlanItem.objects.create(
                plan=plan3,
                crop=soybeans,
                area_ha=Decimal("1.20"),
                expected_yield_kg_per_ha=Decimal("1800.00"),
                expected_yield_kg_total=Decimal("2160.00"),
                expected_cost_per_ha_mwk=Decimal("148000.00"),
                expected_total_cost_mwk=Decimal("177600.00"),
                expected_selling_price_mwk_per_kg=Decimal("345.00"),
                expected_revenue_mwk=Decimal("745200.00"),
                expected_gross_margin_mwk=Decimal("567600.00"),
                break_even_price_mwk_per_kg=Decimal("82.22"),
                notes="Pre-season supply contract with poultry feed mill in Lilongwe."
            )
            # Groundnuts (0.80 ha)
            PlanItem.objects.create(
                plan=plan3,
                crop=groundnuts,
                area_ha=Decimal("0.80"),
                expected_yield_kg_per_ha=Decimal("1350.00"),
                expected_yield_kg_total=Decimal("1080.00"),
                expected_cost_per_ha_mwk=Decimal("126000.00"),
                expected_total_cost_mwk=Decimal("100800.00"),
                expected_selling_price_mwk_per_kg=Decimal("460.00"),
                expected_revenue_mwk=Decimal("496800.00"),
                expected_gross_margin_mwk=Decimal("396000.00"),
                break_even_price_mwk_per_kg=Decimal("93.33"),
                notes="High-oil confectionery grade for regional wholesale off-taker."
            )
            # Maize (0.50 ha)
            PlanItem.objects.create(
                plan=plan3,
                crop=maize,
                area_ha=Decimal("0.50"),
                expected_yield_kg_per_ha=Decimal("3500.00"),
                expected_yield_kg_total=Decimal("1750.00"),
                expected_cost_per_ha_mwk=Decimal("150700.00"),
                expected_total_cost_mwk=Decimal("75350.00"),
                expected_selling_price_mwk_per_kg=Decimal("280.00"),
                expected_revenue_mwk=Decimal("490000.00"),
                expected_gross_margin_mwk=Decimal("414650.00"),
                break_even_price_mwk_per_kg=Decimal("43.06"),
                notes="High-density hybrid maize for domestic food security."
            )

            PlanAssumption.objects.get_or_create(
                plan=plan3,
                parameter_name="Commercial Feed Mill Off-take (Lilongwe)",
                defaults={'value_used': Decimal("345.00"), 'source_note': "Off-taker Pre-Planting Agreement"}
            )
            PlanAssumption.objects.get_or_create(
                plan=plan3,
                parameter_name="Confectionery Groundnut Export Price (Mitundu Hub)",
                defaults={'value_used': Decimal("460.00"), 'source_note': "AMIS Price Bulletin 2025"}
            )

        # ─── Link or Create Season Review ─────────────────────────────────────
        season = Season.objects.filter(farm=farm).order_by('-start_date').first()
        if season:
            review, rev_created = SeasonReview.objects.get_or_create(
                season=season,
                defaults={
                    'associated_plan': plan1,
                    'overall_satisfaction': 4,
                    'lessons_learned': (
                        "1. Early planting following the 28mm rain trigger on Nov 14 resulted in 94% germination.\n"
                        "2. Split CAN application at 3 weeks and 6 weeks protected the maize crop during the January dry spell.\n"
                        "3. Intercropping legumes improved soil friability and provided essential cash flow in April before main maize harvest."
                    ),
                    'weather_assessment': (
                        "Seasonal rainfall totaled 840mm (near normal). "
                        "A 12-day dry spell occurred in early January, but mulching and minimal tillage prevented crop moisture stress."
                    ),
                    'market_assessment': (
                        "Maize grain sold at MWK 280/kg to local buying club. "
                        "Soybean sold at MWK 330/kg directly to processor aggregator, achieving an overall 312% return on working capital."
                    )
                }
            )
            if rev_created:
                self.stdout.write(self.style.SUCCESS(f"Created season review for '{season.name}'."))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded 2 demonstration plans:\n"
            f"  - '{plan1.name}' (Active)\n"
            f"  - '{plan2.name}' (Resilient Variant)\n"
            f"Ready for live comparison at /plans/compare/ and review at /season-review/."
        ))

