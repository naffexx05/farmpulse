import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_seed():
    from django.contrib.auth.models import User
    from core.models import UserProfile
    from farms.models import Farm, Crop, Season, Planting, SeasonReview
    from climate.models import District
    from planner.models import Plan, PlanItem, PlanAssumption
    from innovation.models import SatelliteParcel, ParametricInsurancePolicy

    print("--- Seeding Miriam Chiphaka Account and 10 Years Data ---")

    # 1. District
    mzuzu_dist, _ = District.objects.get_or_create(
        slug='mzuzu',
        defaults={
            'name': 'Mzuzu',
            'region': 'northern',
            'latitude': Decimal('-11.458900'),
            'longitude': Decimal('34.015200'),
            'elevation_m': 1280,
            'description': 'Northern Highlands & Viphya-Mzuzu Plateau. Elevation 1,280m ASL, annual rainfall 1,150 mm, deep humic ferralsols and clay loam with exceptional moisture retention.'
        }
    )
    print(f"District: {mzuzu_dist.name}")

    # 2. User: Miriam Chiphaka
    username = 'miriam'
    user, created = User.objects.get_or_create(username=username)
    user.first_name = 'Miriam'
    user.last_name = 'Chiphaka'
    user.email = 'miriam.chiphaka@farmpulse.mw'
    user.set_password('Password123!')
    user.is_active = True
    user.save()
print(f"User '{user.username}' created/updated (Password: Password123!)")

profile, _ = UserProfile.objects.get_or_create(user=user)
profile.phone_number = '+265 88 412 8901'
profile.preferred_district = 'Mzuzu'
profile.land_unit = 'ha'
profile.yield_unit = 'kg'
profile.currency_format = 'standard'
profile.receive_sms_alerts = True
profile.share_anonymous_benchmarks = True
profile.save()
print("UserProfile configured.")

# 3. Reference Crops
crops = {c.slug: c for c in Crop.objects.all()}
maize = crops.get('maize')
beans = crops.get('common-beans')
soybeans = crops.get('soybeans')
groundnuts = crops.get('groundnuts')

# 4. Farm: Miriam Chiphaka Field
farm, f_created = Farm.objects.get_or_create(
    owner=user,
    name='Miriam Chiphaka Field',
    defaults={
        'location_description': 'Mzuzu, Northern Region (Zolozolo / Lunyangwa research corridor)',
        'latitude': Decimal('-11.458900'),
        'longitude': Decimal('34.015200'),
        'total_land_ha': Decimal('3.50'),
        'cultivated_land_ha': Decimal('3.20'),
        'irrigation_type': 'mixed',
        'water_notes': 'Perennial Lunyangwa stream boundary provides gravity dambo irrigation for winter sugar beans; summer season is reliable rain-fed (1,150 mm/year).',
        'soil_type': 'loam',
        'soil_notes': 'High organic matter humic ferralsols, deep clay loam profile (pH 5.8). High natural fertility, zero salinity, highly responsive to lime and basal NPK.',
        'seasonal_budget_mwk': Decimal('950000.00'),
        'available_labour_persons': 4,
        'labour_notes': 'Miriam, two adult household members, plus 2-3 casual ganyu workers during peak ridge forming, weeding, and pod harvesting.'
    }
)
if not f_created:
    farm.location_description = 'Mzuzu, Northern Region (Zolozolo / Lunyangwa research corridor)'
    farm.latitude = Decimal('-11.458900')
    farm.longitude = Decimal('34.015200')
    farm.total_land_ha = Decimal('3.50')
    farm.cultivated_land_ha = Decimal('3.20')
    farm.irrigation_type = 'mixed'
    farm.seasonal_budget_mwk = Decimal('950000.00')
    farm.available_labour_persons = 4
    farm.save()

farm.preferred_crops.set([beans, maize, soybeans, groundnuts])
print(f"Farm '{farm.name}' configured at {farm.location_description}.")

# 5. Clear old seasons for clean 10-year seed if re-running
farm.seasons.all().delete()

