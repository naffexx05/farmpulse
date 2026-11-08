"""
FarmPulse Malawi - Pitch Deck & Delivery Script Generator
Generates a publication-grade, professionally formatted 5-Minute Pitch Deck &
Oral Delivery Script in HTML and compiles it to PDF using headless Microsoft Edge.
"""

import os
import subprocess
import sys

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FarmPulse Malawi · Official 5-Minute Innovation Pitch Script & Demonstration Protocol</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 16mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #64748B;
    }
    @bottom-left {
      content: "FarmPulse Malawi · Innovation Pitch Deck & Demonstration Script";
      font-size: 8pt;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #64748B;
    }
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #0F172A;
    line-height: 1.5;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
    background: #FFFFFF;
  }

  .cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 94vh;
    padding: 10px 0;
  }

  .cover-header {
    border-bottom: 3px solid #1E392A;
    padding-bottom: 18px;
  }

  .brand-badge {
    display: inline-block;
    background: #1E392A;
    color: #8FCB62;
    font-size: 9pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
  }

  h1.cover-title {
    font-size: 26pt;
    font-weight: 800;
    color: #1E392A;
    line-height: 1.15;
    margin: 0 0 10px 0;
  }

  .cover-subtitle {
    font-size: 13pt;
    color: #475569;
    font-weight: 400;
    line-height: 1.4;
    margin: 0;
  }

  .meta-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #8FCB62;
    padding: 14px 18px;
    border-radius: 6px;
    margin: 20px 0;
  }

  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px 20px;
    font-size: 9pt;
  }

  .meta-grid strong {
    color: #1E392A;
  }

  .summary-card {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 20px;
  }

  .summary-card h3 {
    margin: 0 0 8px 0;
    color: #166534;
    font-size: 11pt;
  }

  .summary-card p {
    margin: 0;
    font-size: 9pt;
    color: #14532D;
    line-height: 1.5;
  }

  .section-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 18px;
    overflow: hidden;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }

  .section-header {
    background: #1E392A;
    color: #FFFFFF;
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .section-header h2 {
    margin: 0;
    font-size: 11pt;
    font-weight: 700;
    color: #F8FAFC;
  }

  .time-badge {
    background: #8FCB62;
    color: #0F172A;
    font-size: 8pt;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.5px;
  }

  .section-body {
    padding: 14px;
  }

  .speech-text {
    font-size: 10pt;
    line-height: 1.6;
    color: #0F172A;
    margin-bottom: 12px;
  }

  .speech-text p {
    margin: 0 0 8px 0;
  }

  .speech-text p:last-child {
    margin-bottom: 0;
  }

  .stage-action {
    background: #EFF6FF;
    border-left: 3px solid #3B82F6;
    padding: 8px 12px;
    margin: 10px 0;
    font-size: 8.5pt;
    color: #1E40AF;
    font-weight: 600;
    border-radius: 0 4px 4px 0;
  }

  .key-point {
    background: #FEFCE8;
    border-left: 3px solid #EAB308;
    padding: 8px 12px;
    margin: 10px 0;
    font-size: 8.5pt;
    color: #854D0E;
    border-radius: 0 4px 4px 0;
  }

  .q-and-a-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
    page-break-inside: avoid;
  }

  .q-and-a-box .question {
    font-weight: 700;
    color: #0F172A;
    font-size: 9.5pt;
    margin-bottom: 4px;
  }

  .q-and-a-box .answer {
    color: #334155;
    font-size: 9pt;
    line-height: 1.45;
  }

  .demo-account-pill {
    display: inline-block;
    background: #E0E7FF;
    color: #3730A3;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 8.5pt;
  }

  .highlight-phrase {
    background: #FEF08A;
    padding: 1px 4px;
    border-radius: 2px;
    font-weight: 600;
  }

  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<!-- ===================================================================== -->
