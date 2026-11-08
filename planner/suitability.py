"""
FarmPulse Malawi - Agro-Ecological Zone (AEZ) & Regional Crop Suitability Engine
Anchored to official DARS (Department of Agricultural Research Services) and
Ministry of Agriculture classification across Malawian districts.
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal


# ==============================================================================
# Comprehensive Malawi Agro-Ecological District Profiles
# ==============================================================================

DISTRICT_AGRO_PROFILES: Dict[str, Dict[str, Any]] = {
    'lilongwe': {
        'name': 'Lilongwe',
        'region': 'Central Region',
        'aez_name': 'Central Plateau & Lilongwe Plains',
        'elevation_m': 1050,
        'elevation_range': '1,000 – 1,250 m ASL',
        'rainfall_mm_annual': 920,
        'rainfall_range': '850 – 1,050 mm',
        'soil_type': 'Ferric Luvisols & Sandy Clay Loam',
        'soil_description': 'Deep, well-drained reddish-brown sandy clay loams with moderate-to-high natural fertility. Ideal tilth and root aeration.',
        'temperature_range': '16°C – 28°C',
        'climate_risk': 'Mid-season dry spells (late Jan / early Feb); low frost risk; high solar radiation.',
        'best_crop_mix': ['maize', 'groundnuts', 'soybeans', 'tobacco'],
    },
    'kasungu': {
        'name': 'Kasungu',
        'region': 'Central Region',
        'aez_name': 'Kasungu-Chipata Plains',
        'elevation_m': 1020,
        'elevation_range': '950 – 1,150 m ASL',
        'rainfall_mm_annual': 880,
        'rainfall_range': '800 – 1,000 mm',
        'soil_type': 'Ferric & Haplic Lixisols (Coarse Sandy Loam)',
        'soil_description': 'Weathered, coarse sandy loam topsoils over sandy clay subsoils. Free draining with moderate leaching vulnerability.',
        'temperature_range': '17°C – 29°C',
        'climate_risk': 'Erratic onset of seasonal rains; sandier soils require split nitrogen applications to prevent leaching.',
        'best_crop_mix': ['maize', 'groundnuts', 'tobacco', 'soybeans'],
    },
    'salima': {
        'name': 'Salima',
        'region': 'Central Region',
        'aez_name': 'Lakeshore Lowland & Floodplains',
        'elevation_m': 480,
        'elevation_range': '470 – 600 m ASL',
        'rainfall_mm_annual': 960,
        'rainfall_range': '800 – 1,200 mm',
        'soil_type': 'Eutric Fluvisols & Alluvial Clays',
        'soil_description': 'Rich riverine alluvium, heavy clay dambos, and lacustrine sands. High moisture retention in lowlands.',
        'temperature_range': '22°C – 34°C',
        'climate_risk': 'High temperatures (>32°C) trigger flower abortion in sensitive beans; lowland flash flooding; erratic dry spells.',
        'best_crop_mix': ['rice', 'cassava', 'groundnuts', 'sorghum'],
    },
    'blantyre': {
        'name': 'Blantyre',
        'region': 'Southern Region',
        'aez_name': 'Shire Highlands & Upper Valley',
        'elevation_m': 1120,
        'elevation_range': '900 – 1,350 m ASL',
        'rainfall_mm_annual': 980,
        'rainfall_range': '850 – 1,250 mm',
        'soil_type': 'Orthic Ferralsols & Eutric Nitisols',
        'soil_description': 'Deep red tropical clay loams on undulating terrain. Good moisture holding capacity, susceptible to slope erosion.',
        'temperature_range': '15°C – 27°C',
        'climate_risk': 'Steep slopes require ridge contouring (vetiver grass hedgerows); dry spells in lower valleys.',
        'best_crop_mix': ['maize', 'common-beans', 'groundnuts', 'soybeans'],
    },
}

# Fallback profile for unlisted districts
DEFAULT_DISTRICT_PROFILE: Dict[str, Any] = {
    'name': 'National Benchmark',
    'region': 'Malawi National Average',
    'aez_name': 'Medium Altitude Plateau Zone',
    'elevation_m': 1000,
    'elevation_range': '800 – 1,200 m ASL',
    'rainfall_mm_annual': 900,
    'rainfall_range': '800 – 1,100 mm',
    'soil_type': 'Sandy Clay Loam',
    'soil_description': 'Standard agricultural loam representative of central and southern farming plateaus.',
    'temperature_range': '18°C – 28°C',
    'climate_risk': 'Variable seasonal rainfall with typical mid-season dry spells.',
    'best_crop_mix': ['maize', 'groundnuts', 'soybeans'],
}


# ==============================================================================
# Crop Suitability Matrix per District
# Tiers:
# - 'optimal': Highly Recommended · Premier Agro-Zone (Score 90-100)
# - 'suitable': Suitable with Good Management (Score 70-89)
# - 'marginal': Elevated Agro-Ecological Risk (Score < 70)
# ==============================================================================

CROP_DISTRICT_SUITABILITY: Dict[str, Dict[str, Dict[str, Any]]] = {
    'lilongwe': {
        'maize': {
            'tier': 'optimal',
            'score': 95,
            'label': 'Highly Recommended · Prime Zone',
            'yield_multiplier': Decimal('1.00'),
            'recommended_varieties': 'SC 419, DKC 80-33, MH 30, Pan 53',
            'rationale': 'Central plateau rainfall (920mm) and deep ferric luvisols provide ideal growing degree days and ear-fill conditions.',
            'soil_fit': 'Excellent fit for sandy clay loam.',
            'water_fit': 'Precipitation satisfies full 650–800mm crop water requirement.',
            'badge_color': 'emerald',
        },
        'groundnuts': {
            'tier': 'optimal',
            'score': 98,
            'label': 'Premier Cash Legume · High Soil Match',
            'yield_multiplier': Decimal('1.15'),
            'recommended_varieties': 'CG7, Chalimbana 2005, Nsinjiro (ICGV-SM 90704)',
            'rationale': 'Lilongwe is Malawi\'s premier groundnut production belt. Well-aerated loam soil facilitates peg penetration and suppresses pod rots.',
            'soil_fit': 'Loose, friable sandy loam prevents peg damage during maturation.',
            'water_fit': 'Tolerates mid-season dry spells via taproot architecture.',
            'badge_color': 'emerald',
        },
        'soybeans': {
            'tier': 'optimal',
            'score': 94,
            'label': 'Highly Recommended · Nitrogen Fixing',
            'yield_multiplier': Decimal('1.12'),
            'recommended_varieties': 'Tikolore, Makwacha, Soprano',
            'rationale': 'Optimal night temperatures and rainfall induce prolific rhizobial nodulation, reducing synthetic basal nitrogen requirements.',
            'soil_fit': 'Thrives in fertile loam with pH 5.8–6.8.',
            'water_fit': 'Moisture window fits 100–120 day maturity cycle cleanly.',
            'badge_color': 'emerald',
        },
        'tobacco': {
            'tier': 'optimal',
            'score': 92,
            'label': 'Commercial Export Crop · Auction Hub',
            'yield_multiplier': Decimal('1.10'),
            'recommended_varieties': 'Kutsaga 51 (Burley), KM 10, Banket A1',
            'rationale': 'Direct proximity to Lilongwe Auction Floors minimizes transit loss. Well-drained soils produce premier cured leaf grade.',
            'soil_fit': 'Requires well-drained subsoil to avoid root waterlogging.',
            'water_fit': 'Moderate moisture requirement with dry curing window in March/April.',
            'badge_color': 'emerald',
        },
        'common-beans': {
            'tier': 'suitable',
            'score': 76,
            'label': 'Suitable · Moderate Care Needed',
            'yield_multiplier': Decimal('0.90'),
            'recommended_varieties': 'Kholophethe, Nanyati, BCMV-resistant lines',
            'rationale': 'Performs well under intercropping or residual dambo moisture, but peak plateau heat can cause slight flower drop compared to Dedza highlands.',
            'soil_fit': 'Prefers neutral loam without soil crusting.',
            'water_fit': 'Sensitive to dry spells during pod formation; best planted early.',
            'badge_color': 'amber',
        },
        'cassava': {
            'tier': 'suitable',
            'score': 74,
            'label': 'Suitable · Resilient Food Reserve',
            'yield_multiplier': Decimal('0.85'),
            'recommended_varieties': 'Sauti, Manyokola, TMS 91/023',
            'rationale': 'Exceptional drought insurance. Bulking is somewhat slower on cooler plateau than along the lakeshore, but guarantees staple security.',
            'soil_fit': 'Deep rooting requires minimum 45cm soil depth.',
            'water_fit': 'Highly drought hardy after first 60 days.',
            'badge_color': 'amber',
        },
        'sorghum': {
            'tier': 'marginal',
            'score': 58,
            'label': 'Elevated Agro-Ecological Risk',
            'yield_multiplier': Decimal('0.70'),
            'recommended_varieties': 'Pilira 1, Pilira 2',
            'rationale': 'Lilongwe plateau rainfall (920mm) and high relative humidity create elevated head-mould and fungal risk during grain filling.',
            'soil_fit': 'Acceptable, but legumes yield higher economic return.',
            'water_fit': 'Surplus water relative to crop needs; better suited to Shire Valley.',
            'badge_color': 'rose',
        },
        'rice': {
            'tier': 'marginal',
            'score': 45,
            'label': 'Marginal · Requires Wetland / Irrigation',
            'yield_multiplier': Decimal('0.55'),
            'recommended_varieties': 'Kilombero, Mpatsa, Faya',
            'rationale': 'Rainfed upland plateau rice suffers severe moisture stress without dedicated dambo water table or gravity irrigation canal.',
            'soil_fit': 'Sandy loams fail to retain surface water ponding.',
            'water_fit': 'Deficit: Rice demands >1,200mm flooded water regime.',
            'badge_color': 'rose',
        },
    },

    'kasungu': {
        'maize': {
            'tier': 'optimal',
            'score': 94,
            'label': 'Highly Recommended · Staple Baseline',
            'yield_multiplier': Decimal('1.00'),
            'recommended_varieties': 'DKC 80-33, SC 419, MH 36',
            'rationale': 'Core grain basket of central Malawi. Sandy loam requires timely basal dressing to optimize seedling establishment.',
            'soil_fit': 'Responds strongly to organic matter addition.',
            'water_fit': 'Sufficient in 880mm rainfall belt.',
            'badge_color': 'emerald',
        },
        'tobacco': {
            'tier': 'optimal',
            'score': 97,
            'label': 'Premier Export Heartlands',
            'yield_multiplier': Decimal('1.15'),
            'recommended_varieties': 'Burley 21, Kutsaga 51, KM 10',
            'rationale': 'Kasungu is Malawi\'s historical burley heartland with dedicated agro-dealer support and curing infrastructure.',
            'soil_fit': 'Coarse sandy loam enables optimal root growth and leaf chemistry.',
            'water_fit': 'Matches rainy season timing perfectly.',
            'badge_color': 'emerald',
        },
        'groundnuts': {
            'tier': 'optimal',
            'score': 95,
            'label': 'Highly Recommended · Legume Rotation',
            'yield_multiplier': Decimal('1.10'),
            'recommended_varieties': 'CG7, Nsinjiro, Chitala',
            'rationale': 'Excellent soil compatibility. Sandy loam soil makes harvesting and lifting effortless with minimal pod losses.',
            'soil_fit': 'Ideal loose texture for lifting.',
            'water_fit': 'Taproots utilize deep subsoil moisture.',
            'badge_color': 'emerald',
        },
        'soybeans': {
            'tier': 'optimal',
            'score': 91,
            'label': 'Highly Recommended · Commercial Demand',
            'yield_multiplier': Decimal('1.10'),
            'recommended_varieties': 'Tikolore, Makwacha',
            'rationale': 'High demand from regional oil-crushers and poultry feed mills in central region.',
            'soil_fit': 'Good nodulation in warm soils.',
            'water_fit': '105-day cycle safely finishes before March rain cessation.',
            'badge_color': 'emerald',
        },
        'cassava': {
            'tier': 'suitable',
            'score': 78,
            'label': 'Suitable · Drought Buffer',
            'yield_multiplier': Decimal('0.90'),
            'recommended_varieties': 'Sauti, Silira',
            'rationale': 'Resilient staple buffer on sandier ridge plots vulnerable to moisture loss.',
            'soil_fit': 'Grows well in loose sandy loam.',
            'water_fit': 'Highly tolerant to dry spells.',
            'badge_color': 'amber',
        },
        'common-beans': {
            'tier': 'suitable',
            'score': 72,
            'label': 'Suitable · Early Season Crop',
            'yield_multiplier': Decimal('0.85'),
            'recommended_varieties': 'Kholophethe, Maluwa',
            'rationale': 'Plant during early rains to avoid late-season high temperatures.',
            'soil_fit': 'Requires fertilizer microdosing on lighter soils.',
            'water_fit': 'Ensure adequate moisture during flowering.',
            'badge_color': 'amber',
        },
        'sorghum': {
            'tier': 'marginal',
            'score': 62,
            'label': 'Elevated Agro-Ecological Risk',
            'yield_multiplier': Decimal('0.75'),
            'recommended_varieties': 'Pilira 1',
            'rationale': 'Lower gross margin than maize and legumes; grain mould risk if late rains persist.',
            'soil_fit': 'Tolerant, but economically sub-optimal.',
            'water_fit': 'Can be grown defensively if severe drought forecasted.',
            'badge_color': 'rose',
        },
        'rice': {
            'tier': 'marginal',
            'score': 42,
            'label': 'Marginal · Low Water Table',
            'yield_multiplier': Decimal('0.50'),
            'recommended_varieties': 'Kilombero',
            'rationale': 'Free-draining sandy loam plains cause rapid percolation; impossible without bunded irrigation.',
            'soil_fit': 'Excessive percolation.',
            'water_fit': 'Severely deficient for rainfed paddy.',
            'badge_color': 'rose',
        },
    },

    'salima': {
        'rice': {
            'tier': 'optimal',
            'score': 98,
            'label': 'Premier Production Belt · Alluvial Soils',
            'yield_multiplier': Decimal('1.25'),
            'recommended_varieties': 'Kilombero, Faya, Mpatsa',
            'rationale': 'Salima lakeshore alluvium and high heat index create Malawi\'s premier rice growing conditions with aromatic premium value.',
            'soil_fit': 'Heavy alluvial silt-clays hold standing water effectively.',
            'water_fit': 'High seasonal rainfall combined with lake drainage channels.',
            'badge_color': 'emerald',
        },
        'cassava': {
            'tier': 'optimal',
            'score': 96,
            'label': 'Highly Recommended · High Thermal Units',
            'yield_multiplier': Decimal('1.20'),
            'recommended_varieties': 'Manyokola, Sauti, Mkondezi',
            'rationale': 'High lakeshore temperatures accelerate tuber bulking; major primary staple and commercial starch cash-crop.',
            'soil_fit': 'Excellent on sandy lacustrine soils and alluvial banks.',
            'water_fit': 'Withstands heat and erratic lake rainfall.',
            'badge_color': 'emerald',
        },
        'sorghum': {
            'tier': 'optimal',
            'score': 91,
            'label': 'Highly Recommended · Heat & Drought Hardy',
            'yield_multiplier': Decimal('1.15'),
            'recommended_varieties': 'Pilira 1, Pilira 2',
            'rationale': 'Thrives in high temperatures (>30°C) where maize tassels scorch. Highly resistant to lowland heat stress.',
            'soil_fit': 'Adapted to marginal and heavy clay vertisols.',
            'water_fit': 'Requires only 400–550mm seasonal precipitation.',
            'badge_color': 'emerald',
        },
        'groundnuts': {
            'tier': 'suitable',
            'score': 84,
            'label': 'Suitable · Select Well-Drained Sites',
            'yield_multiplier': Decimal('0.95'),
            'recommended_varieties': 'Chitala (bred for lakeshore), CG7',
            'rationale': 'Performs well on lighter alluvial soils; avoid heavy lowlands prone to seasonal waterlogging.',
            'soil_fit': 'Must avoid waterlogged clays to prevent pod rot.',
            'water_fit': 'Good performance if planted on raised ridges.',
            'badge_color': 'amber',
        },
        'maize': {
            'tier': 'suitable',
            'score': 75,
            'label': 'Suitable with Drought Risk',
            'yield_multiplier': Decimal('0.85'),
            'recommended_varieties': 'SC 419, DKC 80-33, Drought-Tolerant OPVs',
            'rationale': 'Lowland heat spikes (>33°C) during January can desiccate maize pollen. Requires drought-tolerant seed genetics.',
            'soil_fit': 'Suitable on fertile alluvium.',
            'water_fit': 'Vulnerable to mid-season heat waves and dry spells.',
            'badge_color': 'amber',
        },
        'soybeans': {
            'tier': 'marginal',
            'score': 62,
            'label': 'Elevated Heat Stress Risk',
            'yield_multiplier': Decimal('0.75'),
            'recommended_varieties': 'Tikolore',
            'rationale': 'Excessive tropical heat accelerates senescence and inhibits pod filling; yields trail central plateau benchmarks.',
            'soil_fit': 'Acceptable, but vegetative cycle shortened by heat.',
            'water_fit': 'Sensitive to dry spells during pod expansion.',
            'badge_color': 'rose',
        },
        'tobacco': {
            'tier': 'marginal',
            'score': 55,
            'label': 'Sub-Optimal Agro-Zone',
            'yield_multiplier': Decimal('0.65'),
            'recommended_varieties': 'Burley lines',
            'rationale': 'High relative humidity and warm nights interfere with proper leaf curing; distance to auction adds transport penalty.',
            'soil_fit': 'Heavy alluvial clay produces coarse, thick, low-grade leaf.',
            'water_fit': 'Excessive atmospheric humidity.',
            'badge_color': 'rose',
        },
        'common-beans': {
            'tier': 'marginal',
            'score': 45,
            'label': 'Severe Heat Abortion Risk',
            'yield_multiplier': Decimal('0.55'),
            'recommended_varieties': 'Kholophethe',
            'rationale': 'Common beans suffer severe flower and pod abortion when temperatures exceed 30°C. Only viable as winter residual crop.',
            'soil_fit': 'Poor heat adaptation.',
            'water_fit': 'Fails in lowland summer conditions.',
            'badge_color': 'rose',
        },
    },

    'blantyre': {
        'maize': {
            'tier': 'optimal',
            'score': 95,
            'label': 'Highly Recommended · Staple Grain',
            'yield_multiplier': Decimal('1.00'),
            'recommended_varieties': 'SC 419, DKC 80-33, MH 36',
            'rationale': 'Shire Highlands rainfall (980mm) provides reliable moisture. Requires contour ridge farming on sloping topography.',
            'soil_fit': 'Deep red ferralsols provide sturdy root anchorage.',
            'water_fit': 'Excellent match for 980mm annual precipitation.',
            'badge_color': 'emerald',
        },
        'common-beans': {
            'tier': 'optimal',
            'score': 96,
            'label': 'Premier Highland Legume · High Price',
            'yield_multiplier': Decimal('1.15'),
            'recommended_varieties': 'Kholophethe, Nanyati, Maluwa',
            'rationale': 'Cool highland night temperatures prevent rust and flower abortion. High consumer demand in Blantyre urban markets.',
            'soil_fit': 'Thrives in well-structured red loam soils.',
            'water_fit': 'Sufficient mist and rainfall during pod fill.',
            'badge_color': 'emerald',
        },
        'groundnuts': {
            'tier': 'optimal',
            'score': 92,
            'label': 'Highly Recommended · Cash Legume',
            'yield_multiplier': Decimal('1.05'),
            'recommended_varieties': 'CG7, Nsinjiro, Manipintar',
            'rationale': 'Good yield response and rapid market disposal in southern trading hubs.',
            'soil_fit': 'Requires well-made ridges on clay soils.',
            'water_fit': 'Tolerates typical highland rain patterns.',
            'badge_color': 'emerald',
        },
        'soybeans': {
            'tier': 'optimal',
            'score': 91,
            'label': 'Highly Recommended · Agro-Industrial Demand',
            'yield_multiplier': Decimal('1.05'),
            'recommended_varieties': 'Tikolore, Makwacha',
            'rationale': 'Immediate proximity to commercial oil seed refiners and feed millers in Limbe/Blantyre industrial area.',
            'soil_fit': 'Good nodulation in acidic-to-neutral ferralsols.',
            'water_fit': 'Fits rainy season comfortably.',
            'badge_color': 'emerald',
        },
        'cassava': {
            'tier': 'suitable',
            'score': 82,
            'label': 'Suitable · Soil Conservation Buffer',
            'yield_multiplier': Decimal('0.95'),
            'recommended_varieties': 'Sauti, Manyokola',
            'rationale': 'Provides excellent soil cover against slope erosion; resilient dry season survival food.',
            'soil_fit': 'Deep clay subsoils allow deep root storage.',
            'water_fit': 'Survives erratic rains.',
            'badge_color': 'amber',
        },
        'tobacco': {
            'tier': 'suitable',
            'score': 80,
            'label': 'Suitable · Local Auction Floors',
            'yield_multiplier': Decimal('0.90'),
            'recommended_varieties': 'Burley lines',
            'rationale': 'Serviced by Limbe Auction Floors. Smaller average plot sizes in southern region limit total hectare allocations.',
            'soil_fit': 'Good, but land competition with food crops is intense.',
            'water_fit': 'Adequate rainfall.',
            'badge_color': 'amber',
        },
        'sorghum': {
            'tier': 'marginal',
            'score': 65,
            'label': 'Elevated Agro-Ecological Risk',
            'yield_multiplier': Decimal('0.75'),
            'recommended_varieties': 'Pilira 1',
            'rationale': 'High rainfall and cooler highland mist elevate grain mould risk. Legumes generate far higher gross margin per hectare.',
            'soil_fit': 'Acceptable, but economically uncompetitive.',
            'water_fit': 'Excessive moisture for dryland sorghum.',
            'badge_color': 'rose',
        },
        'rice': {
            'tier': 'marginal',
            'score': 48,
            'label': 'Marginal · Sloping Terrain',
            'yield_multiplier': Decimal('0.60'),
            'recommended_varieties': 'Kilombero',
            'rationale': 'Highland terrain does not retain floodwaters without complex bench terracing. Better suited to lower Shire or Machinga dambos.',
            'soil_fit': 'Sloping soils cannot support paddy ponding.',
            'water_fit': 'Deficient water retention.',
            'badge_color': 'rose',
        },
    },
}


# ==============================================================================
# Helper API Functions
# ==============================================================================

def resolve_district_slug(farm=None, override_slug: Optional[str] = None) -> str:
    """
    Safely resolves the district slug for a farm or request.
    Priority:
    1. Explicit override_slug (if valid)
    2. Farm location_description parsing (e.g. "Lilongwe District")
    3. Farm latitude/longitude proximity
    4. Fallback default: 'lilongwe'
    """
    if override_slug and override_slug.lower() in DISTRICT_AGRO_PROFILES:
        return override_slug.lower()

    if farm:
        # Check location_description
        loc = (farm.location_description or '').lower()
        for key in DISTRICT_AGRO_PROFILES:
            if key in loc:
                return key

        # Coordinates proximity heuristic
        if farm.latitude and farm.longitude:
            lat = float(farm.latitude)
            lng = float(farm.longitude)
            # Salima lakeshore: roughly lat -13.5 to -14.0, lng > 34.1
            if lng > 34.1 and -14.5 <= lat <= -13.2:
                return 'salima'
            # Blantyre / South: lat < -15.0
            if lat < -15.0:
                return 'blantyre'
            # Kasungu: lat > -13.4 and lng < 33.8
            if lat > -13.4 and lng < 33.8:
                return 'kasungu'

    return 'lilongwe'


def get_district_profile(district_slug: str) -> Dict[str, Any]:
    """Returns the full agro-ecological profile for a district."""
    slug = district_slug.lower() if district_slug else 'lilongwe'
    return DISTRICT_AGRO_PROFILES.get(slug, DEFAULT_DISTRICT_PROFILE)


def get_crop_suitability(crop_slug: str, district_slug: str) -> Dict[str, Any]:
    """
    Returns the agro-ecological suitability specification for a given crop and district.
    """
    slug = district_slug.lower() if district_slug else 'lilongwe'
    district_matrix = CROP_DISTRICT_SUITABILITY.get(slug, CROP_DISTRICT_SUITABILITY.get('lilongwe', {}))

    if crop_slug in district_matrix:
        return district_matrix[crop_slug]

    # Sensible baseline fallback
    return {
        'tier': 'suitable',
        'score': 75,
        'label': 'Suitable with Good Management',
        'yield_multiplier': Decimal('1.00'),
        'recommended_varieties': 'Certified DARS Seed',
        'rationale': 'Standard agro-ecological performance across typical Malawian plateau soils.',
        'soil_fit': 'Standard agricultural loam compatibility.',
        'water_fit': 'Normal seasonal rainfall adaptation.',
        'badge_color': 'leaf',
    }


def get_recommended_crop_slugs(district_slug: str, limit: int = 3) -> List[str]:
    """
    Returns the top recommended crop slugs for a district in order of optimal suitability.
    """
    profile = get_district_profile(district_slug)
    mix = profile.get('best_crop_mix', ['maize', 'groundnuts', 'soybeans'])
    return mix[:limit]


def calculate_regional_fit_score(allocated_crops: List[Dict[str, Any]], district_slug: str) -> Dict[str, Any]:
    """
    Calculates an aggregate Agro-Ecological Regional Fit Score (0-100)
    based on the land-weighted suitability scores of the allocated crops.
    """
    total_area = sum(float(c.get('area_ha', 0.0)) for c in allocated_crops)
    if total_area <= 0:
        return {'score': 85, 'verdict': 'Balanced Regional Portfolio', 'warnings': []}

    weighted_score = 0.0
    warnings = []

    for item in allocated_crops:
        slug = item.get('slug')
        area = float(item.get('area_ha', 0.0))
        suit = get_crop_suitability(slug, district_slug)
        weighted_score += suit['score'] * (area / total_area)

        if suit['tier'] == 'marginal' and area > 0:
            warnings.append(
                f"{item.get('name', slug).title()} ({area:.2f} ha) has elevated agro-ecological risk in {district_slug.title()}: {suit['rationale']}"
            )

    score_int = int(round(weighted_score))
    if score_int >= 90:
        verdict = 'Optimal Agro-Ecological Alignment'
    elif score_int >= 75:
        verdict = 'Good Regional Adaptation'
    else:
        verdict = 'Sub-Optimal Agro-Zone Match'

    return {
        'score': score_int,
        'verdict': verdict,
        'warnings': warnings,
    }