# 10 Years of Comprehensive Realistic Seasons (2015/16 to 2024/25)
history_timeline = [
    {
        'year': '2015/16',
        'start': date(2015, 11, 20),
        'end': date(2016, 5, 15),
        'notes': 'Regional El Niño dry spell year across southern Africa. Northern plateau received late rains, shielding Mzuzu from the extreme drought seen in the south.',
        'review': {
            'satisfaction': 3,
            'lessons': 'High-altitude humic soils conserved soil moisture far better than sandy plains. Early planting with hybrid SC 627 saved the maize crop.',
            'weather': 'Erratic early onset with a 14-day dry spell in January; recovered with steady March/April rains.',
            'market': 'National maize deficit pushed ADMARC and open market prices up late in the season.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.80'),
                'p_date': date(2015, 11, 25),
                'h_date': date(2016, 5, 2),
                'yield_kg': Decimal('3780.00'), # 2,100 kg/ha
                'cost': Decimal('85000.00'),
                'price': Decimal('180.00'),
                'rev': Decimal('680400.00'),
                'notes': 'Certified SC 627 highland hybrid; survived mid-season dry spell.'
            },
            {
                'crop': beans,
                'area': Decimal('1.00'),
                'p_date': date(2015, 12, 1),
                'h_date': date(2016, 3, 20),
                'yield_kg': Decimal('750.00'), # 750 kg/ha
                'cost': Decimal('48000.00'),
                'price': Decimal('420.00'),
                'rev': Decimal('315000.00'),
                'notes': 'Maluwa variety; strong local demand at Mzuzu Main Market.'
            }
        ]
    },
    {
        'year': '2016/17',
        'start': date(2016, 11, 15),
        'end': date(2017, 5, 20),
        'notes': 'Excellent recovery year with continuous, well-distributed rainfall (1,220 mm) across the Mzuzu plateau.',
        'review': {
            'satisfaction': 5,
            'lessons': 'Introduced soybeans for the first time; excellent nodulation and residual soil fertility for following maize crop.',
            'weather': 'Consistent rains from November through April with zero severe dry spells.',
            'market': 'Sold sugar beans to regional aggregators supplying Lilongwe supermarkets.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.70'),
                'p_date': date(2016, 11, 20),
                'h_date': date(2017, 5, 10),
                'yield_kg': Decimal('5780.00'), # 3,400 kg/ha
                'cost': Decimal('110000.00'),
                'price': Decimal('150.00'),
                'rev': Decimal('867000.00'),
                'notes': 'High grain density and full cob tip fill.'
            },
            {
                'crop': beans,
                'area': Decimal('0.90'),
                'p_date': date(2016, 11, 28),
                'h_date': date(2017, 3, 15),
                'yield_kg': Decimal('1035.00'), # 1,150 kg/ha
                'cost': Decimal('55000.00'),
                'price': Decimal('550.00'),
                'rev': Decimal('569250.00'),
                'notes': 'Kholophethe sugar beans; premium grade.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.50'),
                'p_date': date(2016, 12, 5),
                'h_date': date(2017, 4, 25),
                'yield_kg': Decimal('650.00'), # 1,300 kg/ha
                'cost': Decimal('35000.00'),
                'price': Decimal('320.00'),
                'rev': Decimal('208000.00'),
                'notes': 'Tikolore variety; inoculated with rhizobia biofertilizer.'
            }
        ]
    },
    {
        'year': '2017/18',
        'start': date(2017, 11, 18),
        'end': date(2018, 5, 15),
        'notes': 'National emergence of Fall Armyworm. Rigorous pest scouting and neem/biological spray prevented major foliage loss.',
        'review': {
            'satisfaction': 4,
            'lessons': 'Early pest trapping and scouting at vegetative stage 4 prevents 80% of cob damage.',
            'weather': 'Normal plateau rains (1,100 mm). Good flowering conditions.',
            'market': 'Bean prices remained firm; maize prices supported by national strategic grain reserve purchases.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.70'),
                'p_date': date(2017, 11, 24),
                'h_date': date(2018, 5, 8),
                'yield_kg': Decimal('4760.00'), # 2,800 kg/ha
                'cost': Decimal('135000.00'),
                'price': Decimal('190.00'),
                'rev': Decimal('904400.00'),
                'notes': 'Targeted cypermethrin sprays kept Fall Armyworm under control.'
            },
            {
                'crop': beans,
                'area': Decimal('1.00'),
                'p_date': date(2017, 12, 2),
                'h_date': date(2018, 3, 22),
                'yield_kg': Decimal('1000.00'), # 1,000 kg/ha
                'cost': Decimal('65000.00'),
                'price': Decimal('600.00'),
                'rev': Decimal('600000.00'),
                'notes': 'NUA 45 biofortified iron beans; high customer demand.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.40'),
                'p_date': date(2017, 12, 8),
                'h_date': date(2018, 4, 20),
                'yield_kg': Decimal('460.00'), # 1,150 kg/ha
                'cost': Decimal('32000.00'),
                'price': Decimal('360.00'),
                'rev': Decimal('165600.00'),
                'notes': 'Clean crop, zero rust symptoms.'
            }
        ]
    },
    {
        'year': '2018/19',
        'start': date(2018, 11, 15),
        'end': date(2019, 5, 22),
        'notes': 'Cyclone Idai struck southern Malawi with catastrophic flooding; Mzuzu highland escaped all cyclone damage and enjoyed a bumper season.',
        'review': {
            'satisfaction': 5,
            'lessons': 'Northern highlands serve as the stabilizing food supply anchor during southern disaster events.',
            'weather': 'Above average rainfall with ideal temperatures for grain maturation.',
            'market': 'High volume sales of dry beans and maize to southern traders.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.60'),
                'p_date': date(2018, 11, 22),
                'h_date': date(2019, 5, 12),
                'yield_kg': Decimal('5120.00'), # 3,200 kg/ha
                'cost': Decimal('145000.00'),
                'price': Decimal('240.00'),
                'rev': Decimal('1228800.00'),
                'notes': 'SC 627 single-cross hybrid; strong resistance to ear rot.'
            },
            {
                'crop': beans,
                'area': Decimal('1.10'),
                'p_date': date(2018, 11, 30),
                'h_date': date(2019, 3, 18),
                'yield_kg': Decimal('1210.00'), # 1,100 kg/ha
                'cost': Decimal('78000.00'),
                'price': Decimal('750.00'),
                'rev': Decimal('907500.00'),
                'notes': 'Kholophethe beans; sold 24 bags directly to Mzuzu central hospital contract.'
            },
            {
                'crop': groundnuts,
                'area': Decimal('0.40'),
                'p_date': date(2018, 12, 6),
                'h_date': date(2019, 4, 30),
                'yield_kg': Decimal('440.00'), # 1,100 kg/ha
                'cost': Decimal('38000.00'),
                'price': Decimal('520.00'),
                'rev': Decimal('228800.00'),
                'notes': 'CG7 high-oil confectionery groundnuts.'
            }
        ]
    },
    {
        'year': '2019/20',
        'start': date(2019, 11, 20),
        'end': date(2020, 5, 18),
        'notes': 'Stable growing season. Early 2020 COVID-19 border closures caused fertilizer shortages, managed with cattle manure and green manuring.',
        'review': {
            'satisfaction': 4,
            'lessons': 'Organic manure integration buffered the farm when synthetic fertilizer prices spiked due to border logistics.',
            'weather': 'Timely onset and gentle finish in April.',
            'market': 'Local food markets remained strong as households prioritized food storage.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.60'),
                'p_date': date(2019, 11, 26),
                'h_date': date(2020, 5, 8),
                'yield_kg': Decimal('5280.00'), # 3,300 kg/ha
                'cost': Decimal('165000.00'),
                'price': Decimal('220.00'),
                'rev': Decimal('1161600.00'),
                'notes': 'High starch and flour yield.'
            },
            {
                'crop': beans,
                'area': Decimal('1.00'),
                'p_date': date(2019, 12, 4),
                'h_date': date(2020, 3, 20),
                'yield_kg': Decimal('1150.00'), # 1,150 kg/ha
                'cost': Decimal('82000.00'),
                'price': Decimal('820.00'),
                'rev': Decimal('943000.00'),
                'notes': 'Excellent quality sugar beans.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.50'),
                'p_date': date(2019, 12, 10),
                'h_date': date(2020, 4, 25),
                'yield_kg': Decimal('650.00'), # 1,300 kg/ha
                'cost': Decimal('44000.00'),
                'price': Decimal('400.00'),
                'rev': Decimal('260000.00'),
                'notes': 'Sold to poultry feed mill in Luwinga industrial area.'
            }
        ]
    },
    {
        'year': '2020/21',
        'start': date(2020, 11, 15),
        'end': date(2021, 5, 25),
        'notes': 'National La Niña season with abundant rainfall (1,290 mm). Peak historic yields recorded on the farm.',
        'review': {
            'satisfaction': 5,
            'lessons': 'Contour ridges and vetiver grass prevented topsoil erosion under heavy torrential rains.',
            'weather': 'Heavy, continuous rainfall; optimal soil moisture throughout vegetative and grain-fill phases.',
            'market': 'Sold record tonnage to commercial agro-dealers in Mzuzu.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.60'),
                'p_date': date(2020, 11, 20),
                'h_date': date(2021, 5, 14),
                'yield_kg': Decimal('5760.00'), # 3,600 kg/ha
                'cost': Decimal('195000.00'),
                'price': Decimal('250.00'),
                'rev': Decimal('1440000.00'),
                'notes': 'DKC 80-33 and SC 627 hybrids produced top yield.'
            },
            {
                'crop': beans,
                'area': Decimal('1.00'),
                'p_date': date(2020, 11, 28),
                'h_date': date(2021, 3, 16),
                'yield_kg': Decimal('1250.00'), # 1,250 kg/ha
                'cost': Decimal('95000.00'),
                'price': Decimal('950.00'),
                'rev': Decimal('1187500.00'),
                'notes': 'Highest ever bean harvest per hectare.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.50'),
                'p_date': date(2020, 12, 5),
                'h_date': date(2021, 4, 28),
                'yield_kg': Decimal('700.00'), # 1,400 kg/ha
                'cost': Decimal('50000.00'),
                'price': Decimal('480.00'),
                'rev': Decimal('336000.00'),
                'notes': 'Tikolore variety; thick pod clustering.'
            }
        ]
    },
    {
        'year': '2021/22',
        'start': date(2021, 11, 18),
        'end': date(2022, 5, 20),
        'notes': 'Moderate season. Cyclone Ana devastated southern lowlands; northern plateau had mild hail in December but quick vegetative recovery.',
        'review': {
            'satisfaction': 4,
            'lessons': 'Input prices escalated sharply (NPK and Urea doubled). Intercropping legumes with maize reduced synthetic fertilizer dependency.',
            'weather': '1,120 mm rainfall; cool temperatures in February slowed grain drying but enhanced grain test weight.',
            'market': 'Grain prices rose sharply due to national deficits in the southern region.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.50'),
                'p_date': date(2021, 11, 25),
                'h_date': date(2022, 5, 10),
                'yield_kg': Decimal('4650.00'), # 3,100 kg/ha
                'cost': Decimal('240000.00'),
                'price': Decimal('320.00'),
                'rev': Decimal('1488000.00'),
                'notes': 'SC 627 highland hybrid.'
            },
            {
                'crop': beans,
                'area': Decimal('1.10'),
                'p_date': date(2021, 12, 2),
                'h_date': date(2022, 3, 22),
                'yield_kg': Decimal('1155.00'), # 1,050 kg/ha
                'cost': Decimal('120000.00'),
                'price': Decimal('1200.00'),
                'rev': Decimal('1386000.00'),
                'notes': 'Kholophethe sugar beans surpassed MWK 1,000/kg threshold.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.50'),
                'p_date': date(2021, 12, 8),
                'h_date': date(2022, 4, 26),
                'yield_kg': Decimal('625.00'), # 1,250 kg/ha
                'cost': Decimal('65000.00'),
                'price': Decimal('600.00'),
                'rev': Decimal('375000.00'),
                'notes': 'Solid return on investment.'
            }
        ]
    },
    {
        'year': '2022/23',
        'start': date(2022, 11, 15),
        'end': date(2023, 5, 25),
        'notes': 'Cyclone Freddy struck southern Malawi in March 2023. Mzuzu plateau maintained consistent rainfall, high grain health, and record selling margins.',
        'review': {
            'satisfaction': 5,
            'lessons': 'Reinvested season profits into Lunyangwa stream intake weir for expanded dry-season gravity furrow irrigation.',
            'weather': 'Steady highland rainfall (1,180 mm) without flooding or prolonged droughts.',
            'market': 'Commodity traders from Blantyre and Lilongwe arrived with 10-tonne trucks to buy grain directly at farm gate.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.50'),
                'p_date': date(2022, 11, 20),
                'h_date': date(2023, 5, 15),
                'yield_kg': Decimal('4950.00'), # 3,300 kg/ha
                'cost': Decimal('380000.00'),
                'price': Decimal('550.00'),
                'rev': Decimal('2722500.00'),
                'notes': 'Top-quality grain sold to commercial aggregators.'
            },
            {
                'crop': beans,
                'area': Decimal('1.10'),
                'p_date': date(2022, 11, 28),
                'h_date': date(2023, 3, 20),
                'yield_kg': Decimal('1265.00'), # 1,150 kg/ha
                'cost': Decimal('180000.00'),
                'price': Decimal('1650.00'),
                'rev': Decimal('2087250.00'),
                'notes': 'Record bean revenues; gross margin over MWK 1.9 Million.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.50'),
                'p_date': date(2022, 12, 6),
                'h_date': date(2023, 4, 28),
                'yield_kg': Decimal('675.00'), # 1,350 kg/ha
                'cost': Decimal('95000.00'),
                'price': Decimal('850.00'),
                'rev': Decimal('573750.00'),
                'notes': 'Certified Tikolore seed.'
            }
        ]
    },
    {
        'year': '2023/24',
        'start': date(2023, 11, 18),
        'end': date(2024, 5, 24),
        'notes': 'Declared national El Niño disaster across 23 districts in Malawi. Mzuzu remained resilient, producing food for the nation with 1,080 mm of rainfall.',
        'review': {
            'satisfaction': 5,
            'lessons': 'The FarmPulse highland advisory saved us from premature harvesting. Mzuzu confirmed as the premier national climate refuge.',
            'weather': 'Normal highland distribution with sufficient rainfall to bring all cereal and legume crops to physiological maturity.',
            'market': 'Maize prices reached MWK 850/kg; dry sugar beans reached MWK 2,400/kg. Highest gross margin decade record.'
        },
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.50'),
                'p_date': date(2023, 11, 24),
                'h_date': date(2024, 5, 12),
                'yield_kg': Decimal('4650.00'), # 3,100 kg/ha
                'cost': Decimal('490000.00'),
                'price': Decimal('850.00'),
                'rev': Decimal('3952500.00'),
                'notes': 'SC 627 highland hybrid; dense grain.'
            },
            {
                'crop': beans,
                'area': Decimal('1.10'),
                'p_date': date(2023, 12, 2),
                'h_date': date(2024, 3, 24),
                'yield_kg': Decimal('1210.00'), # 1,100 kg/ha
                'cost': Decimal('240000.00'),
                'price': Decimal('2400.00'),
                'rev': Decimal('2904000.00'),
                'notes': 'Premium red speckled sugar beans sold at record price.'
            },
            {
                'crop': groundnuts,
                'area': Decimal('0.50'),
                'p_date': date(2023, 12, 8),
                'h_date': date(2024, 5, 5),
                'yield_kg': Decimal('525.00'), # 1,050 kg/ha
                'cost': Decimal('135000.00'),
                'price': Decimal('1800.00'),
                'rev': Decimal('945000.00'),
                'notes': 'CG7 certified seed; sold to Mzuzu oil mill.'
            }
        ]
    },
    {
        'year': '2024/25',
        'start': date(2024, 11, 15),
        'end': date(2025, 5, 30),
        'notes': 'Current 2024/25 growing season. Excellent vegetative vigor, early weeding completed, crop stands are exceptionally healthy.',
        'review': None, # Currently ongoing season!
        'plantings': [
            {
                'crop': maize,
                'area': Decimal('1.50'),
                'p_date': date(2024, 11, 22),
                'h_date': None,
                'yield_kg': None,
                'cost': Decimal('420000.00'),
                'price': None,
                'rev': None,
                'notes': 'SC 627 highland hybrid; currently in late vegetative stage, top-dressed with Urea.'
            },
            {
                'crop': beans,
                'area': Decimal('1.10'),
                'p_date': date(2024, 12, 2),
                'h_date': None,
                'yield_kg': None,
                'cost': Decimal('210000.00'),
                'price': None,
                'rev': None,
                'notes': 'Kholophethe sugar beans; healthy canopy, first flower flush emerging.'
            },
            {
                'crop': soybeans,
                'area': Decimal('0.60'),
                'p_date': date(2024, 12, 8),
                'h_date': None,
                'yield_kg': None,
                'cost': Decimal('125000.00'),
                'price': None,
                'rev': None,
                'notes': 'Tikolore variety; full ground cover established.'
            }
        ]
    }
]

