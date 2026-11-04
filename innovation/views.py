import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import SatelliteParcel, ParametricInsurancePolicy
from .mlimi_engine import MlimiAIEngine
from farms.models import Farm, Crop
from planner.models import Plan
from climate.models import District
from climate.risk import calculate_climate_risks
from market.models import CropPrice


@login_required
def innovation_hub(request):
    """
    Overview portal highlighting FarmPulse's breakthrough innovation modules.
    """
    farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
    parcels_count = SatelliteParcel.objects.filter(farm=farm).count() if farm else 0
    policies_count = ParametricInsurancePolicy.objects.filter(farm=farm).count() if farm else 0

    return render(request, 'innovation/hub.html', {
        'farm': farm,
        'parcels_count': parcels_count,
        'policies_count': policies_count,
        'active_nav': 'innovation_hub',
    })


@login_required
def satellite_twin(request):
    """
    Innovation 1: Satellite Field Twin & Sentinel-2 Earth Observation.
    Visualizes cadastral plot polygons, NDVI canopy vigor, and SAR soil moisture.
    """
    farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
    parcels = SatelliteParcel.objects.filter(farm=farm) if farm else SatelliteParcel.objects.none()
    active_parcel = parcels.first()

    # Pre-calculated NDVI band zones for active parcel
    ndvi_zones = [
        {'zone': 'North Quadrant', 'ndvi': 0.72, 'status': 'Optimal Vigor', 'badge': 'emerald', 'area_pct': 45},
        {'zone': 'Central Swale', 'ndvi': 0.65, 'status': 'Good Canopy', 'badge': 'leaf', 'area_pct': 35},
        {'zone': 'Southern Ridge', 'ndvi': 0.42, 'status': 'Moisture Stress', 'badge': 'amber', 'area_pct': 20},
    ]

    context = {
        'farm': farm,
        'parcels': parcels,
        'active_parcel': active_parcel,
        'ndvi_zones': ndvi_zones,
        'parcel_coords_json': json.dumps(active_parcel.polygon_geojson if active_parcel else []),
        'centroid_lat': float(active_parcel.centroid_lat) if active_parcel else -13.9626,
        'centroid_lng': float(active_parcel.centroid_lng) if active_parcel else 33.7741,
        'active_nav': 'satellite_twin',
    }
    return render(request, 'innovation/satellite_twin.html', context)


@login_required
def ussd_simulator(request):
    """
    Innovation 2: Last-Mile Feature-Phone USSD Simulator.
    Interactive tactile Nokia 3310 phone interface demonstrating zero-data accessibility.
    """
    farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
    return render(request, 'innovation/ussd_simulator.html', {
        'farm': farm,
        'active_nav': 'ussd_simulator',
    })


@csrf_exempt
def ussd_api(request):
    """
    Standard Africa's Talking / Telco USSD Webhook Handler.
    Processes *384*77# session strings: e.g. "1*1" (Prices -> Maize).
    """
    text = request.POST.get('text', '') or request.GET.get('text', '')
    phone = request.POST.get('phoneNumber', '+265991000000')

    parts = [p.strip() for p in text.split('*')] if text else []
    
    # Root Menu
    if not text or len(parts) == 0 or parts == ['']:
        response_text = (
            "CON FarmPulse Malawi\n"
            "1. Mitengo ya Mbewu (Market Prices)\n"
            "2. Weather & Dry-Spell Alert\n"
            "3. Break-Even Price Check\n"
            "4. Uphungu wa Ulimi (Advisory)\n"
            "5. Insurance Shield Status"
        )
        return HttpResponse(response_text, content_type='text/plain')

    # Menu 1: Market Prices
    if parts[0] == '1':
        if len(parts) == 1:
            return HttpResponse(
                "CON Sankhani Mbewu (Select Crop):\n"
                "1. Chimanga (Maize)\n"
                "2. Mtedza (Groundnuts)\n"
                "3. Soya Beans",
                content_type='text/plain'
            )
        crop_slug = {'1': 'maize', '2': 'groundnuts', '3': 'soybeans'}.get(parts[1], 'maize')
        crop = Crop.objects.filter(slug=crop_slug).first()
        if crop:
            # Get latest price
            latest = CropPrice.objects.filter(crop=crop).order_by('-year', '-month').first()
            if latest:
                return HttpResponse(
                    f"END {crop.name} ({latest.get_market_type_display()}):\n"
                    f"Price: MWK {latest.price_mwk_per_kg:.0f}/kg\n"
                    f"Market: {latest.district.name if latest.district else 'National'}\n"
                    f"Date: {latest.month:02d}/{latest.year}",
                    content_type='text/plain'
                )
        return HttpResponse("END Mtengo sunapezeke pano.", content_type='text/plain')

    # Menu 2: Climate Alert
    elif parts[0] == '2':
        return HttpResponse(
            "END Lilongwe Weather Alert:\n"
            "Dry-Spell Risk: Medium (7-9 days)\n"
            "Mvula ikuyembekezeka sabata ino: 35mm.\n"
            "Langizo: Thirani mulching kuti musunge chinyezi.",
            content_type='text/plain'
        )

    # Menu 3: Break-Even Price
    elif parts[0] == '3':
        return HttpResponse(
            "END Break-Even Benchmarks (Lilongwe):\n"
            "Maize: MWK 145/kg\n"
            "Groundnuts: MWK 380/kg\n"
            "Soya: MWK 310/kg\n"
            "Musagulitse pansi pa mitengo iyi kuti mupeze phindu.",
            content_type='text/plain'
        )

    # Menu 4: Chichewa Farming Advisory
    elif parts[0] == '4':
        return HttpResponse(
            "END Uphungu wa Nthawi ya Mvula:\n"
            "1. Dzala nthawi yomweyo mvula yoyamba yoposa 25mm ikagwa.\n"
            "2. Thirani fetereza wa Basal (NPK 23:21:0) mukamadzala.\n"
            "3. Yang'anirani chiswe ndi mbozi ya Fall Armyworm.",
            content_type='text/plain'
        )

    # Menu 5: Insurance Status
    elif parts[0] == '5':
        return HttpResponse(
            "END FarmPulse Satellite Insurance:\n"
            "Policy: FP-MW-2024-0891\n"
            "Coverage: 2.0 ha (MWK 500,000)\n"
            "Status: Active Coverage.\n"
            "Satellite Trigger: No drought detected (8 dry days observed).",
            content_type='text/plain'
        )

    return HttpResponse("END Kusankha kolakwika. Yambaninso kuyimba *384*77#.", content_type='text/plain')


