from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from climate.models import District, WeatherStation, DailyWeatherObservation
from climate.services import fetch_live_forecast_for_station


class Command(BaseCommand):
    help = "Seed Malawian automated weather stations and ingest initial 14-day live forecasts."

    def handle(self, *args, **options):
        stations_data = [
            {
                'station_id': 'DCCMS-LL-CHITEDZE-01',
                'name': 'Chitedze Agricultural Research Station',
                'district_slug': 'lilongwe',
                'station_type': 'research_station',
                'latitude': Decimal('-13.974400'),
                'longitude': Decimal('33.649900'),
                'elevation_m': 1146,
                'hardware_notes': 'Campbell Scientific CR1000X AWS with tipping bucket rain gauge & pyranometer.',
            },
            {
                'station_id': 'DCCMS-LL-KIA-02',
                'name': 'Kamuzu International Airport AWS',
                'district_slug': 'lilongwe',
                'station_type': 'dccms_aws',
                'latitude': Decimal('-13.782900'),
                'longitude': Decimal('33.780800'),
                'elevation_m': 1230,
                'hardware_notes': 'Vaisala Milos 520 aviation meteorological terminal.',
            },
            {
                'station_id': 'DCCMS-KU-BOMA-01',
                'name': 'Kasungu Boma Agromet Station',
                'district_slug': 'kasungu',
                'station_type': 'dccms_aws',
                'latitude': Decimal('-13.033300'),
                'longitude': Decimal('33.483300'),
                'elevation_m': 1045,
                'hardware_notes': 'DCCMS telemetric solar station with GPRS cellular transmitter.',
            },
            {
                'station_id': 'DCCMS-SA-LAKE-01',
                'name': 'Salima Lakeshore Meteorological Station',
                'district_slug': 'salima',
                'station_type': 'dccms_aws',
                'latitude': Decimal('-13.780400'),
                'longitude': Decimal('34.458700'),
                'elevation_m': 512,
                'hardware_notes': 'Lake Malawi basin microclimate sensor suite.',
            },
            {
                'station_id': 'DCCMS-BT-BVUMBWE-01',
                'name': 'Bvumbwe Agro-Research Station',
                'district_slug': 'blantyre',
                'station_type': 'research_station',
                'latitude': Decimal('-15.916700'),
                'longitude': Decimal('35.133300'),
                'elevation_m': 1160,
                'hardware_notes': 'Southern Shire highlands agro-meteorological test bed.',
            },
        ]

        today = date.today()

        for s_data in stations_data:
            district = District.objects.filter(slug=s_data['district_slug']).first()
            if not district:
                district = District.objects.create(
                    name=s_data['district_slug'].capitalize(),
                    slug=s_data['district_slug'],
                    region='central' if s_data['district_slug'] != 'blantyre' else 'southern',
                    elevation_m=s_data['elevation_m'],
                )

            station, created = WeatherStation.objects.get_or_create(
                station_id=s_data['station_id'],
                defaults={
                    'name': s_data['name'],
                    'district': district,
                    'station_type': s_data['station_type'],
                    'latitude': s_data['latitude'],
                    'longitude': s_data['longitude'],
                    'elevation_m': s_data['elevation_m'],
                    'hardware_notes': s_data['hardware_notes'],
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} Station: {station.name}")

            # Seed 7 days of historical ground truth observations
            for day_offset in range(1, 8):
                obs_date = today - timedelta(days=day_offset)
                DailyWeatherObservation.objects.get_or_create(
                    station=station,
                    date=obs_date,
                    defaults={
                        'rainfall_mm': Decimal('12.5') if day_offset in [2, 3] else Decimal('0.0'),
                        'temp_max_c': Decimal('28.5'),
                        'temp_min_c': Decimal('16.8'),
                        'temp_mean_c': Decimal('22.6'),
                        'relative_humidity_pct': 68,
                        'wind_speed_kmh': Decimal('11.5'),
                        'solar_radiation_mj': Decimal('21.4'),
                    }
                )

            # Ingest live forecast
            count, src = fetch_live_forecast_for_station(station)
            self.stdout.write(self.style.SUCCESS(f"  -> Ingested {count} forecast days via {src}"))