created_seasons = 0
created_plantings = 0

for item in history_timeline:
    season_name = f"{item['year']} Season"
    s = Season.objects.create(
        farm=farm,
        name=season_name,
        start_date=item['start'],
        end_date=item['end'],
        notes=item['notes']
    )
    created_seasons += 1

    for p in item['plantings']:
        Planting.objects.create(
            season=s,
            crop=p['crop'],
            area_ha=p['area'],
            planting_date=p['p_date'],
            harvest_date=p['h_date'],
            yield_kg=p['yield_kg'],
            production_cost_mwk=p['cost'],
            selling_price_mwk_per_kg=p['price'],
            revenue_mwk=p['rev'],
            notes=p['notes']
        )
        created_plantings += 1

    rev_data = item['review']
    if rev_data:
        SeasonReview.objects.create(
            season=s,
            overall_satisfaction=rev_data['satisfaction'],
            lessons_learned=rev_data['lessons'],
            weather_assessment=rev_data['weather'],
            market_assessment=rev_data['market']
        )

print(f"Created {created_seasons} seasons with {created_plantings} plantings and verified reviews.")

# 6. Active Strategic Plan in Planner
farm.plans.all().delete()
plan = Plan.objects.create(
    farm=farm,
    name='2024/25 Mzuzu Highland High-Margin Portfolio',
    strategy_type='balanced',
    status='active',
    total_land_ha=Decimal('3.20'),
    total_budget_mwk=Decimal('950000.00'),
    total_expected_cost_mwk=Decimal('755000.00'),
    total_expected_revenue_mwk=Decimal('5820000.00'),
    total_expected_margin_mwk=Decimal('5065000.00'),
    notes='Agro-Ecological portfolio optimized for Mzuzu plateau humic ferralsols. Prioritizes premium sugar beans and high-yield hybrid SC 627.'
)

