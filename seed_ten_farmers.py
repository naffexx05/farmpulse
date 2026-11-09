import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile
from farms.models import Farm, Crop, Season, Planting, SeasonReview
from climate.models import District
from planner.models import Plan, PlanItem, PlanAssumption
from innovation.models import SatelliteParcel, ParametricInsurancePolicy

print("=== SEEDING 12 REALISTIC MALAWIAN FARMERS & ADMINISTRATOR ===")

# Reference crops
crops = {c.slug: c for c in Crop.objects.all()}
maize = crops.get('maize')
beans = crops.get('common-beans')
soybeans = crops.get('soybeans')
groundnuts = crops.get('groundnuts')
rice = crops.get('rice') or maize
potatoes = crops.get('irish-potatoes') or beans
sorghum = crops.get('sorghum') or maize
tobacco = crops.get('tobacco') or maize

# 1. Administrator User
admin_user, _ = User.objects.get_or_create(username='admin')
admin_user.first_name = 'Dr. Patrick'
admin_user.last_name = 'Chikoti'
admin_user.email = 'admin@farmpulse.mw'
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.set_password('Password123!')
admin_user.save()

admin_prof, _ = UserProfile.objects.get_or_create(user=admin_user)
admin_prof.phone_number = '+265 88 100 2000'
admin_prof.preferred_district = 'Lilongwe'
admin_prof.save()
print("Administrator 'admin' (Dr. Patrick Chikoti) verified.")

# Also ensure naffe is staff & superuser
naffe_user = User.objects.filter(username='naffe').first()
if naffe_user:
    naffe_user.is_staff = True
    naffe_user.is_superuser = True
    naffe_user.set_password('Password123!')
    naffe_user.save()
    print("User 'naffe' upgraded to staff/superuser.")

