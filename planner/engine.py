import statistics
from decimal import Decimal
from typing import Dict, Any, List

from farms.models import Crop, Farm, Planting
from market.models import CropPrice, InputCost


DEFAULT_BENCHMARKS = {
    'maize': {'yield_ha': Decimal('2200.0'), 'cost_ha': Decimal('480000.0'), 'price_kg': Decimal('400.0')},
    'groundnuts': {'yield_ha': Decimal('1100.0'), 'cost_ha': Decimal('380000.0'), 'price_kg': Decimal('970.0')},
    'soybeans': {'yield_ha': Decimal('1000.0'), 'cost_ha': Decimal('280000.0'), 'price_kg': Decimal('730.0')},
    'common-beans': {'yield_ha': Decimal('850.0'), 'cost_ha': Decimal('320000.0'), 'price_kg': Decimal('1380.0')},
    'cassava': {'yield_ha': Decimal('7500.0'), 'cost_ha': Decimal('220000.0'), 'price_kg': Decimal('290.0')},
    'rice': {'yield_ha': Decimal('2600.0'), 'cost_ha': Decimal('520000.0'), 'price_kg': Decimal('1250.0')},
    'sorghum': {'yield_ha': Decimal('1200.0'), 'cost_ha': Decimal('200000.0'), 'price_kg': Decimal('420.0')},
    'tobacco': {'yield_ha': Decimal('1400.0'), 'cost_ha': Decimal('740000.0'), 'price_kg': Decimal('2750.0')},
}


def get_crop_benchmarks(crop: Crop, farm: Farm = None) -> Dict[str, Any]:
    """
    Retrieves or derives authoritative baseline benchmarks for a crop:
    - Yield per ha (uses farmer's past actuals if available, else standard agro-ecological baseline)
    - Production cost per ha (from itemized InputCost records)
    - Expected selling price per kg (from latest Farmgate CropPrice)
    """
    slug = crop.slug
    defaults = DEFAULT_BENCHMARKS.get(slug, {
        'yield_ha': Decimal('1500.0'),
        'cost_ha': Decimal('350000.0'),
        'price_kg': Decimal('500.0'),
    })

    # 1. Historical Farm Yield (if farmer has logged plantings for this crop)
    yield_source = "National Agro-Ecological Benchmark"
    yield_kg_ha = defaults['yield_ha']
    if farm:
        past_plantings = list(Planting.objects.filter(
            season__farm=farm, crop=crop, yield_kg__isnull=False, area_ha__gt=0
        ))
        if past_plantings:
            past_yields = [float(p.yield_kg / p.area_ha) for p in past_plantings if p.area_ha > 0]
            if past_yields:
                yield_kg_ha = Decimal(str(round(statistics.mean(past_yields), 1)))
                yield_source = f"Farm History ({len(past_plantings)} observed harvest(s))"

    # 2. Cost per Hectare (from InputCost model)
    cost_source = "AISAM / Agro-Dealer Baseline Benchmark 2024"
    cost_ha = defaults['cost_ha']
    db_inputs = list(InputCost.objects.filter(crop=crop))
    if db_inputs:
        total_db_cost = sum(i.cost_per_ha_mwk for i in db_inputs)
        if total_db_cost > 0:
            cost_ha = total_db_cost
            cost_source = "Itemized Regional Input Survey (Seed, Fertilizer, Labour)"

    # 3. Selling Price per kg (from CropPrice model)
    price_source = "AMIS Malawi Market Benchmark 2024"
    price_kg = defaults['price_kg']
    latest_price = CropPrice.objects.filter(crop=crop, price_farmgate_mwk__isnull=False).order_by('-year', '-month').first()
    if latest_price and latest_price.price_farmgate_mwk:
        price_kg = latest_price.price_farmgate_mwk
        price_source = f"AMIS Farmgate Surveillance ({latest_price.year}-{latest_price.month:02d})"

    # 4. Break-Even Price per kg = Cost per ha / Yield per ha
    break_even_price = cost_ha / yield_kg_ha if yield_kg_ha > 0 else Decimal('0.00')

    return {
        'crop': crop,
        'yield_kg_ha': yield_kg_ha,
        'yield_source': yield_source,
        'cost_ha_mwk': cost_ha,
        'cost_source': cost_source,
        'price_kg_mwk': price_kg,
        'price_source': price_source,
        'break_even_price_mwk': round(break_even_price, 2),
    }