PlanItem.objects.create(
    plan=plan,
    crop=beans,
    area_ha=Decimal('1.10'),
    expected_yield_kg_per_ha=Decimal('1200.00'),
    expected_yield_kg_total=Decimal('1320.00'),
    expected_cost_per_ha_mwk=Decimal('190909.00'),
    expected_total_cost_mwk=Decimal('210000.00'),
    expected_selling_price_mwk_per_kg=Decimal('2400.00'),
    expected_revenue_mwk=Decimal('3168000.00'),
    expected_gross_margin_mwk=Decimal('2958000.00'),
    break_even_price_mwk_per_kg=Decimal('159.00'),
    notes='Premier cash legume: Kholophethe / NUA 45 biofortified iron beans.'
)

PlanItem.objects.create(
    plan=plan,
    crop=maize,
    area_ha=Decimal('1.50'),
    expected_yield_kg_per_ha=Decimal('3200.00'),
    expected_yield_kg_total=Decimal('4800.00'),
    expected_cost_per_ha_mwk=Decimal('280000.00'),
    expected_total_cost_mwk=Decimal('420000.00'),
    expected_selling_price_mwk_per_kg=Decimal('850.00'),
    expected_revenue_mwk=Decimal('4080000.00'),
    expected_gross_margin_mwk=Decimal('3660000.00'),
    break_even_price_mwk_per_kg=Decimal('87.50'),
    notes='Household subsistence reserve (1,200kg) + commercial grain surplus.'
)