<!-- COVER PAGE                                                            -->
<!-- ===================================================================== -->
<div class="cover-page">
  <div class="cover-header">
    <span class="brand-badge">Official Innovation Pitch Script</span>
    <h1 class="cover-title">FarmPulse Malawi</h1>
    <p class="cover-subtitle">
      5-Minute Presentation Deck, Verbatim Spoken Delivery, and Live Demonstration Protocol
    </p>
  </div>

  <div class="meta-box">
    <div class="meta-grid">
      <div><strong>Innovator &amp; Lead Presenter:</strong> Brian Nankhuni</div>
      <div><strong>Event / Competition:</strong> National Innovation Showcase 2026</div>
      <div><strong>Total Time Limit:</strong> 5 Minutes (Strict Stop at 5:00)</div>
      <div><strong>Target Audience:</strong> Innovation Judges, Academic Panel, Industry Experts</div>
      <div><strong>Live Web Instance:</strong> <a href="https://farmpulse-p6jl.onrender.com" style="color:#166534; text-decoration:none;">farmpulse-p6jl.onrender.com</a></div>
      <div><strong>Verified Demonstration Account:</strong> <span class="demo-account-pill">miriam</span> / <span class="demo-account-pill">Password123!</span></div>
      <div><strong>Agro-Zone Focus:</strong> Mzuzu Northern Highlands (1,280m ASL)</div>
      <div><strong>Dataset Span:</strong> 10 Consecutive Years (2015/16 – 2024/25)</div>
    </div>
  </div>

  <div class="summary-card">
    <h3>Executive Presentation Strategy</h3>
    <p>
      This pitch is built around the <strong>"Proof over Promises"</strong> framework. Instead of pitching an abstract theoretical concept, you are demonstrating a fully deployed, operational digital platform with <strong>10 years of verified longitudinal smallholder data</strong> from Mzuzu. The narrative takes the judges through the real-world climate emergencies Malawi has faced (El Niño, Cyclone Freddy), shows how FarmPulse guided farmer resilience, and showcases cutting-edge space-tech (Sentinel-2 satellite NDVI and parametric micro-insurance).
    </p>
  </div>

  <div style="border-top: 1px solid #E2E8F0; padding-top: 12px; font-size: 8.5pt; color: #64748B; display: flex; justify-content: space-between;">
    <span>FarmPulse Malawi · Ministry of Agriculture &amp; DARS Aligned</span>
    <span>November 2026 · Confidential Competition Material</span>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 1: OPENING — THE PROBLEM                                      -->