def calculate_plan_allocations(
    farm: Farm,
    total_land_ha: Decimal,
    seasonal_budget_mwk: Decimal = None,
    available_labour: int = None,
    selected_crops: List[Crop] = None,
) -> Dict[str, Any]:
    """
    Pure-Python calculation engine that generates 3 alternative planning strategies:
    1. 'balanced': Balanced Portfolio (diversification, food + commercial balance)
    2. 'return_focused': Return-Focused Strategy (prioritizes high-margin cash crops)
    3. 'risk_conscious': Risk-Conscious Strategy (prioritizes food staple security & lower inputs)

    Honest trade-offs are articulated for each option.
    """
    if not selected_crops:
        selected_crops = list(farm.preferred_crops.all())
    if not selected_crops:
        # Fallback to Maize + Groundnuts as standard Malawi mix
        selected_crops = list(Crop.objects.filter(slug__in=['maize', 'groundnuts']))
        if not selected_crops:
            selected_crops = list(Crop.objects.all()[:2])

    benchmarks = {c.slug: get_crop_benchmarks(c, farm) for c in selected_crops}

    # Identify primary staple (Maize or Cassava or first crop)
    staple_crop = next((c for c in selected_crops if c.slug in ['maize', 'cassava', 'sorghum']), selected_crops[0])
    cash_crops = [c for c in selected_crops if c.slug != staple_crop.slug]
    if not cash_crops:
        cash_crops = [staple_crop]

    strategies_specs = [
        {
            'type': 'balanced',
            'title': 'Balanced Strategy',
            'tagline': 'Optimal trade-off between household food security and commercial cashflow.',
            'tradeoff_label': 'Moderate Risk / Balanced Return',
            'tradeoff_description': 'Allocates ~50% to staple maize and divides the remaining land across nitrogen-fixing legumes, reducing fertilizer vulnerability while creating market surplus.',
            'badge_class': 'fp-badge-low',
            'staple_share': Decimal('0.55') if cash_crops != [staple_crop] else Decimal('1.00'),
        },
        {
            'type': 'return_focused',
            'title': 'Return-Focused Strategy',
            'tagline': 'Maximizes expected net gross margin per hectare through cash crop allocation.',
            'tradeoff_label': 'Higher Commercial Return / Capital Intensive',
            'tradeoff_description': 'Shifts land into high-value legumes or cash crops. Demands higher upfront working capital and increases exposure to wholesale market price volatility.',
            'badge_class': 'fp-badge-medium',
            'staple_share': Decimal('0.35') if cash_crops != [staple_crop] else Decimal('1.00'),
        },
        {
            'type': 'risk_conscious',
            'title': 'Risk-Conscious Strategy',
            'tagline': 'Prioritizes household calorie security, drought tolerance, and lower cash expenditure.',
            'tradeoff_label': 'Defensive / Low Input Risk',
            'tradeoff_description': 'Secures a 12-month family grain reserve first. Requires significantly lower input capital, insulating the farm against mid-season dry spells and cash crunches.',
            'badge_class': 'fp-badge-water',
            'staple_share': Decimal('0.70') if cash_crops != [staple_crop] else Decimal('1.00'),
        },
    ]

    generated_plans = []

    for spec in strategies_specs:
        staple_area = round(total_land_ha * spec['staple_share'], 2)
        remaining_land = total_land_ha - staple_area

        # Distribute remaining land equally among cash crops
        cash_crop_count = len(cash_crops) if cash_crops != [staple_crop] else 0
        cash_area_per_crop = round(remaining_land / cash_crop_count, 2) if cash_crop_count > 0 else Decimal('0.00')

        plan_items = []
        total_plan_cost = Decimal('0.00')
        total_plan_revenue = Decimal('0.00')
        assumptions = []

        # 1. Staple Allocation
        st_bm = benchmarks[staple_crop.slug]
        st_cost = staple_area * st_bm['cost_ha_mwk']
        st_yield_total = staple_area * st_bm['yield_kg_ha']
        st_rev = st_yield_total * st_bm['price_kg_mwk']
        st_margin = st_rev - st_cost
        st_break_even = st_cost / st_yield_total if st_yield_total > 0 else Decimal('0.00')

        total_plan_cost += st_cost
        total_plan_revenue += st_rev

        plan_items.append({
            'crop': staple_crop,
            'area_ha': staple_area,
            'yield_kg_ha': st_bm['yield_kg_ha'],
            'yield_total_kg': round(st_yield_total, 1),
            'cost_ha_mwk': round(st_bm['cost_ha_mwk'], 2),
            'total_cost_mwk': round(st_cost, 2),
            'price_kg_mwk': round(st_bm['price_kg_mwk'], 2),
            'revenue_mwk': round(st_rev, 2),
            'gross_margin_mwk': round(st_margin, 2),
            'break_even_price_mwk': round(st_break_even, 2),
            'is_staple': True,
        })

        assumptions.append({
            'category': 'price',
            'name': f"{staple_crop.name} Selling Price",
            'value': f"MWK {st_bm['price_kg_mwk']:,.0f}/kg",
            'source': st_bm['price_source'],
        })
        assumptions.append({
            'category': 'yield',
            'name': f"{staple_crop.name} Expected Yield",
            'value': f"{st_bm['yield_kg_ha']:,.0f} kg/ha",
            'source': st_bm['yield_source'],
        })
        assumptions.append({
            'category': 'cost',
            'name': f"{staple_crop.name} Cost / ha",
            'value': f"MWK {st_bm['cost_ha_mwk']:,.0f}/ha",
            'source': st_bm['cost_source'],
        })

        # 2. Cash Crops Allocation
        if cash_crops != [staple_crop]:
            for c in cash_crops:
                c_bm = benchmarks[c.slug]
                c_cost = cash_area_per_crop * c_bm['cost_ha_mwk']
                c_yield_total = cash_area_per_crop * c_bm['yield_kg_ha']
                c_rev = c_yield_total * c_bm['price_kg_mwk']
                c_margin = c_rev - c_cost
                c_break_even = c_cost / c_yield_total if c_yield_total > 0 else Decimal('0.00')

                total_plan_cost += c_cost
                total_plan_revenue += c_rev

                plan_items.append({
                    'crop': c,
                    'area_ha': cash_area_per_crop,
                    'yield_kg_ha': c_bm['yield_kg_ha'],
                    'yield_total_kg': round(c_yield_total, 1),
                    'cost_ha_mwk': round(c_bm['cost_ha_mwk'], 2),
                    'total_cost_mwk': round(c_cost, 2),
                    'price_kg_mwk': round(c_bm['price_kg_mwk'], 2),
                    'revenue_mwk': round(c_rev, 2),
                    'gross_margin_mwk': round(c_margin, 2),
                    'break_even_price_mwk': round(c_break_even, 2),
                    'is_staple': False,
                })

                assumptions.append({
                    'category': 'price',
                    'name': f"{c.name} Selling Price",
                    'value': f"MWK {c_bm['price_kg_mwk']:,.0f}/kg",
                    'source': c_bm['price_source'],
                })
                assumptions.append({
                    'category': 'cost',
                    'name': f"{c.name} Cost / ha",
                    'value': f"MWK {c_bm['cost_ha_mwk']:,.0f}/ha",
                    'source': c_bm['cost_source'],
                })

        total_margin = total_plan_revenue - total_plan_cost

        # Budget Check
        budget_warning = None
        if seasonal_budget_mwk is not None and total_plan_cost > seasonal_budget_mwk:
            deficit = total_plan_cost - seasonal_budget_mwk
            budget_warning = f"Required capital exceeds available seasonal budget by MWK {deficit:,.0f}."

        generated_plans.append({
            'strategy_type': spec['type'],
            'title': spec['title'],
            'tagline': spec['tagline'],
            'tradeoff_label': spec['tradeoff_label'],
            'tradeoff_description': spec['tradeoff_description'],
            'badge_class': spec['badge_class'],
            'total_land_ha': total_land_ha,
            'total_cost_mwk': round(total_plan_cost, 2),
            'total_revenue_mwk': round(total_plan_revenue, 2),
            'total_margin_mwk': round(total_margin, 2),
            'budget_warning': budget_warning,
            'items': plan_items,
            'assumptions': assumptions,
        })

    return {
        'plans': generated_plans,
        'farm': farm,
        'total_land_ha': total_land_ha,
        'seasonal_budget_mwk': seasonal_budget_mwk,
        'available_labour': available_labour,
        'selected_crops': selected_crops,
    }