PlanItem.objects.create(
    plan=plan,
    crop=soybeans,
    area_ha=Decimal('0.60'),
    expected_yield_kg_per_ha=Decimal('1350.00'),
    expected_yield_kg_total=Decimal('810.00'),
    expected_cost_per_ha_mwk=Decimal('208333.00'),
    expected_total_cost_mwk=Decimal('125000.00'),
    expected_selling_price_mwk_per_kg=Decimal('950.00'),
    expected_revenue_mwk=Decimal('769500.00'),
    expected_gross_margin_mwk=Decimal('644500.00'),
    break_even_price_mwk_per_kg=Decimal('154.00'),
    notes='Biological nitrogen fixation for soil fertility conservation.'
)

PlanAssumption.objects.create(
    plan=plan,
    category='price',
    parameter_name='Mzuzu Wholesale Sugar Bean Price',
    value_used='MWK 2,400 / kg',
    source_note='Mzuzu Main Market Agro-Commodity Board Dec 2024'
)
PlanAssumption.objects.create(
    plan=plan,
    category='yield',
    parameter_name='Highland Hybrid Maize SC 627 Yield',
    value_used='3,200 kg / ha',
    source_note='DARS Lunyangwa / Bvumbwe Research Station calibrated trials'
)
PlanAssumption.objects.create(
    plan=plan,
    category='climate',
    parameter_name='Seasonal Rainfall Outlook',
    value_used='1,150 mm Normal to Above Normal',
    source_note='DCCMS Mzuzu Airport Synoptic Weather Station'
)
print("Strategic Crop Plan & Economic Assumptions saved.")