# 12 Malawian Farmer Profiles
farmer_specs = [
    {
        'username': 'miriam',
        'first_name': 'Miriam',
        'last_name': 'Chiphaka',
        'email': 'miriam.chiphaka@farmpulse.mw',
        'phone': '+265 88 412 8901',
        'district': 'Mzuzu',
        'farm_name': 'Miriam Chiphaka Field',
        'location': 'Mzuzu, Northern Region (Lunyangwa research corridor)',
        'lat': Decimal('-11.4395'),
        'lng': Decimal('34.0042'),
        'total_land': Decimal('3.50'),
        'soil': 'sandy_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('950000.00'),
        'labour': 4,
        'crops': [maize, beans, soybeans],
        'ndvi': Decimal('0.72'),
        'stress': 'optimal',
        'cooperative': 'Lunyangwa Dairy & Legume Cooperative',
        'seasons_count': 10,
    },
    {
        'username': 'kphiri',
        'first_name': 'Kondwani',
        'last_name': 'Phiri',
        'email': 'kondwani.phiri@farmpulse.mw',
        'phone': '+265 99 341 5521',
        'district': 'Lilongwe',
        'farm_name': 'Chitukuko Mixed Farm',
        'location': 'Mitundu, Lilongwe Central Plain',
        'lat': Decimal('-14.1200'),
        'lng': Decimal('33.7800'),
        'total_land': Decimal('4.20'),
        'soil': 'red_clay',
        'irrigation': 'rainfed',
        'budget': Decimal('1400000.00'),
        'labour': 5,
        'crops': [maize, groundnuts, soybeans],
        'ndvi': Decimal('0.68'),
        'stress': 'optimal',
        'cooperative': 'Mitundu Grain Growers Association',
        'seasons_count': 4,
    },
    {
        'username': 'cbanda',
        'first_name': 'Chimwemwe',
        'last_name': 'Banda',
        'email': 'chimwemwe.banda@farmpulse.mw',
        'phone': '+265 88 719 3342',
        'district': 'Kasungu',
        'farm_name': 'Banda Agro-Enterprise',
        'location': 'Chinkhoma, Kasungu Tobacco & Legume Belt',
        'lat': Decimal('-13.0333'),
        'lng': Decimal('33.4833'),
        'total_land': Decimal('5.00'),
        'soil': 'sandy_clay',
        'irrigation': 'rainfed',
        'budget': Decimal('1800000.00'),
        'labour': 6,
        'crops': [soybeans, groundnuts, maize],
        'ndvi': Decimal('0.58'),
        'stress': 'moderate_stress',
        'cooperative': 'Kasungu Legume Seed Multiplication Union',
        'seasons_count': 5,
    },
    {
        'username': 'amsiska',
        'first_name': 'Alinane',
        'last_name': 'Msiska',
        'email': 'alinane.msiska@farmpulse.mw',
        'phone': '+265 99 822 1044',
        'district': 'Karonga',
        'farm_name': 'Rukuru River Irrigation Scheme',
        'location': 'Karonga North Lakeshore Plain',
        'lat': Decimal('-9.9333'),
        'lng': Decimal('33.9333'),
        'total_land': Decimal('2.80'),
        'soil': 'alluvial',
        'irrigation': 'canal',
        'budget': Decimal('1100000.00'),
        'labour': 4,
        'crops': [rice, maize],
        'ndvi': Decimal('0.74'),
        'stress': 'optimal',
        'cooperative': 'Karonga Rice Growers Cooperative',
        'seasons_count': 4,
    },
    {
        'username': 'tgondwe',
        'first_name': 'Thokozani',
        'last_name': 'Gondwe',
        'email': 'thokozani.gondwe@farmpulse.mw',
        'phone': '+265 88 563 9081',
        'district': 'Rumphi',
        'farm_name': 'Gondwe Highland Terraces',
        'location': 'Livingstonia Slopes, Rumphi Highlands',
        'lat': Decimal('-10.6000'),
        'lng': Decimal('34.1100'),
        'total_land': Decimal('3.00'),
        'soil': 'clay_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('850000.00'),
        'labour': 3,
        'crops': [beans, maize],
        'ndvi': Decimal('0.66'),
        'stress': 'optimal',
        'cooperative': 'Northern Highlands Horticulture Trust',
        'seasons_count': 3,
    },
    {
        'username': 'ckachale',
        'first_name': 'Chisomo',
        'last_name': 'Kachale',
        'email': 'chisomo.kachale@farmpulse.mw',
        'phone': '+265 99 470 1199',
        'district': 'Dedza',
        'farm_name': 'Kachale Hillside Potato Plot',
        'location': 'Dedza Boma Highlands (Cold Zone)',
        'lat': Decimal('-14.3800'),
        'lng': Decimal('34.3300'),
        'total_land': Decimal('2.50'),
        'soil': 'volcanic_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('1200000.00'),
        'labour': 5,
        'crops': [potatoes, beans, maize],
        'ndvi': Decimal('0.70'),
        'stress': 'optimal',
        'cooperative': 'Dedza Potato Farmers Association',
        'seasons_count': 4,
    },
    {
        'username': 'fmwale',
        'first_name': 'Fatsani',
        'last_name': 'Mwale',
        'email': 'fatsani.mwale@farmpulse.mw',
        'phone': '+265 88 333 7812',
        'district': 'Salima',
        'farm_name': 'Lifidzi Lakeshore Farm',
        'location': 'Salima Lakeshore, Lifidzi Valley',
        'lat': Decimal('-13.7800'),
        'lng': Decimal('34.4500'),
        'total_land': Decimal('3.80'),
        'soil': 'sandy_alluvium',
        'irrigation': 'treadle',
        'budget': Decimal('980000.00'),
        'labour': 4,
        'crops': [sorghum, groundnuts, maize],
        'ndvi': Decimal('0.61'),
        'stress': 'optimal',
        'cooperative': 'Salima Cotton & Sorghum Producers',
        'seasons_count': 3,
    },
    {
        'username': 'gchinkhunda',
        'first_name': 'Grace',
        'last_name': 'Chinkhunda',
        'email': 'grace.chinkhunda@farmpulse.mw',
        'phone': '+265 99 118 4422',
        'district': 'Balaka',
        'farm_name': 'Chinkhunda Climate Resilient Plot',
        'location': 'Rivi Rivi Valley, Balaka District',
        'lat': Decimal('-14.9800'),
        'lng': Decimal('34.9500'),
        'total_land': Decimal('2.20'),
        'soil': 'sandy_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('620000.00'),
        'labour': 3,
        'crops': [sorghum, groundnuts],
        'ndvi': Decimal('0.48'),
        'stress': 'moderate_stress',
        'cooperative': 'Shire Valley Climate Resilience Network',
        'seasons_count': 4,
    },
    {
        'username': 'tmatenje',
        'first_name': 'Tadala',
        'last_name': 'Matenje',
        'email': 'tadala.matenje@farmpulse.mw',
        'phone': '+265 88 901 6723',
        'district': 'Thyolo',
        'farm_name': 'Matenje Green Slopes',
        'location': 'Bvumbwe / Luchenza corridor, Thyolo',
        'lat': Decimal('-15.9500'),
        'lng': Decimal('35.1500'),
        'total_land': Decimal('3.20'),
        'soil': 'red_clay_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('1350000.00'),
        'labour': 5,
        'crops': [maize, beans],
        'ndvi': Decimal('0.75'),
        'stress': 'optimal',
        'cooperative': 'Thyolo Smallholder Planters Cooperative',
        'seasons_count': 3,
    },
    {
        'username': 'ynkhoma',
        'first_name': 'Yamikani',
        'last_name': 'Nkhoma',
        'email': 'yamikani.nkhoma@farmpulse.mw',
        'phone': '+265 99 655 4310',
        'district': 'Zomba',
        'farm_name': 'Likangala Horticultural Gardens',
        'location': 'Likangala River Basin, Zomba Rural',
        'lat': Decimal('-15.3800'),
        'lng': Decimal('35.3200'),
        'total_land': Decimal('1.80'),
        'soil': 'alluvial_loam',
        'irrigation': 'solar_drip',
        'budget': Decimal('1150000.00'),
        'labour': 4,
        'crops': [beans, maize],
        'ndvi': Decimal('0.78'),
        'stress': 'optimal',
        'cooperative': 'Zomba Peri-Urban Market Gardeners',
        'seasons_count': 3,
    },
    {
        'username': 'ebanda',
        'first_name': 'Enock',
        'last_name': 'Banda',
        'email': 'enock.banda@farmpulse.mw',
        'phone': '+265 88 224 8890',
        'district': 'Mchinji',
        'farm_name': 'Mchinji Border Agro-Hub',
        'location': 'Kamwendo Trading Centre, Mchinji West',
        'lat': Decimal('-13.8000'),
        'lng': Decimal('32.8800'),
        'total_land': Decimal('6.00'),
        'soil': 'fertile_clay',
        'irrigation': 'rainfed',
        'budget': Decimal('2200000.00'),
        'labour': 7,
        'crops': [soybeans, groundnuts, maize],
        'ndvi': Decimal('0.69'),
        'stress': 'optimal',
        'cooperative': 'Kamwendo Grain Exporters Union',
        'seasons_count': 4,
    },
    {
        'username': 'lchibambo',
        'first_name': 'Lusekelo',
        'last_name': 'Chibambo',
        'email': 'lusekelo.chibambo@farmpulse.mw',
        'phone': '+265 99 778 3311',
        'district': 'Mzimba',
        'farm_name': 'Mzimba South Livestock & Grain Farm',
        'location': 'Jenda, Mzimba South Plain',
        'lat': Decimal('-12.2500'),
        'lng': Decimal('33.6000'),
        'total_land': Decimal('4.50'),
        'soil': 'sandy_loam',
        'irrigation': 'rainfed',
        'budget': Decimal('1250000.00'),
        'labour': 5,
        'crops': [maize, soybeans, groundnuts],
        'ndvi': Decimal('0.63'),
        'stress': 'optimal',
        'cooperative': 'Mzimba Legume Growers Cooperative',
        'seasons_count': 3,
    },
]