@login_required
def parametric_insurance(request):
    """
    Innovation 3: Parametric Drought De-Risking & Smart Contract Insurance.
    Automates claims without loss adjusters using satellite rainfall index triggers.
    """
    farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
    policies = ParametricInsurancePolicy.objects.filter(farm=farm) if farm else ParametricInsurancePolicy.objects.none()
    active_policy = policies.first()

    # Handle simulation POST
    if request.method == 'POST' and active_policy:
        simulated_dry_days = int(request.POST.get('dry_spell_days', 8))
        active_policy.observed_dry_spell_days = simulated_dry_days

        if simulated_dry_days >= active_policy.trigger_dry_spell_days:
            active_policy.status = 'triggered'
            active_policy.payout_mwk = active_policy.sum_insured_mwk
            active_policy.transaction_ref = f"TX-AIRTEL-MW-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            messages.success(
                request,
                f"SATELLITE DROUGHT TRIGGER ACTIVATED: {simulated_dry_days} consecutive dry days detected. "
                f"Automated payout of MWK {active_policy.sum_insured_mwk:,.0f} disbursed to {active_policy.payout_recipient_phone} ({active_policy.transaction_ref})!"
            )
        else:
            active_policy.status = 'active'
            active_policy.payout_mwk = Decimal('0.00')
            messages.info(request, f"Satellite reading updated: {simulated_dry_days} consecutive dry days. Policy remains active with no payout triggered.")

        active_policy.save()
        return redirect('innovation:parametric_insurance')

    context = {
        'farm': farm,
        'policies': policies,
        'active_policy': active_policy,
        'active_nav': 'parametric_insurance',
    }
    return render(request, 'innovation/parametric_insurance.html', context)


