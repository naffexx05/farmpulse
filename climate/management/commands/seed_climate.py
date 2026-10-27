import math
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from climate.models import District, ClimateSource, ClimateRecord


DISTRICTS = [
    {
        'name': 'Lilongwe',
        'slug': 'lilongwe',
        'region': 'central',
        'latitude': Decimal('-13.962612'),
        'longitude': Decimal('33.774119'),
        'elevation_m': 1050,
        'description': 'Central agricultural plateau. Fertile sandy-clay loams; unimodal rainfall Nov–Apr; primary maize, groundnut, and soybean belt.',
        'base_rain': [225.0, 210.0, 140.0, 40.0, 8.0, 2.0, 1.0, 1.0, 3.0, 15.0, 65.0, 180.0],  # Jan to Dec
        'base_max_t': [26.5, 26.5, 26.2, 26.0, 25.2, 23.5, 23.2, 25.5, 28.5, 30.5, 29.8, 27.2],
        'base_min_t': [17.5, 17.2, 16.5, 14.5, 11.2, 8.5, 8.0, 9.8, 13.0, 16.5, 18.0, 17.8],
        'heat_sensitivity': 1.0,
    },
    {
        'name': 'Kasungu',
        'slug': 'kasungu',
        'region': 'central',
        'latitude': Decimal('-13.033333'),
        'longitude': Decimal('33.483333'),
        'elevation_m': 1030,
        'description': 'Northern-central plateau. Coarser light-textured soils with lower water retention and higher susceptibility to mid-season dry spells.',
        'base_rain': [200.0, 180.0, 120.0, 35.0, 5.0, 1.0, 1.0, 1.0, 2.0, 12.0, 50.0, 160.0],
        'base_max_t': [27.0, 27.0, 26.8, 26.5, 25.8, 24.0, 23.8, 26.2, 29.2, 31.2, 30.5, 27.8],
        'base_min_t': [17.0, 16.8, 16.0, 14.0, 10.5, 8.0, 7.5, 9.0, 12.5, 16.0, 17.5, 17.2],
        'heat_sensitivity': 1.2,
    },
    {
        'name': 'Salima',
        'slug': 'salima',
        'region': 'central',
        'latitude': Decimal('-13.780400'),
        'longitude': Decimal('34.458700'),
        'elevation_m': 490,
        'description': 'Lakeshore lowlands bordering Lake Malawi. Hotter climate with high thermal extremes, erratic convective storms, and flood hazards.',
        'base_rain': [260.0, 240.0, 170.0, 55.0, 12.0, 3.0, 2.0, 2.0, 3.0, 18.0, 70.0, 200.0],
        'base_max_t': [30.5, 30.2, 30.0, 29.8, 28.5, 26.8, 26.5, 28.8, 32.5, 34.8, 34.2, 31.5],
        'base_min_t': [21.5, 21.5, 20.8, 19.0, 16.0, 13.5, 13.0, 14.8, 18.2, 22.0, 23.5, 22.2],
        'heat_sensitivity': 2.4,
    },
    {
        'name': 'Blantyre',
        'slug': 'blantyre',
        'region': 'southern',
        'latitude': Decimal('-15.786111'),
        'longitude': Decimal('35.005833'),
        'elevation_m': 1040,
        'description': 'Southern Shire Highlands. Cooler temperate climate with Chiperoni winter drizzle and vulnerability to intense southern tropical cyclones.',
        'base_rain': [240.0, 220.0, 180.0, 60.0, 18.0, 8.0, 6.0, 5.0, 6.0, 28.0, 85.0, 210.0],
        'base_max_t': [26.0, 25.8, 25.5, 24.8, 23.5, 21.8, 21.5, 23.8, 27.0, 29.2, 28.5, 26.5],
        'base_min_t': [17.8, 17.5, 17.0, 15.2, 12.8, 10.5, 10.0, 11.2, 13.8, 16.8, 18.2, 18.0],
        'heat_sensitivity': 0.6,
    },
]

HISTORICAL_YEARS = list(range(2005, 2025))  # 20 years: 2005 to 2024

# Drought years (El Niño anomaly multipliers for southern/central Africa)
DROUGHT_ANOMALIES = {
    2015: 0.72,
    2016: 0.76,
    2018: 0.85,
    2023: 0.80,
    2024: 0.75,  # 2023/24 strong El Niño
}