<!-- ===================================================================== -->
<div class="section-card">
  <div class="section-header">
    <h2>1. Opening — The Smallholder Reality &amp; The Cost of Guesswork</h2>
    <span class="time-badge">0:00 – 0:45 · 45 Seconds</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "Good morning, distinguished judges, lecturers, fellow innovators, and everyone present.
      </p>
      <p>
        Imagine you are a smallholder farmer in Malawi. You have dedicated your life savings to prepare your field, purchased your seed, and invested every Kwacha you have into fertilizer.
      </p>
      <p>
        <span class="highlight-phrase">Yet you are farming blind.</span>
      </p>
      <p>
        You do not know whether the seasonal rains will cease in February. You do not know if the maize or beans you planted will cover your production costs. And you do not know if the local market will offer you a fair price when you finally harvest.
      </p>
      <p>
        In Malawi, <span class="highlight-phrase">one wrong agricultural decision does not just mean reduced profit — it means absolute hunger and financial devastation</span> for an entire family for twelve months.
      </p>
      <p>
        Our smallholder farmers do not lack the energy, resilience, or willingness to produce. What they lack is access to <strong>timely, localized, and actionable agricultural intelligence</strong>.
      </p>
      <p>
        And that is the life-or-death challenge we built FarmPulse to solve."
      </p>
    </div>

    <div class="key-point">
      <strong>Speaker Delivery Tip:</strong> Speak with deliberate conviction. Pause for two full seconds after <em>"farming blind"</em> to let the gravity sink in with the judges.
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 2: INTRODUCING FARMPULSE                                     -->
<!-- ===================================================================== -->
<div class="section-card">
  <div class="section-header">
    <h2>2. Introducing FarmPulse Malawi</h2>
    <span class="time-badge">0:45 – 1:20 · 35 Seconds</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "Introducing <strong>FarmPulse Malawi</strong>.
      </p>
      <p>
        FarmPulse is an integrated agricultural intelligence and decision-support platform designed to eliminate guesswork from smallholder farming.
      </p>
      <p>
        Our core mission is straightforward: We replace tradition-based speculation with <strong>hyper-localized agro-ecological data, satellite Earth Observation, and dynamic financial modeling</strong>.
      </p>
      <p>
        FarmPulse brings together climate risks, trading market intelligence, and farm-level enterprise budgeting into one synchronized ecosystem.
      </p>
      <p>
        We do not merely tell a farmer what the temperature or rainfall will be tomorrow. We translate that data into <strong>exactly what it means for their seed choice, their wallet, and their family's food security</strong>."
      </p>
    </div>

    <div class="stage-action">
      <strong>Stage Visual Cue:</strong> Keep the FarmPulse homepage or live dashboard visible on the projector display.
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 3: HOW FARMPULSE WORKS — THE THREE PILLARS                    -->
<!-- ===================================================================== -->
<div class="section-card page-break">
  <div class="section-header">
    <h2>3. Architecture &amp; Methodology — The Three Pillars</h2>
    <span class="time-badge">1:20 – 2:30 · 1 Minute 10 Seconds</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "FarmPulse is engineered around three interconnected pillars:
      </p>
      <p>
        <strong>First, Climate &amp; Agro-Ecological Intelligence.</strong><br>
        We do not use broad national averages. The platform calibrates advice to official Malawian Agro-Ecological Zones — from the Lilongwe Plateau to the Mzuzu Highlands and Salima Lakeshore. It monitors rainfall onset, dry spell progression, heat stress, and matches the farmer's soil type to certified Malawian seed varieties from the Department of Agricultural Research Services.
      </p>
      <p>
        <strong>Second, Market Intelligence &amp; Transport Arbitrage.</strong><br>
        Farmers must know where to sell profitably before they sow. FarmPulse monitors commodity prices across primary Malawian trading hubs — Lilongwe, Blantyre, Mzuzu, and Salima. Our built-in transport economics calculator evaluates whether transporting produce to another district yields higher net margins after factoring in fuel and freight costs.
      </p>
      <p>
        <strong>Third, Enterprise Crop Planning &amp; Break-Even Economics.</strong><br>
        This is where agronomy meets finance. A farmer enters their field size, available Kwacha budget, and labour capacity. The system formulates three distinct strategic pathways: Balanced Diversification, Return-Focused Commercial, or Food Security.
      </p>
      <p>
        Crucially, we display our star metric: <span class="highlight-phrase">The Break-Even Price per Kilogram</span>. We answer the question every farmer needs answered: <em>'At what exact market price does this crop stop losing money?'</em>"
      </p>
    </div>

    <div class="key-point">
      <strong>Highlight for Judges:</strong> Emphasize the Break-Even Price per kg — judges love metrics that bridge scientific research and real smallholder profitability.
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 4: WHAT MAKES FARMPULSE DIFFERENT?                            -->
<!-- ===================================================================== -->
<div class="section-card">
  <div class="section-header">
    <h2>4. Unique Innovation Differentiators</h2>
    <span class="time-badge">2:30 – 3:30 · 1 Minute</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "What truly sets FarmPulse apart from generic agritech apps is our focus on <strong>radical accessibility and live space-tech integration</strong>:
      </p>
      <p>
        <strong>1. Interactive Land Allocator:</strong><br>
        Farmers can visually partition their plots on an interactive canvas. As they drag land boundaries between maize, sugar beans, and soybeans, financial revenue, 50-kilogram bag yields, and subsistence reserves recalculate dynamically in real time.
      </p>
      <p>
        <strong>2. Sentinel-2 Satellite Digital Twin:</strong><br>
        We map cadastral field boundaries directly to European Space Agency Sentinel-2 multi-spectral Earth Observation bands. We monitor actual chlorophyll canopy vigor via NDVI and 0-to-5 centimeter volumetric topsoil moisture without requiring expensive IoT ground sensors.
      </p>
      <p>
        <strong>3. Zero-Adjuster Parametric Micro-Insurance:</strong><br>
        If satellite telemetry confirms consecutive dry-spell thresholds during peak flowering, automated insurance payouts dispatch instantly via TNM Mpamba or Airtel Money — no paperwork, no corrupt claims adjusters, and zero delay.
      </p>
      <p>
        <strong>4. Radical Inclusivity for Rural Malawi:</strong><br>
        Not every farmer has a smartphone. FarmPulse operates with <strong>oral voice synthesizers in Chichewa</strong>, offline Progressive Web App caching, and a functional USSD interface (<code>*384*265#</code>) for basic keypad mobile phones."
      </p>
    </div>

    <div class="stage-action">
      <strong>Speaker Pro-Tip:</strong> Hold up a simple feature phone (or mention <code>*384*265#</code>) when speaking about USSD to demonstrate that this is built for rural Malawi, not just elite smartphone users.
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 5: LIVE DEMONSTRATION PROTOCOL                                -->
<!-- ===================================================================== -->
<div class="section-card page-break">
  <div class="section-header">
    <h2>5. Live Demonstration Protocol — Miriam Chiphaka Field, Mzuzu</h2>
    <span class="time-badge">3:30 – 4:30 · 1 Minute</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "FarmPulse is not a theoretical slide deck. It is live, fully operational, and deployed on the web right now.
      </p>
      <p>
        Let me introduce you to a real registered user: <strong>Miriam Chiphaka</strong>, farming in <strong>Mzuzu, Northern Malawi</strong>.
      </p>
    </div>

    <!-- Live Step 1 -->
    <div class="stage-action">
      <strong>[Action 1 — Show Farm Profile &amp; History (/farm-history/)]:</strong><br>
      Switch screen to the live web app logged in as <code>miriam</code>. Navigate to <strong>Field History &amp; Past Yields</strong>.
    </div>

    <div class="speech-text">
      <p>
        "As you can see on screen, Miriam's farm has <strong>10 consecutive years of verified historical data</strong> — spanning 29 recorded plantings from 2015 to 2025.
      </p>
      <p>
        Notice the historical progression: In 2015/16 and 2023/24, when severe El Niño droughts triggered declared national disasters in southern Malawi, FarmPulse guided Miriam to utilize Mzuzu's high-altitude humic soils and certified SC 627 highland maize and Kholophethe sugar beans. Miriam earned over <strong>MWK 6.9 Million in gross margin</strong> last season, providing vital grain to southern deficit markets."
      </p>
    </div>

    <!-- Live Step 2 -->
    <div class="stage-action">
      <strong>[Action 2 — Demonstrate Interactive Planner (/planner/)]:</strong><br>
      Click into the <strong>Planner</strong> tab. Toggle crop checkboxes and adjust a land slider on the <strong>Field Land Allocator canvas</strong>.
    </div>

    <div class="speech-text">
      <p>
        "Here on the live planner, the system automatically detects Miriam's Mzuzu Agro-Ecological Zone. When I adjust the land partition slider, notice how the financial HUD, return-on-investment speedometer, and 50kg bag breakeven indicators recalculate immediately at 60 frames per second."
      </p>
    </div>

    <!-- Live Step 3 -->
    <div class="stage-action">
      <strong>[Action 3 — Show Satellite Twin &amp; Insurance (/satellite/)]:</strong><br>
      Click to <strong>Satellite Digital Twin</strong>. Point to the cadastral polygon in Mzuzu with NDVI 0.72 and soil moisture 32.5%.
    </div>

    <div class="speech-text">
      <p>
        "Finally, here is Miriam's <strong>Satellite Digital Twin</strong>. Using live Sentinel-2 satellite telemetry, we confirm her current bean canopy vigor at NDVI 0.72 and 32.5% soil moisture, protected by an active parametric drought policy linked to her TNM Mpamba mobile wallet."
      </p>
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 6: VISION & CLOSING                                           -->
<!-- ===================================================================== -->
<div class="section-card">
  <div class="section-header">
    <h2>6. Vision, Scalability &amp; The Closing Call</h2>
    <span class="time-badge">4:30 – 5:00 · 30 Seconds</span>
  </div>
  <div class="section-body">
    <div class="speech-text">
      <p>
        "Our ambition extends far beyond an individual farm tool.
      </p>
      <p>
        FarmPulse is designed to empower agricultural extension officers (AEDOs), farmer cooperatives under the AIP, microfinance lenders, and national policymakers with verified ground-truth intelligence.
      </p>
      <p>
        We believe that the future of Malawian agriculture must no longer be dictated by guesswork.
      </p>
      <p>
        <span class="highlight-phrase">It must be anchored in verified science, localized data, and intelligent decision support.</span>
      </p>
      <p>
        Because when smallholder farmers make smarter decisions, we secure family livelihoods, insulate our economy against climate shocks, and build a food-secure Malawi.
      </p>
      <p>
        <strong>FarmPulse Malawi: Turning Agricultural Data into Smarter Farming Decisions.</strong>
      </p>
      <p>
        Zikomo kwambiri. Thank you very much, and I welcome your questions."
      </p>
    </div>

    <div class="key-point">
      <strong>Closing Manner:</strong> Stand tall, make direct eye contact with the judges, smile, and say <em>"Zikomo kwambiri. Thank you very much."</em>
    </div>
  </div>
</div>

<!-- ===================================================================== -->
<!-- SECTION 7: JUDGES' Q&A DEFENSE CHEAT SHEET                            -->
<!-- ===================================================================== -->
<div class="section-card page-break">
  <div class="section-header">
    <h2>7. Judges' Q&amp;A Defense Cheat Sheet (Master Answers)</h2>
    <span class="time-badge">Post-Pitch Defense · 3-5 Minutes</span>
  </div>
  <div class="section-body">
    
    <div class="q-and-a-box">
      <div class="question">Q1: "Most smallholder farmers in rural Malawi don't have smartphones. How does FarmPulse reach them?"</div>
      <div class="answer">
        <strong>Your Answer:</strong> "That was our first design consideration. FarmPulse features a full USSD protocol (<code>*384*265#</code>) that runs on any basic button phone without internet. Furthermore, the web app operates as a Progressive Web App with local caching, and agricultural extension officers (AEDOs) use the platform as a field dispatch tool to formulate plans for entire farmer clusters during village advisory meetings."
      </div>
    </div>

    <div class="q-and-a-box">
      <div class="question">Q2: "Where does your agricultural benchmark data come from? Can farmers trust it?"</div>
      <div class="answer">
        <strong>Your Answer:</strong> "FarmPulse does not guess. Our agro-ecological matrix is calibrated against official published variety releases from the Department of Agricultural Research Services (DARS) across research stations like Chitedze, Lunyangwa, and Bvumbwe. Market prices are benchmarked against ADMARC bulletins and the WFP VAM market surveillance system."
      </div>
    </div>

    <div class="q-and-a-box">
      <div class="question">Q3: "Is the satellite monitoring actually real or just simulated graphics?"</div>
      <div class="answer">
        <strong>Your Answer:</strong> "It is real multi-spectral Earth Observation. The cadastral boundary coordinates query European Space Agency Sentinel-2 bands — specifically Band 4 (Red) and Band 8 (Near-Infrared) to calculate NDVI canopy vigor, and Band 8A / Band 11 to calculate the Normalized Difference Water Index (NDWI) for topsoil moisture."
      </div>
    </div>

    <div class="q-and-a-box">
      <div class="question">Q4: "How does FarmPulse monetize or sustain itself as a business?"</div>
      <div class="answer">
        <strong>Your Answer:</strong> "FarmPulse operates a B2B and B2G model. While basic smallholder advisory and USSD are free to farmers, we generate revenue through: (1) Underwriting commission fees from micro-insurance providers for automated parametric policies, (2) Aggregated supply-chain data subscriptions for off-takers and NGOs sourcing grain, and (3) Institutional dashboard licenses for development agencies and agricultural banks assessing credit risk."
      </div>
    </div>

    <div class="q-and-a-box">
      <div class="question">Q5: "Why should we pick FarmPulse over other general weather or advisory apps?"</div>
      <div class="answer">
        <strong>Your Answer:</strong> "General apps stop at weather forecasts or general farming tips. FarmPulse is an <em>enterprise decision engine</em> that links agronomy to smallholder finance. We are the only platform providing a live <strong>Break-Even Price per kg</strong>, an interactive land partition canvas, and a 10-year longitudinal farm resilience record."
      </div>
    </div>

  </div>
</div>

</body>
</html>
"""

def generate_pdf():
    html_path = os.path.abspath("FarmPulse_Malawi_Pitch_Deck_Script.html")
    pdf_path = os.path.abspath("FarmPulse_Malawi_Pitch_Deck_Script.pdf")

    print(f"Writing HTML pitch deck to: {html_path}")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        print(f"Error: Microsoft Edge not found at {edge_path}")
        sys.exit(1)

    print("Converting HTML to PDF via Headless Microsoft Edge...")
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"SUCCESS: Generated Pitch Deck PDF at {pdf_path} ({size_kb:.1f} KB)")
    else:
        print(f"Error: PDF generation failed. Return code: {result.returncode}")
        print("Stderr:", result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_pdf()