# 7. Satellite Digital Twin Parcel for Miriam Chiphaka Field
farm.satellite_parcels.all().delete()
parcel = SatelliteParcel.objects.create(
    farm=farm,
    name='Miriam Chiphaka Field — Lunyangwa Plot',
    crop=beans,
    centroid_lat=Decimal('-11.458900'),
    centroid_lng=Decimal('34.015200'),
    calculated_area_ha=Decimal('3.20'),
    polygon_geojson={
        "type": "Polygon",
        "coordinates": [[
            [34.0135, -11.4575],
            [34.0170, -11.4572],
            [34.0168, -11.4605],
            [34.0133, -11.4608],
            [34.0135, -11.4575]
        ]]
    },
    mean_ndvi=Decimal('0.72'),
    soil_moisture_pct=Decimal('32.5'),
    stress_level='optimal'
)
print(f"Satellite Digital Twin Parcel created: NDVI {parcel.mean_ndvi}, Moisture {parcel.soil_moisture_pct}%.")

# 8. Parametric Insurance Policy
farm.insurance_policies.all().delete()
policy = ParametricInsurancePolicy.objects.create(
    farm=farm,
    policy_number='FP-MZU-2024-9104',
    crop=beans,
    coverage_ha=Decimal('3.20'),
    sum_insured_mwk=Decimal('1200000.00'),
    premium_mwk=Decimal('72000.00'),
    trigger_dry_spell_days=14,
    trigger_window_start=date(2024, 12, 1),
    trigger_window_end=date(2025, 3, 31),
    status='active',
    observed_dry_spell_days=4,
    mobile_money_provider='TNM Mpamba',
    payout_recipient_phone='+265 88 412 8901',
    transaction_ref=''
)
print(f"Parametric Insurance Policy created: {policy.policy_number} ({policy.status}).")
    print("\n--- MIRIAM CHIPHAKA SEEDING COMPLETE! ---")


if __name__ == '__main__':
    run_seed()