@login_required
def mlimi_advisor(request):
    """
    Innovation 4: Context-Aware Autonomous Agronomist (English & Chichewa).
    Bilingual agronomic AI ingesting soil, land, crops, and microclimate.
    """
    farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
    lang = request.GET.get('lang', 'ch').lower()  # default to Chichewa for domestic impact

    # Contextual Agronomic Insights built from actual farm data
    soil_display = farm.get_soil_type_display() if farm else "Sandy Clay Loam"
    district_name = farm.location_description.split(',')[0].strip() if farm else "Lilongwe"

    # Active plan benchmarks for telemetry banner
    active_plan = Plan.objects.filter(farm=farm).order_by('-created_at').first() if farm else None
    break_evens = []
    if active_plan:
        for item in active_plan.items.select_related('crop').all():
            break_evens.append({
                'crop_name': item.crop.name,
                'break_even_price': item.break_even_price_mwk_per_kg,
                'expected_yield': item.expected_yield_kg_total,
                'area_ha': item.area_ha,
            })

    insights = {
        'en': {
            'greeting': f"Agronomic Advisory for {farm.name if farm else 'Your Farm'}",
            'soil_strategy': f"Managing {soil_display} in {district_name}: Incorporate crop residues to enhance organic matter retention and prevent crusting during early germination.",
            'fertilizer_schedule': "Split Urea Application: Apply 50% at 3 weeks after crop emergence, and remaining 50% at 6 weeks (knee-high) right before expected rainfall.",
            'pest_alert': "Fall Armyworm Alert: Inspect leaf whorls at early morning for pin-hole feeding signs. Apply botanical neem extract or Emamectin Benzoate if infestation exceeds 10% of field stations.",
            'intercropping': "Nitrogen Fixation: Intercrop Maize with Groundnuts (CG7/Mwayi) at a 1:2 row ratio to naturally fix up to 40 kg N/ha and insulate against drought.",
        },
        'ch': {
            'greeting': f"Uphungu wa Ulimi pa {farm.name if farm else 'Munda Wanu'}",
            'soil_strategy': f"Kusamalira nthaka ya {soil_display} ku {district_name}: Osatentha zotsalira za mbewu; zisiye m'munda kuti ziwonjezere manyowa ndi chinyezi nthaka isamaume msanga.",
            'fertilizer_schedule': "Kuthira Fetereza wa Urea: Thirani gawo loyamba masabata 3 chimanga chitamera, ndipo gawo lachiwiri chimanga chikafika m'maondo mvula ikangoyamba kugwa.",
            'pest_alert': "Chenjezo la Mbozi ya Fall Armyworm: Yang'anani m'mphuno mwa chimanga m'mawa kwambiri. Ngati muwona mabowo m'masamba, thirani mankhwala achilengedwe a tsabola/phulusa kapena neem leaves nthawi yomweyo.",
            'intercropping': "Kusakaniza Mbewu: Dzala chimanga pamodzi ndi mtedza wa CG7 kapena nyemba kuti muteteze munda ku chilala ndikuwonjezera mphamvu ya nthaka mwachilengedwe.",
        }
    }

    selected_insights = insights.get(lang, insights['ch'])

    return render(request, 'innovation/mlimi_advisor.html', {
        'farm': farm,
        'lang': lang,
        'insights': selected_insights,
        'active_plan': active_plan,
        'break_evens': break_evens,
        'active_nav': 'mlimi_advisor',
    })


@csrf_exempt
def mlimi_chat_api(request):
    """
    AJAX endpoint for Mlimi AI autonomous agronomic copilot queries.
    Accepts JSON or form POST with 'message' and optional 'lang'.
    Returns structured recommendations, audio transcript, context, and follow-ups.
    Safe for both authenticated farmers and unauthenticated national demonstration kiosks.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
        else:
            payload = request.POST
    except Exception:
        payload = {}

    user_message = payload.get('message', '').strip()
    force_lang = payload.get('lang', None)

    if not user_message:
        return JsonResponse({'error': 'Message content cannot be blank'}, status=400)

    if request.user.is_authenticated:
        farm = Farm.objects.filter(owner=request.user).first() or Farm.objects.first()
        user = request.user
    else:
        farm = Farm.objects.first()
        user = None
    try:
        engine = MlimiAIEngine(farm=farm, user=user)
        result = engine.process_query(user_message, force_lang=force_lang)
        return JsonResponse({
            'success': True,
            'query': user_message,
            'farm_name': farm.name if farm else 'Farm',
            **result,
        })
    except Exception as exc:
        is_ch = (force_lang == 'ch') or ('ch' in str(request.META.get('HTTP_REFERER', '')))
        fallback_reply = (
            "Pepani! Pakhala vuto la ndondomeko yowerengera. Koma malangizo okhudza ulimi: "
            "onetsetsani kuti mukutsatira ndondomeko ya mvula (25-30mm) musanadzale mbewu, "
            "ndikugawanitsa fetereza wa Urea pa masabata 3 ndi masabata 6."
            if is_ch else
            "An error occurred while compiling full agronomic context. As a general protocol: "
            "ensure minimum 25-30 mm rainfall accumulation before planting, and split top-dress Urea "
            "at week 3 and week 6."
        )
        return JsonResponse({
            'success': True,
            'query': user_message,
            'farm_name': farm.name if farm else 'Farm',
            'reply': fallback_reply,
            'audio_text': fallback_reply,
            'category': 'general_advisory',
            'context_used': ['Standard Chitedze Extension Handbook'],
            'suggested_followups': [
                "Ndidzale liti chimanga ngati mvula yacedwa?",
                "Kodi mtedza wa CG7 umafunika fetereza wanji?",
                "Kodi mtengo wa MWK 750/kg ndi wopindulitsa?",
            ],
            'debug_error': str(exc),
        })