for idx, spec in enumerate(farmer_specs, start=1):
    u, _ = User.objects.get_or_create(username=spec['username'])
    u.first_name = spec['first_name']
    u.last_name = spec['last_name']
    u.email = spec['email']
    u.set_password('Password123!')
    u.is_active = True
    u.save()

    prof, _ = UserProfile.objects.get_or_create(user=u)
    prof.phone_number = spec['phone']
    prof.preferred_district = spec['district']
    prof.land_unit = 'ha'
    prof.yield_unit = 'kg'
    prof.receive_sms_alerts = True
    prof.share_anonymous_benchmarks = True
    prof.save()

    # Farm
    farm, _ = Farm.objects.get_or_create(
        owner=u,
        name=spec['farm_name'],
        defaults={
            'location_description': spec['location'],
            'latitude': spec['lat'],
            'longitude': spec['lng'],
            'total_land_ha': spec['total_land'],
            'cultivated_land_ha': spec['total_land'] * Decimal('0.85'),
            'irrigation_type': spec['irrigation'],
            'soil_type': spec['soil'],
            'seasonal_budget_mwk': spec['budget'],
            'available_labour_persons': spec['labour'],
            'water_notes': f"Managed by {spec['cooperative']}.",
            'soil_notes': f"Dominant soil: {spec['soil']}. Standard soil test completed.",
            'labour_notes': f"{spec['labour']} full-time household & hired seasonal workers.",
        }
    )
    farm.location_description = spec['location']
    farm.latitude = spec['lat']
    farm.longitude = spec['lng']
    farm.total_land_ha = spec['total_land']
    farm.cultivated_land_ha = spec['total_land'] * Decimal('0.85')
    farm.irrigation_type = spec['irrigation']
    farm.soil_type = spec['soil']
    farm.seasonal_budget_mwk = spec['budget']
    farm.available_labour_persons = spec['labour']
    farm.save()

    valid_crops = [c for c in spec['crops'] if c]
    farm.preferred_crops.set(valid_crops)

    # Seasons & Plantings
    years = [
        ('2024/25 Season', date(2024, 11, 15), date(2025, 4, 30)),
        ('2023/24 Season', date(2023, 11, 15), date(2024, 4, 30)),
        ('2022/23 Season', date(2022, 11, 15), date(2023, 4, 30)),
        ('2021/22 Season', date(2021, 11, 15), date(2022, 4, 30)),
        ('2020/21 Season', date(2020, 11, 15), date(2021, 4, 30)),
    ][:spec['seasons_count']]

    for s_name, s_start, s_end in years:
        season, _ = Season.objects.get_or_create(
            farm=farm,
            name=s_name,
            defaults={'start_date': s_start, 'end_date': s_end, 'notes': f"Recorded for {spec['cooperative']}"}
        )
        if season.plantings.count() == 0:
            for crop_obj in valid_crops:
                area = (spec['total_land'] * Decimal('0.85') / len(valid_crops)).quantize(Decimal('0.01'))
                cost = (spec['budget'] / len(valid_crops)).quantize(Decimal('0.01'))
                # realistic yields
                if crop_obj.slug == 'maize':
                    yield_kg = (area * Decimal('3200')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('380')).quantize(Decimal('0.01'))
                elif crop_obj.slug in ['soybeans', 'common-beans']:
                    yield_kg = (area * Decimal('1500')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('750')).quantize(Decimal('0.01'))
                elif crop_obj.slug == 'groundnuts':
                    yield_kg = (area * Decimal('1400')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('900')).quantize(Decimal('0.01'))
                elif crop_obj.slug == 'rice':
                    yield_kg = (area * Decimal('3800')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('650')).quantize(Decimal('0.01'))
                elif crop_obj.slug == 'irish-potatoes':
                    yield_kg = (area * Decimal('8500')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('320')).quantize(Decimal('0.01'))
                else:
                    yield_kg = (area * Decimal('2000')).quantize(Decimal('0.01'))
                    rev = (yield_kg * Decimal('450')).quantize(Decimal('0.01'))

                Planting.objects.create(
                    season=season,
                    crop=crop_obj,
                    area_ha=area,
                    planting_date=s_start + timedelta(days=10),
                    harvest_date=s_end - timedelta(days=15),
                    yield_kg=yield_kg,
                    production_cost_mwk=cost,
                    revenue_mwk=rev,
                    notes=f"Certified seeds used. FarmPulse planner recommendations followed."
                )

    # Generated Plan
    plan_name = f"2024/25 {spec['district']} High-Yield Commercial Plan"
    plan, _ = Plan.objects.get_or_create(
        farm=farm,
        name=plan_name,
        defaults={
            'strategy_type': 'balanced',
            'status': 'active',
            'total_land_ha': spec['total_land'],
            'total_budget_mwk': spec['budget'],
            'total_expected_cost_mwk': spec['budget'],
            'total_expected_revenue_mwk': spec['budget'] * Decimal('2.4'),
            'total_expected_margin_mwk': spec['budget'] * Decimal('1.4'),
            'notes': f"Generated for {spec['first_name']} {spec['last_name']} under {spec['cooperative']}.",
        }
    )

    # Satellite Parcel
    SatelliteParcel.objects.get_or_create(
        farm=farm,
        name=f"{spec['farm_name']} — Field A",
        defaults={
            'crop': valid_crops[0] if valid_crops else None,
            'centroid_lat': spec['lat'],
            'centroid_lng': spec['lng'],
            'calculated_area_ha': spec['total_land'],
            'mean_ndvi': spec['ndvi'],
            'soil_moisture_pct': Decimal('28.5') if spec['stress'] == 'optimal' else Decimal('19.2'),
            'stress_level': spec['stress'],
            'polygon_geojson': {
                "type": "Polygon",
                "coordinates": [[
                    [float(spec['lng']) - 0.002, float(spec['lat']) - 0.002],
                    [float(spec['lng']) + 0.002, float(spec['lat']) - 0.002],
                    [float(spec['lng']) + 0.002, float(spec['lat']) + 0.002],
                    [float(spec['lng']) - 0.002, float(spec['lat']) + 0.002],
                    [float(spec['lng']) - 0.002, float(spec['lat']) - 0.002]
                ]]
            }
        }
    )

    # Parametric Insurance Policy
    pol_num = f"FP-MLW-2024-{idx:04d}"
    ParametricInsurancePolicy.objects.get_or_create(
        farm=farm,
        policy_number=pol_num,
        defaults={
            'crop': valid_crops[0] if valid_crops else maize,
            'coverage_ha': spec['total_land'] * Decimal('0.8'),
            'sum_insured_mwk': spec['budget'] * Decimal('1.2'),
            'premium_mwk': spec['budget'] * Decimal('0.06'),
            'trigger_dry_spell_days': 14,
            'trigger_window_start': date(2024, 12, 1),
            'trigger_window_end': date(2025, 3, 31),
            'status': 'triggered' if spec['stress'] == 'moderate_stress' else 'active',
            'observed_dry_spell_days': 15 if spec['stress'] == 'moderate_stress' else 7,
            'payout_mwk': (spec['budget'] * Decimal('1.2')) if spec['stress'] == 'moderate_stress' else Decimal('0.00'),
            'mobile_money_provider': 'Airtel Money' if idx % 2 == 0 else 'TNM Mpamba',
            'payout_recipient_phone': spec['phone'],
            'transaction_ref': f"TXN-AIRTEL-{idx}98765" if spec['stress'] == 'moderate_stress' else '',
        }
    )

    print(f"[{idx}/12] Farmer '{spec['first_name']} {spec['last_name']}' ({spec['district']}) seeded. Farm: {spec['farm_name']}")

print("\n=== TOTAL SEEDING COMPLETE ===")
print(f"Total Users: {User.objects.count()}")
print(f"Total Farms: {Farm.objects.count()}")
print(f"Total Seasons: {Season.objects.count()}")
print(f"Total Plantings: {Planting.objects.count()}")
print(f"Total Plans: {Plan.objects.count()}")
print(f"Total Satellite Parcels: {SatelliteParcel.objects.count()}")
print(f"Total Parametric Policies: {ParametricInsurancePolicy.objects.count()}")
