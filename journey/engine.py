"""
journey/engine.py
Smart advisory engine for FarmPulse Season Journey.
Generates contextual farming advice based on check-in data.
"""

STAGE_FERTILISER_ALERTS = {
    'prep': [
        "Before planting, apply basal fertiliser (D-Compound) at 200 kg/ha to build soil nutrient base.",
        "Test your soil pH if possible — maize prefers pH 5.5 to 7.0.",
    ],
    'germination': [
        "Ensure soil moisture is consistent during germination — do not let topsoil dry out.",
        "Check seed emergence uniformity at 7-10 days. Re-plant gaps above 10% to protect yield.",
    ],
    'vegetative': [
        "Apply top-dress fertiliser (CAN or Urea) at 6-8 weeks after planting when maize reaches knee height.",
        "Weed aggressively in the first 6 weeks — this is the highest-impact intervention for yield.",
    ],
    'flowering': [
        "Silking stage is the most moisture-sensitive phase. Any water stress now directly cuts yield.",
        "Avoid applying nitrogen fertiliser after silking — it will not improve grain fill.",
    ],
    'grain_fill': [
        "Grain fill is active — maintain soil moisture and protect from lodging caused by wind.",
        "Scout for stalk borer damage at the base of plants — treat immediately if found.",
    ],
    'maturity': [
        "Assess physiological maturity by checking for black layer at base of kernel.",
        "Delay harvest if moisture content is above 25% to reduce storage losses.",
    ],
    'harvest': [
        "Harvest at 20-25% grain moisture. Dry to below 13% before long-term storage.",
        "Use PICS bags or hermetic storage to prevent post-harvest losses from weevils.",
    ],
}

PEST_ADVISORIES = {
    'light': "Light pest pressure detected. Scout weekly and monitor population trends before treating.",
    'moderate': (
        "Moderate pest pressure. Identify the pest species and apply targeted control — "
        "Fall Armyworm: apply Emamectin benzoate 1.9EC at first sign. Aphids: spot-spray "
        "affected zones with a registered insecticide."
    ),
    'severe': (
        "SEVERE pest pressure — act immediately. Consult your extension officer and apply "
        "appropriate registered pesticide. Document all treatments in your activity log."
    ),
}

DISEASE_ADVISORIES = {
    'light': "Light disease signs. Remove and destroy infected plant material. Improve air circulation.",
    'moderate': (
        "Moderate disease pressure. Apply a registered fungicide. Common maize diseases: "
        "Grey Leaf Spot — apply Mancozeb; Northern Leaf Blight — apply Propiconazole."
    ),
    'severe': (
        "SEVERE disease outbreak. Apply fungicide immediately and report to your extension officer. "
        "Document losses in your activity log for insurance claims."
    ),
}

MOISTURE_ADVISORIES = {
    1: (
        "Very dry conditions — CRITICAL water stress risk. If irrigation is available, apply immediately. "
        "Mulch around plants to conserve remaining soil moisture."
    ),
    2: (
        "Dry soil conditions detected. If rains are delayed over 7 days, consider supplemental irrigation "
        "or drought mitigation (mulching, shade cloth on seedlings)."
    ),
    4: "Soil moisture is good. Continue monitoring and avoid over-irrigation which causes root disease.",
    5: (
        "Waterlogged conditions detected. Improve drainage urgently — maize cannot tolerate flooded roots "
        "for more than 48 hours without yield loss."
    ),
}


def generate_advisory(stage, pest_pressure, disease_pressure, moisture_score, week_number):
    """
    Generate a structured advisory message from check-in data.
    Returns a plain-text string with actionable recommendations.
    """
    lines = []

    # Stage-specific fertiliser / management tips
    stage_tips = STAGE_FERTILISER_ALERTS.get(stage, [])
    if stage_tips:
        lines.append(f"STAGE ADVISORY ({stage.replace('_', ' ').title()}):")
        for tip in stage_tips:
            lines.append(f"  - {tip}")

    # Pest advisory
    if pest_pressure and pest_pressure != 'none':
        lines.append("\nPEST ALERT:")
        lines.append(f"  - {PEST_ADVISORIES[pest_pressure]}")

    # Disease advisory
    if disease_pressure and disease_pressure != 'none':
        lines.append("\nDISEASE ALERT:")
        lines.append(f"  - {DISEASE_ADVISORIES[disease_pressure]}")

    # Moisture advisory
    if moisture_score in MOISTURE_ADVISORIES:
        lines.append("\nMOISTURE / WATER ADVISORY:")
        lines.append(f"  - {MOISTURE_ADVISORIES[moisture_score]}")

    # Week-specific reminders
    if week_number == 1:
        lines.append("\nWEEK 1 REMINDER:")
        lines.append("  - Record all seed, fertiliser, and labour costs in your activity log from day one.")
    elif week_number == 4:
        lines.append("\nWEEK 4 CHECK:")
        lines.append("  - Assess plant population. Count plants in a 5m row and multiply by 20,000 for stand count per ha.")
    elif week_number == 8:
        lines.append("\nWEEK 8 CHECK:")
        lines.append("  - Confirm top-dress fertiliser application is complete. Late application loses 30-40% efficiency.")

    if not lines:
        lines.append("No specific advisories this week. Continue monitoring and record all farm activities.")

    return "\n".join(lines)