def simulate_game_shocks(
    baseline_plan: Dict[str, Any],
    rainfall_delta_pct: float = 0.0,
    temp_delta_c: float = 0.0,
    price_delta_pct: float = 0.0,
    input_cost_delta_pct: float = 0.0,
) -> Dict[str, Any]:
    """
    Game Engine Simulation:
    Applies real-time climate, market, and agronomic shocks to a crop plan.
    Calculates Resilience Score (Health Bar 0-100), Profit/Loss Coin Meter,
    Food Security coverage, and Season Performance Grade (A+ to F).
    """
    sim_items = []
    total_sim_cost = Decimal('0.00')
    total_sim_rev = Decimal('0.00')

    # Agronomic response curves:
    # - Rainfall: Maize is highly sensitive (-1.2x elasticity on deficit); Legumes moderately sensitive (-0.8x)
    # - Temperature: antesis heat stress penalty if temp_delta > 1.5°C
    heat_penalty = max(0.0, (temp_delta_c - 1.2) * 0.08)  # up to 16% yield drop if +3.0°C

    for item in baseline_plan['items']:
        crop_slug = item['crop'].slug

        # 1. Yield Shock
        if rainfall_delta_pct < 0:
            rain_elasticity = 1.25 if crop_slug == 'maize' else (0.75 if crop_slug in ['groundnuts', 'soybeans'] else 0.4)
            yield_multiplier = 1.0 + ((rainfall_delta_pct / 100.0) * rain_elasticity) - heat_penalty
        else:
            # Positive rain has diminishing returns
            yield_multiplier = 1.0 + min(0.20, (rainfall_delta_pct / 100.0) * 0.5) - heat_penalty

        yield_multiplier = max(0.25, yield_multiplier)  # crop doesn't drop below 25% minimum salvage
        sim_yield_ha = Decimal(str(round(float(item['yield_kg_ha']) * yield_multiplier, 1)))
        sim_yield_total = Decimal(str(round(float(item['area_ha']) * float(sim_yield_ha), 1)))

        # 2. Cost Shock (Input and fertilizer price adjustments)
        cost_multiplier = max(0.6, 1.0 + (input_cost_delta_pct / 100.0))
        sim_total_cost = Decimal(str(round(float(item['total_cost_mwk']) * cost_multiplier, 2)))

        # 3. Market Price Shock
        # If national drought occurs (rainfall_delta < -15%), staple grain prices naturally spike (+15-25%)
        market_drought_spike = 0.18 if (rainfall_delta_pct <= -20 and crop_slug == 'maize') else 0.0
        effective_price_change = (price_delta_pct / 100.0) + market_drought_spike
        price_multiplier = max(0.4, 1.0 + effective_price_change)

        sim_price_kg = Decimal(str(round(float(item['price_kg_mwk']) * price_multiplier, 2)))
        sim_rev = Decimal(str(round(float(sim_yield_total) * float(sim_price_kg), 2)))
        sim_margin = sim_rev - sim_total_cost

        # New break-even point under shock
        sim_break_even = sim_total_cost / sim_yield_total if sim_yield_total > 0 else Decimal('0.00')

        total_sim_cost += sim_total_cost
        total_sim_rev += sim_rev

        sim_items.append({
            'crop_name': item['crop'].name,
            'crop_slug': crop_slug,
            'area_ha': float(item['area_ha']),
            'orig_margin': float(item['gross_margin_mwk']),
            'sim_yield_total_kg': float(sim_yield_total),
            'sim_total_cost_mwk': float(sim_total_cost),
            'sim_revenue_mwk': float(sim_rev),
            'sim_margin_mwk': float(sim_margin),
            'margin_delta_mwk': float(sim_margin - item['gross_margin_mwk']),
            'sim_break_even_mwk': float(round(sim_break_even, 2)),
            'status': 'Thriving' if sim_margin > 0 else 'Loss-Making',
        })

    total_sim_margin = total_sim_rev - total_sim_cost
    orig_total_margin = Decimal(str(baseline_plan['total_margin_mwk']))
    delta_margin = total_sim_margin - orig_total_margin

    # 4. Game Mechanics: Resilience Score & Grade
    # Resilience starts at 75, adjusted by profit retention and food security
    ratio = float(total_sim_margin / orig_total_margin) if orig_total_margin > 0 else 0.5
    resilience_score = int(max(5, min(100, round(50 + (ratio * 40)))))

    if resilience_score >= 85 and total_sim_margin > 0:
        grade = 'A+'
        health_status = 'Thriving & Resilient'
        health_color = 'bg-leaf'
    elif resilience_score >= 70 and total_sim_margin > 0:
        grade = 'A'
        health_status = 'Solid Harvest'
        health_color = 'bg-leaf'
    elif resilience_score >= 50:
        grade = 'B'
        health_status = 'Weather Strained'
        health_color = 'bg-risk-medium'
    elif resilience_score >= 30:
        grade = 'C'
        health_status = 'Vulnerable'
        health_color = 'bg-risk-high'
    else:
        grade = 'F'
        health_status = 'Severe Crop Failure'
        health_color = 'bg-risk-high'

    # Food Security calculation (Family requirement: ~1,200 kg maize for family of 5)
    maize_harvested = next((item['sim_yield_total_kg'] for item in sim_items if item['crop_slug'] == 'maize'), 0.0)
    food_security_pct = min(100, int(round((maize_harvested / 1200.0) * 100))) if maize_harvested else 100

    # Game Commentary reaction
    if delta_margin >= 0:
        commentary = "Superb outcome! Favourable conditions boosted your harvest and market margins."
    elif total_sim_margin > 0:
        commentary = "Weather shock absorbed! While profits softened, your crop diversification kept farm cashflow in the green."
    else:
        commentary = "Alert: Under this extreme shock, farm production costs exceed harvest sales. Consider adjusting crop allocations or adding irrigation."

    return {
        'sim_items': sim_items,
        'total_sim_cost': float(total_sim_cost),
        'total_sim_rev': float(total_sim_rev),
        'total_sim_margin': float(total_sim_margin),
        'delta_margin': float(delta_margin),
        'resilience_score': resilience_score,
        'grade': grade,
        'health_status': health_status,
        'health_color': health_color,
        'food_security_pct': food_security_pct,
        'commentary': commentary,
        'shocks_applied': {
            'rainfall_delta_pct': rainfall_delta_pct,
            'temp_delta_c': temp_delta_c,
            'price_delta_pct': price_delta_pct,
            'input_cost_delta_pct': input_cost_delta_pct,
        }
    }