# Wet / Cyclone years
WET_ANOMALIES = {
    2008: 1.25,
    2012: 1.18,
    2019: 1.30,  # Cyclone Idai peripheral rains
    2022: 1.22,  # Storm Ana
    2023: 1.15,  # Cyclone Freddy in March (South)
}


class Command(BaseCommand):
    help = 'Seed 20 years of synthetic climate intelligence for Malawian districts.'

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Sources
        hist_source, _ = ClimateSource.objects.get_or_create(
            name='Synthetic Climatology Baseline (Malawi DCCMS Calibration 2005–2024)',
            defaults={
                'source_type': 'historical_observed',
                'attribution': 'Synthetic calibration generated based on Department of Climate Change and Meteorological Services (DCCMS) agro-ecological benchmarks (2005–2024). For demonstration and simulation purposes only.',
                'citation_url': 'https://www.metmalawi.gov.mw',
                'is_synthetic': True,
            }
        )

        outlook_source, _ = ClimateSource.objects.get_or_create(
            name='Official Seasonal Outlook 2024/25 (Synthetic Reference)',
            defaults={
                'source_type': 'seasonal_outlook',
                'attribution': 'Synthetic simulation of national seasonal weather advisory outlook for 2024/25 agricultural season.',
                'citation_url': 'https://www.metmalawi.gov.mw',
                'is_synthetic': True,
            }
        )

        scenario_source, _ = ClimateSource.objects.get_or_create(
            name='Illustrative Climate Scenario (+1.5°C Warming & -15% Precipitation)',
            defaults={
                'source_type': 'illustrative_scenario',
                'attribution': 'Simulated stress scenario representing regional warming and increased mid-season precipitation gaps.',
                'is_synthetic': True,
            }
        )

        # 2. Districts & Records
        total_records_created = 0

        # Pseudo-random generator with fixed seed for reproducibility
        rng = random.Random(42)

        for d_info in DISTRICTS:
            district, _ = District.objects.get_or_create(
                slug=d_info['slug'],
                defaults={
                    'name': d_info['name'],
                    'region': d_info['region'],
                    'latitude': d_info['latitude'],
                    'longitude': d_info['longitude'],
                    'elevation_m': d_info['elevation_m'],
                    'description': d_info['description'],
                }
            )

            # Generate 20 years of historical monthly records (2005-2024)
            for year in HISTORICAL_YEARS:
                # Global climate trend: gradual warming (+0.02°C/year since 2005)
                warming_delta = (year - 2005) * 0.022

                # Year-specific rainfall anomaly factor
                rain_factor = DROUGHT_ANOMALIES.get(year, WET_ANOMALIES.get(year, 1.0))
                # Add slight random variation (+- 7%)
                year_noise = rng.uniform(0.93, 1.07)
                effective_rain_factor = rain_factor * year_noise

                for m in range(1, 13):
                    m_idx = m - 1
                    base_r = d_info['base_rain'][m_idx]
                    base_max_t = d_info['base_max_t'][m_idx]
                    base_min_t = d_info['base_min_t'][m_idx]

                    # Monthly rainfall
                    month_noise = rng.uniform(0.85, 1.15) if base_r > 20 else rng.uniform(0.5, 1.5)
                    rainfall = round(max(0.0, base_r * effective_rain_factor * month_noise), 1)

                    # Rainfall days
                    if rainfall > 150:
                        rain_days = rng.randint(14, 22)
                    elif rainfall > 50:
                        rain_days = rng.randint(6, 14)
                    elif rainfall > 10:
                        rain_days = rng.randint(2, 6)
                    elif rainfall > 0:
                        rain_days = rng.randint(0, 2)
                    else:
                        rain_days = 0

                    # Maximum dry spell in month
                    if m in [11, 12, 1, 2, 3]:  # core wet months
                        if effective_rain_factor < 0.85:
                            # Drought / El Niño year dry spells
                            max_dry_days = rng.randint(12, 20)
                        else:
                            max_dry_days = rng.randint(4, 10)
                    elif m in [4, 10]:
                        max_dry_days = rng.randint(10, 22)
                    else:  # dry winter months (May-Sep)
                        max_dry_days = rng.randint(24, 31)

                    # Temperature
                    temp_max = round(base_max_t + warming_delta + rng.uniform(-0.8, 0.8), 1)
                    temp_min = round(base_min_t + warming_delta + rng.uniform(-0.7, 0.7), 1)
                    temp_mean = round((temp_max + temp_min) / 2.0, 1)

                    # Heat wave days (extreme heat threshold: >= 33°C for plateau, >= 35°C for lakeshore)
                    threshold = 34.5 if d_info['slug'] == 'salima' else 32.5
                    heat_sensitivity = d_info['heat_sensitivity']

                    if m in [10, 11] and temp_max >= threshold:
                        heat_days = int(round(rng.uniform(3, 10) * heat_sensitivity))
                        heat_events = 1 if heat_days >= 3 else 0
                    elif m in [12, 1, 2, 9] and temp_max >= threshold:
                        heat_days = int(round(rng.uniform(1, 4) * heat_sensitivity))
                        heat_events = 1 if heat_days >= 3 else 0
                    else:
                        heat_days = 0
                        heat_events = 0

                    notes = ""
                    if year in [2015, 2016, 2024] and m in [1, 2]:
                        notes = "Prolonged mid-season dry spell recorded during El Niño cycle."
                    elif year == 2023 and m == 3 and d_info['slug'] == 'blantyre':
                        notes = "Intense rainfall associated with Tropical Cyclone Freddy."

                    _, created = ClimateRecord.objects.get_or_create(
                        district=district,
                        year=year,
                        month=m,
                        record_type='historical',
                        defaults={
                            'source': hist_source,
                            'rainfall_mm': Decimal(str(rainfall)),
                            'rainfall_days': rain_days,
                            'dry_spell_days_max': max_dry_days,
                            'temp_min_c': Decimal(str(temp_min)),
                            'temp_mean_c': Decimal(str(temp_mean)),
                            'temp_max_c': Decimal(str(temp_max)),
                            'heat_wave_days': heat_days,
                            'heat_wave_events': heat_events,
                            'notes': notes,
                        }
                    )
                    if created:
                        total_records_created += 1

            # 3. Create Official Seasonal Outlook records for 2024/25
            for m in [11, 12, 1, 2, 3, 4]:
                m_year = 2024 if m in [11, 12] else 2025
                m_idx = m - 1
                base_r = d_info['base_rain'][m_idx]
                outlook_rain = round(base_r * 1.05, 1)  # slightly above normal forecast
                _, created = ClimateRecord.objects.get_or_create(
                    district=district,
                    year=m_year,
                    month=m,
                    record_type='outlook',
                    defaults={
                        'source': outlook_source,
                        'rainfall_mm': Decimal(str(outlook_rain)),
                        'rainfall_days': rng.randint(8, 18),
                        'dry_spell_days_max': rng.randint(5, 9),
                        'temp_min_c': Decimal(str(d_info['base_min_t'][m_idx])),
                        'temp_mean_c': Decimal(str((d_info['base_max_t'][m_idx] + d_info['base_min_t'][m_idx]) / 2)),
                        'temp_max_c': Decimal(str(d_info['base_max_t'][m_idx])),
                        'heat_wave_days': 1 if m in [11, 12] else 0,
                        'heat_wave_events': 0,
                        'notes': "Official 2024/25 Seasonal Outlook: Normal to above-normal precipitation expected.",
                    }
                )
                if created:
                    total_records_created += 1

            # 4. Create Illustrative Stress Scenario for 2024/25
            for m in [11, 12, 1, 2, 3, 4]:
                m_year = 2024 if m in [11, 12] else 2025
                m_idx = m - 1
                base_r = d_info['base_rain'][m_idx]
                scenario_rain = round(base_r * 0.82, 1)  # -18% deficit stress test
                _, created = ClimateRecord.objects.get_or_create(
                    district=district,
                    year=m_year,
                    month=m,
                    record_type='scenario',
                    defaults={
                        'source': scenario_source,
                        'rainfall_mm': Decimal(str(scenario_rain)),
                        'rainfall_days': rng.randint(5, 12),
                        'dry_spell_days_max': rng.randint(14, 21),  # severe dry spell
                        'temp_min_c': Decimal(str(d_info['base_min_t'][m_idx] + 1.5)),
                        'temp_mean_c': Decimal(str(((d_info['base_max_t'][m_idx] + d_info['base_min_t'][m_idx]) / 2) + 1.5)),
                        'temp_max_c': Decimal(str(d_info['base_max_t'][m_idx] + 1.8)),
                        'heat_wave_days': 5 if m in [11, 12] else 2,
                        'heat_wave_events': 1,
                        'notes': "Simulation Scenario: +1.5°C thermal elevation and increased dry spell frequency.",
                    }
                )
                if created:
                    total_records_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {len(DISTRICTS)} districts and {total_records_created} climate records (2005–2024 + 2024/25 outlook and scenarios)."
            )
        )
