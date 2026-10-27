import statistics
from decimal import Decimal
from typing import Dict, Any, List


def calculate_climate_risks(district, records=None) -> Dict[str, Any]:
    """
    Computes objective climate risk indicators for a district based on historical climate records:
    - Rainfall Variability & Drought Risk
    - Mid-Season Dry Spell Hazard
    - Heat Wave & Extreme Temperature Stress
    - Overall Composite Risk Assessment

    STRICT BRIEF RULE: Must output 'Insufficient Data' (never a fake 'Low')
    when record history is inadequate.
    """
    if records is None:
        records = list(district.climate_records.filter(record_type='historical').order_by('year', 'month'))
    else:
        records = list(records)

    total_months = len(records)
    distinct_years = sorted(list({r.year for r in records}))
    years_count = len(distinct_years)

    # --------------------------------------------------------------------------
    # 1. Rainfall & Drought Risk
    # --------------------------------------------------------------------------
    # Group rainfall by hydrologic growing season: Nov(Y-1) to Apr(Y)
    seasonal_totals: List[float] = []
    rainfall_records_count = sum(1 for r in records if r.rainfall_mm is not None)

    # We require at least 3 distinct growing seasons (>= 18 rainy months)
    rainy_months = [r for r in records if r.month in [11, 12, 1, 2, 3, 4] and r.rainfall_mm is not None]

    if len(rainy_months) < 18 or years_count < 3:
        rainfall_risk = {
            'level': 'Insufficient Data',
            'score': None,
            'badge_class': 'fp-badge-medium',
            'mean_seasonal_mm': None,
            'cv_pct': None,
            'deficit_frequency_pct': None,
            'explanation': f"Only {len(rainy_months)} rainy season months recorded. Minimum 3 complete seasons (18 months) required for statistical drought assessment.",
            'is_insufficient': True,
        }
    else:
        # Calculate rainfall for each full year
        annual_map = {}
        for r in records:
            if r.rainfall_mm is not None:
                annual_map[r.year] = annual_map.get(r.year, 0.0) + float(r.rainfall_mm)

        annual_values = [v for v in annual_map.values() if v > 100]  # valid years
        if len(annual_values) >= 3:
            mean_rain = statistics.mean(annual_values)
            stdev_rain = statistics.stdev(annual_values) if len(annual_values) > 1 else 0.0
            cv = (stdev_rain / mean_rain) if mean_rain > 0 else 0.0
            cv_pct = round(cv * 100, 1)

            # Frequency of severe deficit years (< 70% of mean)
            deficit_years = sum(1 for v in annual_values if v < (mean_rain * 0.75))
            deficit_pct = round((deficit_years / len(annual_values)) * 100, 1)

            if cv >= 0.28 or deficit_pct >= 25 or mean_rain < 680:
                rf_level = 'High'
                rf_class = 'fp-badge-high'
                rf_score = 78
                rf_exp = f"High inter-annual variability (CV {cv_pct}%). Severe rainfall deficit occurs in {deficit_pct}% of recorded seasons."
            elif cv >= 0.18 or deficit_pct >= 12 or mean_rain < 820:
                rf_level = 'Medium'
                rf_class = 'fp-badge-medium'
                rf_score = 48
                rf_exp = f"Moderate rainfall variability (CV {cv_pct}%) with occasional mid-season deficits. Average annual total is {mean_rain:.0f} mm."
            else:
                rf_level = 'Low'
                rf_class = 'fp-badge-low'
                rf_score = 22
                rf_exp = f"Reliable precipitation baseline (CV {cv_pct}%). Historical average is {mean_rain:.0f} mm with low drought recurrence."

            rainfall_risk = {
                'level': rf_level,
                'score': rf_score,
                'badge_class': rf_class,
                'mean_seasonal_mm': round(mean_rain, 1),
                'cv_pct': cv_pct,
                'deficit_frequency_pct': deficit_pct,
                'explanation': rf_exp,
                'is_insufficient': False,
            }
        else:
            rainfall_risk = {
                'level': 'Insufficient Data',
                'score': None,
                'badge_class': 'fp-badge-medium',
                'mean_seasonal_mm': None,
                'cv_pct': None,
                'deficit_frequency_pct': None,
                'explanation': "Incomplete annual rainfall totals prevent confidence assessment.",
                'is_insufficient': True,
            }

    # --------------------------------------------------------------------------
    # 2. Mid-Season Dry Spell Hazard (Critical Jan/Feb window)
    # --------------------------------------------------------------------------
    jan_feb_spells = [
        r.dry_spell_days_max for r in records
        if r.month in [1, 2] and r.dry_spell_days_max is not None
    ]

    if len(jan_feb_spells) < 6:
        dry_spell_risk = {
            'level': 'Insufficient Data',
            'score': None,
            'badge_class': 'fp-badge-medium',
            'max_consecutive_days': None,
            'severe_spell_freq_pct': None,
            'explanation': f"Insufficient dry-spell observations ({len(jan_feb_spells)} critical months recorded). At least 6 Jan/Feb periods required.",
            'is_insufficient': True,
        }
    else:
        max_spell = max(jan_feb_spells)
        # Severe dry spell in critical tasseling/flowering phase: >= 12 consecutive days
        severe_spells = sum(1 for days in jan_feb_spells if days >= 12)
        severe_pct = round((severe_spells / len(jan_feb_spells)) * 100, 1)

        if max_spell >= 16 or severe_pct >= 30:
            ds_level = 'High'
            ds_class = 'fp-badge-high'
            ds_score = 80
            ds_exp = f"Prolonged dry spells (>14 days) occur during the critical Jan/Feb flowering window in {severe_pct}% of seasons. Peak recorded dry spell was {max_spell} days."
        elif max_spell >= 11 or severe_pct >= 15:
            ds_level = 'Medium'
            ds_class = 'fp-badge-medium'
            ds_score = 50
            ds_exp = f"Moderate mid-season dry spell hazard. Short dry intervals (10-14 days) observed in {severe_pct}% of Jan/Feb cycles."
        else:
            ds_level = 'Low'
            ds_class = 'fp-badge-low'
            ds_score = 20
            ds_exp = f"Low mid-season dry spell frequency. Rains are typically well-distributed with rare interruptions exceeding 10 days."

        dry_spell_risk = {
            'level': ds_level,
            'score': ds_score,
            'badge_class': ds_class,
            'max_consecutive_days': max_spell,
            'severe_spell_freq_pct': severe_pct,
            'explanation': ds_exp,
            'is_insufficient': False,
        }

    # --------------------------------------------------------------------------
    # 3. Heat Wave & Temperature Stress
    # --------------------------------------------------------------------------
    heat_records = [r for r in records if r.temp_max_c is not None]
    if len(heat_records) < 24:
        heat_risk = {
            'level': 'Insufficient Data',
            'score': None,
            'badge_class': 'fp-badge-medium',
            'avg_heat_days_per_year': None,
            'max_temp_c': None,
            'explanation': f"Insufficient temperature time series ({len(heat_records)} monthly records available; minimum 24 required).",
            'is_insufficient': True,
        }
    else:
        all_max_temps = [float(r.temp_max_c) for r in heat_records]
        peak_temp = max(all_max_temps) if all_max_temps else 0.0

        # Annual heat wave days
        heat_days_by_year = {}
        for r in records:
            heat_days_by_year[r.year] = heat_days_by_year.get(r.year, 0) + (r.heat_wave_days or 0)

        heat_days_list = list(heat_days_by_year.values())
        avg_heat_days = round(statistics.mean(heat_days_list), 1) if heat_days_list else 0.0

        if avg_heat_days >= 12 or peak_temp >= 36.0:
            heat_level = 'High'
            heat_class = 'fp-badge-high'
            heat_score = 75
            heat_exp = f"Frequent thermal stress with average {avg_heat_days} extreme heat days annually. All-time recorded high is {peak_temp:.1f}°C."
        elif avg_heat_days >= 5 or peak_temp >= 33.0:
            heat_level = 'Medium'
            heat_class = 'fp-badge-medium'
            heat_score = 45
            heat_exp = f"Moderate heat exposure (averaging {avg_heat_days} heat days per year). Peak pre-rains temperature reaches {peak_temp:.1f}°C in Oct/Nov."
        else:
            heat_level = 'Low'
            heat_class = 'fp-badge-low'
            heat_score = 20
            heat_exp = f"Low thermal stress regime. Temperate highland conditions with average {avg_heat_days} heat days per year."

        heat_risk = {
            'level': heat_level,
            'score': heat_score,
            'badge_class': heat_class,
            'avg_heat_days_per_year': avg_heat_days,
            'max_temp_c': round(peak_temp, 1),
            'explanation': heat_exp,
            'is_insufficient': False,
        }

    # --------------------------------------------------------------------------
    # 4. Composite Assessment
    # --------------------------------------------------------------------------
    active_scores = [
        r['score'] for r in [rainfall_risk, dry_spell_risk, heat_risk]
        if r['score'] is not None
    ]

    insufficient_count = sum(
        1 for r in [rainfall_risk, dry_spell_risk, heat_risk]
        if r['level'] == 'Insufficient Data'
    )

    if insufficient_count >= 2:
        composite_level = 'Insufficient Data'
        composite_class = 'fp-badge-medium'
        composite_exp = "Comprehensive climate risk cannot be verified due to gaps in historical observations for this district."
        composite_score = None
    elif insufficient_count == 1:
        composite_score = round(statistics.mean(active_scores))
        if composite_score >= 65:
            composite_level = 'High'
            composite_class = 'fp-badge-high'
        elif composite_score >= 40:
            composite_level = 'Medium'
            composite_class = 'fp-badge-medium'
        else:
            composite_level = 'Low'
            composite_class = 'fp-badge-low'
        composite_exp = "Partial assessment derived from available parameters (one metric has insufficient historical coverage)."
    else:
        composite_score = round(statistics.mean(active_scores))
        if composite_score >= 65 or (rainfall_risk['level'] == 'High' and dry_spell_risk['level'] == 'High'):
            composite_level = 'High'
            composite_class = 'fp-badge-high'
            composite_exp = "Elevated climatic hazard profile driven by rainfall variability and dry spell frequency. Drought-tolerant cultivars strongly advised."
        elif composite_score >= 40 or rainfall_risk['level'] == 'Medium':
            composite_level = 'Medium'
            composite_class = 'fp-badge-medium'
            composite_exp = "Moderate climate risk. Sound agronomic management, staggered planting, and soil moisture conservation recommended."
        else:
            composite_level = 'Low'
            composite_class = 'fp-badge-low'
            composite_exp = "Favourable agro-climatic stability with dependable historical seasonal precipitation and low thermal stress."

    return {
        'rainfall': rainfall_risk,
        'dry_spell': dry_spell_risk,
        'heat': heat_risk,
        'composite': {
            'level': composite_level,
            'score': composite_score,
            'badge_class': composite_class,
            'explanation': composite_exp,
        },
        'metadata': {
            'total_months_evaluated': total_months,
            'years_range': f"{distinct_years[0]}–{distinct_years[-1]}" if distinct_years else "None",
            'is_synthetic': True,
        }
    }
