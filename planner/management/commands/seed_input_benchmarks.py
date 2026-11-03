"""
Management command: seed_input_benchmarks
Populates InputCostBenchmark with 2025 ADMARC / AGORA reference prices
for the six key Malawian smallholder crops.

Source: ADMARC Input Price Bulletin October 2025; Chitedze Research Station
extension advisory; MoAIWD Seasonal Input Cost Guidelines 2024/25.

Run: python manage.py seed_input_benchmarks
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from farms.models import Crop
from planner.models import InputCostBenchmark

SEASON = 2025

# fmt: off
# Data: (crop_slug, input_category, description, price_per_ha_mwk)
BENCHMARKS = [

    # ─── MAIZE ───────────────────────────────────────────────────────────────
    ('maize', 'seed',       'SC403 hybrid seed (25 kg/ha)',                        Decimal('14500')),
    ('maize', 'basal_fert', '23:21:0+4S basal fertiliser (100 kg/ha)',             Decimal('42000')),
    ('maize', 'top_dress',  'CAN top dressing (100 kg/ha, split application)',     Decimal('38000')),
    ('maize', 'labour',     'Tillage, planting, weeding × 2, shelling (ganyu)',    Decimal('28000')),
    ('maize', 'herbicide',  'Atrazine pre-emergent herbicide (2 L/ha)',            Decimal('4200')),
    ('maize', 'transport',  'Transport to ADMARC depot or nearest AMIS hub',       Decimal('3500')),

    # ─── GROUNDNUTS ──────────────────────────────────────────────────────────
    ('groundnuts', 'seed',       'CG7 / Chalimbana groundnut seed (80 kg/ha)',     Decimal('28000')),
    ('groundnuts', 'basal_fert', 'Single Super Phosphate (SSP) 100 kg/ha',         Decimal('22000')),
    ('groundnuts', 'top_dress',  'Not typically required (N-fixing legume)',        Decimal('0')),
    ('groundnuts', 'labour',     'Planting, weeding × 2, lifting, shelling',       Decimal('24000')),
    ('groundnuts', 'herbicide',  'Post-emergence broadleaf control (1.5 L/ha)',    Decimal('3800')),
    ('groundnuts', 'transport',  'Transport to NASFAM / oil-pressing depot',       Decimal('4200')),

    # ─── SOYBEANS ─────────────────────────────────────────────────────────────
    ('soybeans', 'seed',       'Tikolore / Nasoko soybean seed (80 kg/ha)',        Decimal('19200')),
    ('soybeans', 'basal_fert', 'SSP basal (100 kg/ha) + Rhizobium inoculant',     Decimal('18500')),
    ('soybeans', 'top_dress',  'Minimal — legume (spot-apply if deficiency noted)',Decimal('0')),
    ('soybeans', 'labour',     'Planting, weeding × 2, harvesting, threshing',    Decimal('22000')),
    ('soybeans', 'herbicide',  'Metolachlor pre-emergence (2 L/ha)',               Decimal('5100')),
    ('soybeans', 'transport',  'Transport to SOYCO / processor warehouse',        Decimal('4800')),

    # ─── BEANS (COMMON / KIDNEY) ──────────────────────────────────────────────
    ('common-beans', 'seed',       'Lyabi / Kamsosa bean seed (60 kg/ha)',               Decimal('21000')),
    ('common-beans', 'basal_fert', 'SSP 75 kg/ha',                                       Decimal('16500')),
    ('common-beans', 'top_dress',  'Not typically required',                              Decimal('0')),
    ('common-beans', 'labour',     'Planting, weeding x 2, harvesting, threshing',       Decimal('20000')),
    ('common-beans', 'herbicide',  'Pre-emergence broadleaf 1 L/ha',                     Decimal('2800')),
    ('common-beans', 'transport',  'Transport to Mzuzu / Lilongwe wholesale hub',        Decimal('5000')),

    # ─── CASSAVA ─────────────────────────────────────────────────────────────
    ('cassava', 'seed',       'Manyokola cuttings / Sauti variety (8,000/ha)',    Decimal('12000')),
    ('cassava', 'basal_fert', 'NPK compound (60:30:30) 100 kg/ha',               Decimal('28000')),
    ('cassava', 'top_dress',  'Urea top-dress at 3 months (50 kg/ha)',            Decimal('19000')),
    ('cassava', 'labour',     'Land prep, planting, weeding × 2, harvesting',    Decimal('26000')),
    ('cassava', 'herbicide',  'Pre-emergence control (2 L/ha)',                   Decimal('3600')),
    ('cassava', 'transport',  'Transport to SFFRFM / urban market',              Decimal('6000')),

    # ─── TOBACCO (BURLEY) ────────────────────────────────────────────────────
    ('tobacco', 'seed',       'Certified burley variety (nursery + transplant)',  Decimal('18000')),
    ('tobacco', 'basal_fert', 'CAN 150 kg/ha + compound fertiliser',             Decimal('68000')),
    ('tobacco', 'top_dress',  'CAN split top dressing (150 kg/ha)',               Decimal('57000')),
    ('tobacco', 'labour',     'Nursery, transplanting, topping, grading, baling', Decimal('72000')),
    ('tobacco', 'herbicide',  'Pre-emergent herbicide application',               Decimal('5500')),
    ('tobacco', 'transport',  'Transport to Limbe auction floor / buying club',  Decimal('9500')),
]
# fmt: on


class Command(BaseCommand):
    help = "Seed InputCostBenchmark table with 2025 reference input prices (ADMARC/AGORA)"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        skipped = 0

        for slug, category, description, price in BENCHMARKS:
            try:
                crop = Crop.objects.get(slug=slug)
            except Crop.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Crop not found: {slug} — skipping"))
                skipped += 1
                continue

            obj, was_created = InputCostBenchmark.objects.update_or_create(
                crop=crop,
                input_category=category,
                season_year=SEASON,
                defaults={
                    'description': description,
                    'benchmark_price_mwk_per_ha': price,
                    'source_note': 'ADMARC Input Price Bulletin Oct 2025 / MoAIWD Guidelines',
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nInput Cost Benchmarks seeded: {created} created, {updated} updated, {skipped} skipped."
        ))
