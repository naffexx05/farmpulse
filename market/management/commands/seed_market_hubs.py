from decimal import Decimal
from django.core.management.base import BaseCommand
from climate.models import District
from market.models import MarketHub
from market.services import fetch_live_market_feed_for_hub


class Command(BaseCommand):
    help = "Seed Malawian agricultural market hubs and ingest initial real-time quotes & 30-day price projections."

    def handle(self, *args, **options):
        hubs_data = [
            {
                'hub_id': 'AMIS-LL-MITUNDU-01',
                'name': 'Mitundu Grain Aggregation Depot',
                'district_slug': 'lilongwe',
                'hub_type': 'rural_aggregation',
                'latitude': Decimal('-14.166700'),
                'longitude': Decimal('33.783300'),
                'primary_commodities': 'Maize, Groundnuts, Soybeans, Common Beans',
                'operating_schedule': 'Tuesdays & Saturdays (Primary Market Days)',
                'notes': 'Prime central region maize and legume aggregation terminal for over 15,000 smallholders.',
            },
            {
                'hub_id': 'AMIS-LL-MCHESI-02',
                'name': 'Mchesi Central Wholesale Terminal',
                'district_slug': 'lilongwe',
                'hub_type': 'urban_wholesale',
                'latitude': Decimal('-13.983300'),
                'longitude': Decimal('33.783300'),
                'primary_commodities': 'Maize Grain, Soybeans, Refined Flour, Rice',
                'operating_schedule': 'Daily Trading (06:00 - 18:00)',
                'notes': 'Primary urban wholesale depot supplying grain millers, commercial food vendors, and Lilongwe retailers.',
            },
            {
                'hub_id': 'AMIS-BT-LUNZU-01',
                'name': 'Lunzu Regional Aggregation Hub',
                'district_slug': 'blantyre',
                'hub_type': 'rural_aggregation',
                'latitude': Decimal('-15.683300'),
                'longitude': Decimal('35.016700'),
                'primary_commodities': 'Pigeon Peas, Maize, Cassava, Sweet Potatoes',
                'operating_schedule': 'Wednesdays & Sundays',
                'notes': 'Southern highway aggregation gateway linking produce from Shire Highlands and lower Shire.',
            },
            {
                'hub_id': 'AMIS-BT-LIMBE-02',
                'name': 'Limbe Commercial Wholesale Market',
                'district_slug': 'blantyre',
                'hub_type': 'urban_wholesale',
                'latitude': Decimal('-15.816700'),
                'longitude': Decimal('35.050000'),
                'primary_commodities': 'White Maize, Soya Oilseed, Groundnuts, Beans',
                'operating_schedule': 'Daily Wholesale & Commercial Distribution',
                'notes': 'Premier southern regional terminal market with large-scale agro-processors and grain trading companies.',
            },
            {
                'hub_id': 'AMIS-KU-CHINKHOMA-01',
                'name': 'Chinkhoma Commercial Trading Center',
                'district_slug': 'kasungu',
                'hub_type': 'commodity_exchange',
                'latitude': Decimal('-13.116700'),
                'longitude': Decimal('33.433300'),
                'primary_commodities': 'Maize, Soybeans, Sunflower, Tobacco',
                'operating_schedule': 'Mondays to Fridays',
                'notes': 'Central grain belt aggregation center with warehousing adjacent to the auction floors.',
            },
            {
                'hub_id': 'AMIS-SA-LAKESHORE-01',
                'name': 'Salima Central Lakeshore Market',
                'district_slug': 'salima',
                'hub_type': 'rural_aggregation',
                'latitude': Decimal('-13.780400'),
                'longitude': Decimal('34.458700'),
                'primary_commodities': 'Kilombero Rice, Cassava Makaka, Maize, Fish',
                'operating_schedule': 'Daily Lakeshore Trade',
                'notes': 'Primary market hub for lakeshore irrigated rice schemes and cassava chips.',
            },
        ]

        for h_data in hubs_data:
            district = District.objects.filter(slug=h_data['district_slug']).first()
            if not district:
                district = District.objects.create(
                    name=h_data['district_slug'].capitalize(),
                    slug=h_data['district_slug'],
                    region='central' if h_data['district_slug'] in ['lilongwe', 'kasungu', 'salima'] else 'southern',
                )

            hub, created = MarketHub.objects.get_or_create(
                hub_id=h_data['hub_id'],
                defaults={
                    'name': h_data['name'],
                    'district': district,
                    'hub_type': h_data['hub_type'],
                    'latitude': h_data['latitude'],
                    'longitude': h_data['longitude'],
                    'primary_commodities': h_data['primary_commodities'],
                    'operating_schedule': h_data['operating_schedule'],
                    'notes': h_data['notes'],
                }
            )

            res = fetch_live_market_feed_for_hub(hub)
            action = "Created" if created else "Updated"
            self.stdout.write(
                f"{action} Hub: {hub.name} ({res['quotes_updated']} quotes, {res['forecasts_updated']} forecasts)"
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded all Malawian market hubs and live feeds."))
