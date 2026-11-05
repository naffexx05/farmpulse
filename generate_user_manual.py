"""
FarmPulse Malawi - User Manual Generator
Generates a complete, exhaustive, publication-grade User Manual in HTML
and compiles it to a high-resolution PDF using headless Microsoft Edge.
"""

import os
import subprocess
import sys

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FarmPulse Malawi · Official User Manual & Operational Handbook</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #64748B;
    }
    @bottom-left {
      content: "FarmPulse Malawi · National Agricultural Intelligence Platform";
      font-size: 8pt;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #64748B;
    }
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1E293B;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background: #FFFFFF;
  }

  .cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 92vh;
    padding: 20px 0;
  }

  .cover-header {
    border-bottom: 4px solid #16A34A;
    padding-bottom: 25px;
  }

  .cover-badge {
    display: inline-block;
    background: #DCFCE7;
    color: #15803D;
    font-size: 9pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    border: 1px solid #86EFAC;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 15px;
  }

  .cover-title {
    font-size: 28pt;
    font-weight: 800;
    color: #062B20;
    line-height: 1.15;
    margin: 0 0 10px 0;
  }

  .cover-subtitle {
    font-size: 14pt;
    color: #475569;
    font-weight: 500;
    margin: 0 0 15px 0;
    line-height: 1.4;
  }

  .cover-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-top: 40px;
    padding: 20px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
  }

  .meta-item {
    font-size: 9pt;
  }

  .meta-item strong {
    color: #0F172A;
    display: block;
    margin-bottom: 2px;
  }

  .meta-item span {
    color: #64748B;
  }

  .cover-footer {
    border-top: 1px solid #E2E8F0;
    padding-top: 20px;
    font-size: 8.5pt;
    color: #64748B;
    display: flex;
    justify-content: space-between;
  }

  .page-break {
    page-break-before: always;
  }

  h1 {
    font-size: 18pt;
    color: #062B20;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 6px;
    margin-top: 28px;
    margin-bottom: 14px;
    font-weight: 800;
  }

  h2 {
    font-size: 13pt;
    color: #15803D;
    margin-top: 20px;
    margin-bottom: 8px;
    font-weight: 700;
  }

  h3 {
    font-size: 11pt;
    color: #0F172A;
    margin-top: 14px;
    margin-bottom: 6px;
    font-weight: 700;
  }

  p {
    margin: 0 0 10px 0;
  }

  ul, ol {
    margin: 0 0 12px 0;
    padding-left: 22px;
  }

  li {
    margin-bottom: 5px;
  }

  .callout-box {
    background: #F0FDF4;
    border-left: 4px solid #16A34A;
    padding: 12px 14px;
    margin: 14px 0;
    border-radius: 0 8px 8px 0;
    font-size: 9.5pt;
  }

  .callout-box.tip {
    background: #EFF6FF;
    border-left-color: #2563EB;
  }

  .callout-box.warning {
    background: #FFFBEB;
    border-left-color: #D97706;
  }

  .callout-title {
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
    font-size: 9.5pt;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }

  th {
    background: #F1F5F9;
    color: #0F172A;
    font-weight: 700;
    text-align: left;
    padding: 8px 10px;
    border: 1px solid #CBD5E1;
  }

  td {
    padding: 7px 10px;
    border: 1px solid #E2E8F0;
    vertical-align: top;
  }

  tr:nth-child(even) td {
    background: #F8FAFC;
  }

  .badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 7.5pt;
    font-weight: 700;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .badge-green { background: #DCFCE7; color: #15803D; }
  .badge-blue { background: #E0F2FE; color: #0369A1; }
  .badge-amber { background: #FEF3C7; color: #B45309; }
  .badge-red { background: #FFE4E6; color: #BE123C; }

  .toc-list {
    list-style: none;
    padding-left: 0;
  }

  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px dotted #CBD5E1;
    font-size: 9.5pt;
  }

  .toc-title {
    font-weight: 600;
    color: #0F172A;
  }

  .toc-desc {
    color: #64748B;
    font-size: 8.5pt;
    display: block;
    margin-top: 2px;
  }

  .step-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    page-break-inside: avoid;
  }

  .step-number {
    display: inline-block;
    width: 22px;
    height: 22px;
    background: #16A34A;
    color: #FFFFFF;
    border-radius: 50%;
    text-align: center;
    line-height: 22px;
    font-weight: 700;
    font-size: 8.5pt;
    margin-right: 6px;
  }

  .code-pill {
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 1px 5px;
    font-family: Consolas, Monaco, monospace;
    font-size: 8.5pt;
    color: #0F172A;
  }
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- COVER PAGE -->
<!-- ========================================================================= -->
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-badge">National Agricultural Intelligence Platform · Malawi</div>
    <div class="cover-title">FarmPulse Malawi</div>
    <div class="cover-subtitle">Comprehensive Official User Manual & Operational Field Handbook</div>
    <p style="font-size: 10pt; color: #334155; max-width: 90%;">
      A complete, step-by-step practical guide to planning crops, mastering weather risk, tracking national market prices, adopting satellite precision farming, and shielding harvests across Malawi.
    </p>
  </div>

  <div class="cover-meta-grid">
    <div class="meta-item">
      <strong>Target Audience</strong>
      <span>Commercial Smallholders, Estate Agronomists, Extension Officers, Agricultural Cooperatives, Financial Lenders.</span>
    </div>
    <div class="meta-item">
      <strong>Institutional Register</strong>
      <span>Ministry of Agriculture Standards (MWK, Hectares, 50kg Bags, Metric Tons).</span>
    </div>
    <div class="meta-item">
      <strong>National Telemetry Feeds</strong>
      <span>DCCMS Weather Stations, AMIS Commodity Trading Hubs, Sentinel-2 Optical & Radar Earth Observation.</span>
    </div>
    <div class="meta-item">
      <strong>Accessibility Standards</strong>
      <span>Bilingual English & Chichewa, Dual Forest/Sunlight Theme, Last-Mile USSD *384# Access.</span>
    </div>
  </div>

  <div class="cover-footer">
    <div>FarmPulse Agricultural Intelligence System · Version 3.9 (Production Release)</div>
    <div>Lilongwe & Blantyre, Republic of Malawi</div>
  </div>
</div>

<!-- ========================================================================= -->
<!-- TABLE OF CONTENTS -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Table of Contents</h1>
  <p style="color: #64748B; font-size: 9pt;">This manual covers every feature, screen, calculation, and workflow available in FarmPulse.</p>

  <ul class="toc-list">
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 1: Introducing FarmPulse Malawi</span>
        <span class="toc-desc">The core agricultural challenge, system philosophy, three foundational pillars, and standard Malawian units.</span>
      </div>
      <div>Section 1</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 2: Account Creation, Farm Setup & Navigation</span>
        <span class="toc-desc">Registering, topbar controls, Sunlight/Forest themes, audio advisories, and building your farm profile.</span>
      </div>
      <div>Section 2</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 3: The Executive Agricultural Dashboard</span>
        <span class="toc-desc">Hero greeting, live price ticker, farm KPIs, and the interactive National Agromet & Market Flow Radar.</span>
      </div>
      <div>Section 3</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 4: Climate Intelligence & Planting Window Engine</span>
        <span class="toc-desc">14-day DCCMS forecasts, 25mm planting trigger, historical 10-year agromet baselines, and dry-spell risk.</span>
      </div>
      <div>Section 4</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 5: Market Intelligence & Highway Price Arbitrage</span>
        <span class="toc-desc">5 trading hubs (Limbe, Mchesi, Mzuzu, Luchenza, Kasungu), farmgate vs wholesale spreads, and transport profits.</span>
      </div>
      <div>Section 5</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 6: Crop Planner & Enterprise Simulation</span>
        <span class="toc-desc">Step-by-step land & cash allocation, 3 automated strategies, input budgeting, and the One-Click Season Execution Bridge.</span>
      </div>
      <div>Section 6</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 7: Risk Analysis & The Stress Scenario Simulator</span>
        <span class="toc-desc">Simulating drought, market crashes, and fertilizer inflation; farm health grading (A+ to F); break-even price.</span>
      </div>
      <div>Section 7</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 8: My Farm, Plot Tracking & Season Review</span>
        <span class="toc-desc">Active plot management, multi-year yield ledgers, and end-of-season planned vs actual post-mortems.</span>
      </div>
      <div>Section 8</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 9: Satellite Field Twin & Variable-Rate Prescriptions</span>
        <span class="toc-desc">Sentinel-2 NDVI vigor, SAR moisture, virtual sampling, and saving MWK 126,000 on fertilizer through micro-zoning.</span>
      </div>
      <div>Section 9</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 10: Last-Mile USSD *384# Feature-Phone Terminal</span>
        <span class="toc-desc">Zero-data access for farmers without smartphones, interactive Nokia 3310 simulator, and complete menu directory.</span>
      </div>
      <div>Section 10</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 11: Parametric Weather-Index Crop Insurance</span>
        <span class="toc-desc">Zero-adjuster satellite insurance, the 14-day dry-spell trigger, and automated mobile money payouts (Airtel/TNM).</span>
      </div>
      <div>Section 11</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 12: Mlimi AI Agricultural Advisor (Bilingual English/Chichewa)</span>
        <span class="toc-desc">AI diagnostic engine for Fall Armyworm, rosette virus, fertilizer timing, and natural voice/chat extension.</span>
      </div>
      <div>Section 12</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 13: Offline Progressive Web App (PWA) & Data Export</span>
        <span class="toc-desc">Installing FarmPulse on mobile devices, offline service workers, and exporting farm records to CSV/JSON.</span>
      </div>
      <div>Section 13</div>
    </li>
    <li class="toc-item">
      <div>
        <span class="toc-title">Chapter 14: Glossary of Technical, Agronomic & Chichewa Terms</span>
        <span class="toc-desc">Clear definitions of institutional terminology, fertilizer formulations, satellite metrics, and Chichewa vocabulary.</span>
      </div>
      <div>Section 14</div>
    </li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 1 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 1: Introducing FarmPulse Malawi</h1>
  
  <h2>1.1 The Challenge Facing Malawian Agriculture</h2>
  <p>
    For decades, farming in Malawi has been governed by guesswork and vulnerability. Over 80% of Malawians rely on agriculture, yet farmers routinely encounter four severe obstacles:
  </p>
  <ul>
    <li><strong>Unpredictable Weather:</strong> Delayed onset of rains, erratic rainfall, and mid-season dry spells caused by climate change lead to false planting starts and burnt seed.</li>
    <li><strong>Market Exploitation:</strong> Farmers sell to informal middlemen (vendors) at farmgate prices 30% to 50% below fair market value because they lack live price transparency in major regional trading hubs like Limbe and Mchesi.</li>
    <li><strong>Suboptimal Crop Allocation:</strong> Farmers allocate their land without calculating crop-by-crop gross margins, operating costs, or break-even prices, leading to severe cash losses when input prices rise.</li>
    <li><strong>The Digital Divide:</strong> Most digital farming tools require expensive smartphones, mobile broadband bundles, or English fluency, locking out the vast majority of rural smallholders.</li>
  </ul>

  <h2>1.2 The FarmPulse Solution</h2>
  <p>
    <strong>FarmPulse Malawi</strong> is a purpose-built National Agricultural Intelligence Platform. It bridges the gap between high-level satellite Earth Observation, institutional weather stations (DCCMS), national commodity price feeds (AMIS), and the farmer on the ground.
  </p>
  <p>
    FarmPulse operates on three core pillars:
  </p>
  <ol>
    <li><strong>Climate Intelligence:</strong> Tells you exactly when to plant, how much rain is coming over 14 days, and whether a dry spell threatens your crop.</li>
    <li><strong>Market Intelligence:</strong> Shows live commodity prices across 5 major Malawian hubs and calculates whether hiring transport to sell in town will make you more profit than selling at your farm gate.</li>
    <li><strong>Enterprise Crop Planning:</strong> Generates optimized farm plans that balance household food security (Maize) with cash crop profits (Groundnuts, Soya, Beans, Rice), backed by detailed input budgets and one-click execution.</li>
  </ol>

  <h2>1.3 Standard Malawian Units & Currency</h2>
  <p>
    To ensure seamless relevance to Malawian institutions, banks, extension workers, and farmers, FarmPulse strictly adheres to official national agricultural measurements:
  </p>
  <table>
    <thead>
      <tr>
        <th>Measurement Type</th>
        <th>Standard Unit</th>
        <th>Practical Malawian Conversion</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Land Area</strong></td>
        <td>Hectares (ha)</td>
        <td>1 hectare (ha) = 2.47 acres = 10,000 square meters. A typical smallholder farm is 1.0 to 2.5 ha.</td>
      </tr>
      <tr>
        <td><strong>Currency</strong></td>
        <td>Malawi Kwacha (MWK)</td>
        <td>All budgets, market prices, fertilizer costs, and profit projections are calculated in MWK.</td>
      </tr>
      <tr>
        <td><strong>Commodity Volumes</strong></td>
        <td>50kg Bags / Metric Tons</td>
        <td>1 standard bag = 50 kg. 20 bags = 1.0 Metric Ton (1,000 kg). Prices are displayed per kg and per 50kg bag.</td>
      </tr>
      <tr>
        <td><strong>Fertilizer Dosing</strong></td>
        <td>Bags / Practical Caps</td>
        <td>Standard 50kg bags of Urea, CAN, or 23:21:0+4S. Practical dosing uses local measures (e.g. 1 Coca-Cola bottle cap = 5g).</td>
      </tr>
    </tbody>
  </table>

  <div class="callout-box">
    <div class="callout-title">Zero Guesswork Rule</div>
    Every recommendation, budget, and risk calculation in FarmPulse is rooted in real historical data, live agrometeorological sensors, and verified market surveys—never arbitrary estimates.
  </div>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 2 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 2: Account Creation, Farm Setup & Navigation</h1>

  <h2>2.1 Registering and Logging In</h2>
  <p>
    FarmPulse provides secure user authentication to keep your farm data confidential:
  </p>
  <ul>
    <li>To access the platform, navigate to the web address provided by your administrator or extension office.</li>
    <li>Click <strong>Register</strong> if you are a new farmer, or enter your username and password on the <strong>Login</strong> page.</li>
    <li>Once authenticated, your active farm profile and previous plans are loaded automatically.</li>
  </ul>

  <h2>2.2 Topbar Controls & Tools</h2>
  <p>
    The top navigation bar is accessible on every page and provides quick access to vital operational controls:
  </p>
  <ul>
    <li><strong>Global Search (<span class="code-pill">/</span> key):</strong> Instantly search crops, simulation plans, past plantings, districts, and commodity markets by typing a keyword.</li>
    <li><strong>Malawi Standard Time Clock:</strong> Displays live Central Africa Time (CAT, UTC+2). Agromet predictions and market prices sync to this clock.</li>
    <li><strong>Telemetry Connection Pill:</strong> Shows a green indicator (<span class="badge badge-green">Live Connected AMIS/DCCMS</span>) confirming active data streams from the Ministry of Agriculture and Meteorological Services.</li>
    <li><strong>Theme Selector (Sunlight / Forest):</strong> 
      <ul>
        <li><strong>Forest Mode:</strong> Deep emerald and midnight green theme designed for low-light indoor review, evening planning, and battery conservation.</li>
        <li><strong>Sunlight Mode:</strong> High-contrast paper-white cards with deep charcoal text and emerald highlights, engineered for high-glare readability under bright outdoor Malawian sunlight.</li>
      </ul>
    </li>
    <li><strong>Audio Advisory Pill (<span class="badge badge-blue">Audio Advisory</span>):</strong> Click to hear audio narrations of your current farm status in English or Chichewa. Perfect for oral communication in the field.</li>
    <li><strong>Demo Data Pill:</strong> Allows extension officers, instructors, and evaluators to quickly load pre-configured realistic Malawian farms (e.g. Chitukuko Farm, 2.5 ha).</li>
    <li><strong>User Profile & Settings Menu:</strong> View your username, farm profile shortcut, unit preferences, and logout action.</li>
  </ul>

  <h2>2.3 Setting Up Your Farm Profile</h2>
  <p>
    Your Farm Profile forms the foundation of all crop plans and climate alerts. Navigate to <strong>My Farm → Edit Farm</strong> to configure:
  </p>
  <div class="step-card">
    <span class="step-number">1</span> <strong>Farm Name & Location:</strong> Name your farm (e.g., <em>Chitukuko Farm</em>) and select your District (e.g., Blantyre, Lilongwe, Kasungu, Mzimba). This links your farm to the nearest DCCMS weather station.
  </div>
  <div class="step-card">
    <span class="step-number">2</span> <strong>Enterprise Land Area:</strong> Enter total farm land in hectares (e.g., 2.5 ha) and currently cultivated land.
  </div>
  <div class="step-card">
    <span class="step-number">3</span> <strong>Soil & Irrigation Characteristics:</strong> Choose your predominant soil type (Sandy Loam, Clay Loam, Silt Loam) and water regime (Rain-Fed or Irrigated via solar drip, treadle pump, or canal).
  </div>
  <div class="step-card">
    <span class="step-number">4</span> <strong>Available Labour & Seasonal Budget:</strong> Specify household and hired workers available for field work, plus your total cash operating budget in MWK (e.g., MWK 1,200,000).
  </div>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 3 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 3: The Executive Agricultural Dashboard</h1>

  <h2>3.1 Overview of the Dashboard</h2>
  <p>
    The Overview Dashboard (<span class="code-pill">/</span>) is the central command center of FarmPulse. When you open the platform, it presents an immediate executive summary of your farm's health, incoming weather alerts, market movements, and geographic context.
  </p>

  <h2>3.2 Hero Banner & Action Shortcuts</h2>
  <p>
    The top of the dashboard displays the <strong>Hero Banner</strong>:
  </p>
  <ul>
    <li><strong>Greeting & Monitoring Status:</strong> Identifies you, your active farm, land size, and current season status (e.g., <em>"Monitoring Chitukuko Farm (2.5 ha). Ready for seasonal planning."</em>).</li>
    <li><strong>Generate Crop Plan Button:</strong> Primary call-to-action that launches the 4-step Crop Planner to build an optimized seasonal strategy.</li>
    <li><strong>Seasonal Risk Analysis Button:</strong> Direct link to the Monte Carlo scenario simulator to test your farm against drought and price drops.</li>
  </ul>

  <h2>3.3 Quick Navigation Cards</h2>
  <p>
    Four fast-track cards allow single-click access to core operational modules:
  </p>
  <ul>
    <li><strong>Create Crop Plan:</strong> View and compare 3 computer-generated land allocation strategies.</li>
    <li><strong>Analyse Climate:</strong> Inspect 14-day rainfall volume, temperature highs, and heat stress.</li>
    <li><strong>Market Prices:</strong> Review price spreads between farmgate vendors and wholesale depots.</li>
    <li><strong>Farm History:</strong> Access multi-year records of past yields, harvests, and gross margins.</li>
  </ul>

  <h2>3.4 Live National Commodity Price Ticker</h2>
  <p>
    Below the action cards is a continuously scrolling live price strip. It updates automatically from the Agricultural Market Information System (AMIS) and displays current wholesale prices and 24-hour percentage changes:
  </p>
  <ul>
    <li><strong>Common Beans:</strong> e.g., MWK 1,720 / kg (+2.4%)</li>
    <li><strong>Groundnuts CG7:</strong> e.g., MWK 1,240 / kg (+3.3%)</li>
    <li><strong>Hybrid Maize:</strong> e.g., MWK 520 / kg (+4.0%)</li>
    <li><strong>Kilombero Rice:</strong> e.g., MWK 1,580 / kg (+2.6%)</li>
    <li><strong>Soya Tikolore:</strong> e.g., MWK 890 / kg (+1.8%)</li>
  </ul>

  <h2>3.5 Farm Performance KPI Cards</h2>
  <p>
    Four summary cards keep your farm's core constraints visible at all times:
  </p>
  <ul>
    <li><strong>Enterprise Land:</strong> Total land vs. cultivated land (e.g., 2.5 ha total, 2.0 ha cultivated).</li>
    <li><strong>Operating Budget:</strong> Cash allocated for the current cropping season (e.g., MWK 1,200,000).</li>
    <li><strong>Available Labour:</strong> Total active family and seasonal workers (e.g., 4 persons).</li>
    <li><strong>Water & Soil:</strong> Water regime and soil profile (e.g., Rain-Fed / Loam).</li>
  </ul>

  <h2>3.6 National Agromet & Market Flow Radar</h2>
  <p>
    An interactive geospatial map powered by Leaflet:
  </p>
  <ul>
    <li><strong>Weather Stations (8 DCCMS Locations):</strong> Marked with blue pins (e.g., Chichiri, Chileka, KIA Lilongwe, Mzuzu, Salima, Kasungu). Clicking reveals current rainfall and temperature.</li>
    <li><strong>Agricultural Trading Hubs (5 AMIS Markets):</strong> Marked with green pins (Limbe, Mchesi, Mzuzu, Luchenza, Kasungu). Clicking displays commodity buying prices.</li>
    <li><strong>Highway Arbitrage Corridors:</strong> Dashed green lines tracing the M1 national highway network. Clicking shows estimated transport costs and net price advantage between regions.</li>
    <li><strong>Chichewa Audio Advisory:</strong> Click the voice button to listen to a full Chichewa audio explanation of national weather and price flows.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 4 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 4: Climate Intelligence & Planting Window Engine</h1>

  <h2>4.1 The Importance of Agrometeorology in Malawi</h2>
  <p>
    Malawian agriculture is heavily rain-fed. Planting too early on a "false start" of rain causes seeds to germinate and then scorch when dry weather returns, wiping out scarce seed capital. Planting too late shortens the growing season and cuts yields in half. FarmPulse removes this risk.
  </p>

  <h2>4.2 The 14-Day DCCMS Weather Forecast</h2>
  <p>
    FarmPulse pulls high-resolution agrometeorological telemetry from the Department of Climate Change and Meteorological Services (DCCMS):
  </p>
  <ul>
    <li><strong>Daily Precipitation (mm):</strong> Expected rainfall volume in millimeters.</li>
    <li><strong>Rain Probability (%):</strong> Statistical confidence of rainfall occurring on each day.</li>
    <li><strong>Temperature Extremes (°C):</strong> Daily minimum and maximum temperatures.</li>
    <li><strong>Estimated Soil Moisture Index (%):</strong> Calculated topsoil saturation based on recent rainfall and solar evaporation.</li>
  </ul>

  <h2>4.3 The Critical Planting Window Engine</h2>
  <p>
    FarmPulse implements the scientific recommendation of the Ministry of Agriculture and CIMMYT for safe maize and legume sowing:
  </p>
  <div class="callout-box">
    <div class="callout-title">The 25mm Cumulative Sowing Rule</div>
    Do not sow seed until your district records at least <strong>25 to 30 millimeters of cumulative rainfall across three consecutive days</strong>, with moist soil penetrating at least 15 cm deep.
  </div>
  <p>
    The platform dynamically evaluates this threshold:
  </p>
  <ul>
    <li><span class="badge badge-amber">Hold Sowing — Inadequate Moisture:</span> Indicates rainfall has been sporadic (&lt; 20mm). Planting now risks losing certified hybrid seed.</li>
    <li><span class="badge badge-green">Optimal Sowing Window Active:</span> Indicates cumulative rainfall has crossed 28mm and follow-up rains are forecast. Farmers should immediately plant.</li>
    <li><span class="badge badge-red">Late Sowing Alert:</span> Indicates the season is advancing rapidly. Recommends switching to ultra-early maturing varieties (e.g. SC 419 or Kanyani).</li>
  </ul>

  <h2>4.4 Dry Spell & Heatwave Risk Matrix</h2>
  <p>
    During the critical flowering and grain-filling stages (usually January and February), a dry spell lasting longer than 10 days causes catastrophic yield loss. FarmPulse continuously forecasts:
  </p>
  <ul>
    <li><strong>Mid-Season Dry Spell Probability:</strong> The statistical chance of 10+ consecutive dry days.</li>
    <li><strong>Heat Stress Days:</strong> Days where ambient temperature exceeds 32°C, which impairs pollen viability in maize.</li>
    <li><strong>Agronomic Mitigation Actions:</strong> When risk is high, FarmPulse advises farmers to apply organic mulch along furrows, dig tied ridges to harvest water, and ensure weeding is completed early to eliminate weed competition for moisture.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 5 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 5: Market Intelligence & Highway Price Arbitrage</h1>

  <h2>5.1 Why Price Transparency Matters</h2>
  <p>
    Smallholder farmers frequently lose up to half their potential income because they sell to itinerant vendors at the farm gate who exploit the farmer's lack of price information. FarmPulse gives every farmer institutional-grade market visibility.
  </p>

  <h2>5.2 The 5 Monitored National Trading Hubs</h2>
  <p>
    FarmPulse tracks official price returns from Malawi's five major commercial hubs:
  </p>
  <table>
    <thead>
      <tr>
        <th>Market Hub</th>
        <th>Region</th>
        <th>Market Role & Primary Demand</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Limbe Hub (Blantyre)</strong></td>
        <td>Southern</td>
        <td>Major urban deficit consumer market; highest average prices for maize, common beans, and pigeon peas.</td>
      </tr>
      <tr>
        <td><strong>Mchesi Market (Lilongwe)</strong></td>
        <td>Central</td>
        <td>Central national aggregator; massive demand for soya, groundnuts, and hybrid maize.</td>
      </tr>
      <tr>
        <td><strong>Mzuzu Main Market</strong></td>
        <td>Northern</td>
        <td>Northern transit terminal; strong market for Kilombero rice, beans, and coffee.</td>
      </tr>
      <tr>
        <td><strong>Luchenza Hub</strong></td>
        <td>Southern</td>
        <td>Key agricultural trading depot linking Thyolo tea belts and Mulanje smallholders.</td>
      </tr>
      <tr>
        <td><strong>Kasungu Trading Centre</strong></td>
        <td>Central</td>
        <td>Primary agricultural production hub; high volumes of groundnuts, soya, and maize.</td>
      </tr>
    </tbody>
  </table>

  <h2>5.3 The Three-Tier Pricing Structure</h2>
  <p>
    For every monitored commodity, FarmPulse shows three distinct price levels:
  </p>
  <ol>
    <li><strong>Farmgate Price:</strong> What local buyers and vendors pay when purchasing directly at the village level.</li>
    <li><strong>Wholesale Price:</strong> What registered depots, aggregators, and millers pay for minimum 50kg bag deliveries in commercial centers.</li>
    <li><strong>Retail Price:</strong> What consumers pay in urban retail open-air stalls and grocery shops.</li>
  </ol>

  <h2>5.4 Highway Transport Arbitrage Calculator</h2>
  <p>
    Should you sell at your farm gate or hire a 3-ton truck to transport your harvest to Limbe or Mchesi? FarmPulse answers this mathematically:
  </p>
  <ul>
    <li>Enter your harvest volume in 50kg bags (e.g., 50 bags of maize = 2,500 kg).</li>
    <li>Select your origin district and destination market.</li>
    <li>FarmPulse calculates total distance, diesel fuel requirements, truck hire fees, and bag offloading charges.</li>
    <li><strong>Net Arbitrage Profit:</strong> FarmPulse subtracts total transport costs from the urban wholesale revenue. If the net gain exceeds farmgate earnings by more than 15%, it recommends transporting; otherwise, it advises selling locally to avoid logistics risk.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 6 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 6: Crop Planner & Enterprise Simulation</h1>

  <h2>6.1 What is the Crop Planner?</h2>
  <p>
    The <strong>Crop Planner</strong> (<span class="code-pill">/planner/input/</span>) is FarmPulse's intelligent mathematical engine. It takes your farm's available land, cash budget, soil type, and labor capacity, and generates three complete, balanced cropping strategies tailored specifically to Malawian agro-ecological zones.
  </p>

  <h2>6.2 Step-by-Step Planning Workflow</h2>

  <div class="step-card">
    <span class="step-number">1</span> <strong>Define Constraints:</strong> Enter your total available land for the season (e.g. 2.5 ha), cash budget (e.g. MWK 1,200,000), family workers (e.g. 4 persons), and soil classification.
  </div>

  <div class="step-card">
    <span class="step-number">2</span> <strong>Select Primary Farm Priority:</strong> Choose between three distinct farm objectives:
    <ul>
      <li><em>Food Security First:</em> Guarantees your family has enough maize to eat for the entire 12-month calendar year before allocating land to cash crops.</li>
      <li><em>Commercial Profit Maximizer:</em> Allocates the maximum possible land to high-gross-margin cash crops (Soya, Groundnuts, Beans) to maximize net cash return in MWK.</li>
      <li><em>Climate-Resilient Hybrid:</em> Spreads risk across drought-tolerant legumes and early-maturing cereals, safeguarding working capital against mid-season dry spells.</li>
    </ul>
  </div>

  <div class="step-card">
    <span class="step-number">3</span> <strong>Review Enterprise Budgets:</strong> FarmPulse details every anticipated cost per crop per hectare:
    <ul>
      <li>Certified seed requirement (kg/ha and cost in MWK).</li>
      <li>Basal fertilizer (23:21:0+4S) bags and cost.</li>
      <li>Top-dressing fertilizer (Urea / CAN) bags and cost.</li>
      <li>Crop protection pesticides and herbicides.</li>
      <li>Casual labor allowance (land prep, planting, weeding, harvesting).</li>
    </ul>
  </div>

  <div class="step-card">
    <span class="step-number">4</span> <strong>Compare Outcome Projections:</strong> Review projected harvest yield (bags and tons), gross revenue, total production expenses, net gross margin, and Return on Investment (ROI %).
  </div>

  <h2>6.3 The One-Click Plan-to-Season Execution Bridge</h2>
  <p>
    A simulation is useless if it stays locked in a computer. FarmPulse features an automated execution bridge:
  </p>
  <ul>
    <li>On the Plan Detail page, click the green <strong>"Execute Plan (Start Season)"</strong> button.</li>
    <li>FarmPulse instantly translates the simulated plan into an active farming season.</li>
    <li>It automatically creates physical plot records in <strong>My Farm</strong> for each allocated crop, logs target planting dates, reserves your operating budget, and schedules key agronomic calendar milestones (e.g. first weeding at 21 DAP, top-dressing at 35 DAP).</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 7 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 7: Risk Analysis & The Stress Scenario Simulator</h1>

  <h2>7.1 Why Stress-Test a Farm?</h2>
  <p>
    In agriculture, plans rarely go exactly as expected. Rains may be 30% below normal, fertilizer prices may double, or market prices may crash due to an export ban. The <strong>Scenario Simulator</strong> (<span class="code-pill">/planner/scenarios/</span>) allows you to "crash-test" your farm before spending a single Kwacha.
  </p>

  <h2>7.2 Interactive Shock Sliders</h2>
  <p>
    The simulator provides three dynamic shock controls that you can adjust in real time:
  </p>
  <ul>
    <li><strong>Rainfall Deficit Slider (-50% to +50%):</strong> Simulate mild dry spells (-15%) up to severe drought (-35% or worse). Watch how cereal yields plummet while legumes retain vigor.</li>
    <li><strong>Market Price Shock Slider (-40% to +40%):</strong> Simulate a bumper crop market slump (-25%) or a favorable regional price surge (+30%).</li>
    <li><strong>Fertilizer & Input Price Shock Slider (-20% to +60%):</strong> Simulate international fertilizer price spikes and see how they impact your cash flow and net profitability.</li>
  </ul>

  <h2>7.3 Farm Health Grade (A+ to F)</h2>
  <p>
    As you adjust the shock sliders, FarmPulse dynamically recalculates your <strong>Farm Health Grade</strong>:
  </p>
  <table>
    <thead>
      <tr>
        <th>Grade</th>
        <th>Status</th>
        <th>Financial & Agronomic Meaning</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="badge badge-green">Grade A+ / A</span></td>
        <td>Highly Resilient</td>
        <td>Farm generates healthy profits even under combined drought and market shocks. Ample liquidity.</td>
      </tr>
      <tr>
        <td><span class="badge badge-green">Grade B</span></td>
        <td>Moderate Buffer</td>
        <td>Farm absorbs normal seasonal variations with positive net income. Minor cash flow pressure.</td>
      </tr>
      <tr>
        <td><span class="badge badge-amber">Grade C</span></td>
        <td>Vulnerable</td>
        <td>Farm barely breaks even under shocks. Working capital is depleted; emergency borrowing may be needed.</td>
      </tr>
      <tr>
        <td><span class="badge badge-red">Grade D / F</span></td>
        <td>Severe Distress</td>
        <td>Farm suffers catastrophic losses. Operating capital is wiped out; high risk of loan default.</td>
      </tr>
    </tbody>
  </table>

  <h2>7.4 Break-Even Price Calculation</h2>
  <p>
    For every crop in your plan, the simulator displays the <strong>Break-Even Selling Price (MWK/kg)</strong>. This is the absolute minimum price you must receive to recover your production costs.
  </p>
  <div class="callout-box">
    <div class="callout-title">The Golden Rule of Selling</div>
    Never accept a vendor's offer below your break-even price. If market prices are currently below break-even, FarmPulse recommends storing your grain using PICS hermetic bags and waiting for seasonal price appreciation in July/August.
  </div>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 8 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 8: My Farm, Plot Tracking & Season Review</h1>

  <h2>8.1 Managing Active Farm Plots</h2>
  <p>
    The <strong>My Farm</strong> module (<span class="code-pill">/farms/my-farm/</span>) displays your farm's physical layout:
  </p>
  <ul>
    <li><strong>Plot Inventory:</strong> See every subdivided plot on your farm (e.g. Plot 1: 1.5 ha Maize; Plot 2: 0.6 ha Groundnuts; Plot 3: 0.4 ha Soya).</li>
    <li><strong>Soil Profile by Plot:</strong> Specific soil textures, slope, and drainage conditions for each parcel.</li>
    <li><strong>Planting Date Tracking:</strong> Records the exact day seed entered the ground to drive automated Days After Planting (DAP) alerts.</li>
  </ul>

  <h2>8.2 Farm History Ledger</h2>
  <p>
    The <strong>Farm History</strong> view (<span class="code-pill">/farms/history/</span>) functions as your permanent digital farm ledger:
  </p>
  <ul>
    <li>Stores historical crop yields (50kg bags/ha) achieved across past seasons (e.g. 2023/24, 2024/25).</li>
    <li>Records actual sales prices achieved and inputs applied.</li>
    <li>Enables multi-year soil fertility and crop rotation tracking (ensuring legumes rotate with cereals to replenish soil nitrogen).</li>
  </ul>

  <h2>8.3 The End-of-Season Review Engine</h2>
  <p>
    When harvesting is complete, navigate to <strong>Season Review</strong> (<span class="code-pill">/farms/season-review/</span>):
  </p>
  <ul>
    <li><strong>Planned vs. Actual Comparison:</strong> Compare your pre-season target harvest against actual bags weighed in your barn.</li>
    <li><strong>Budget Variance Analysis:</strong> Highlights where you overspent (e.g. extra weeding labor) and where you saved money.</li>
    <li><strong>Agronomic Post-Mortem:</strong> Document key lessons learned (e.g., <em>"Groundnuts planted on Nov 25 yielded 40% higher than those planted on Dec 18 due to early dry-spell escape"</em>). These lessons refine your next season's plan.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 9 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 9: Satellite Field Twin & Variable-Rate Prescriptions</h1>

  <h2>9.1 Orbital Earth Observation for Malawian Smallholders</h2>
  <p>
    The <strong>Satellite Field Twin</strong> (<span class="code-pill">/satellite/</span>) connects your cadastral farm polygon to the European Space Agency's <strong>Sentinel-2</strong> multi-spectral optical satellites and <strong>Sentinel-1</strong> Synthetic Aperture Radar (SAR). Every 5 days, a satellite passes over your farm, capturing 10-meter resolution images of your crops.
  </p>

  <h2>9.2 Multi-Spectral Sensor Layers</h2>
  <p>
    Use the top layer buttons to switch between three satellite views:
  </p>
  <ul>
    <li><strong>True Color (RGB):</strong> Standard photographic imagery showing your field exactly as it looks from orbit.</li>
    <li><strong>Sentinel-2 NDVI Canopy Vigor:</strong> Normalized Difference Vegetation Index. Measures near-infrared chlorophyll reflectance on a scale from 0.0 to 1.0. Dense, green, healthy maize shows bright green (0.65–0.85); yellowing or stunted crops show amber/red (&lt; 0.45).</li>
    <li><strong>SAR Topsoil Dielectric Moisture:</strong> Radar sensor that penetrates clouds and canopy to measure volumetric moisture percentage in the top 0–5 cm of soil.</li>
  </ul>

  <h2>9.3 Virtual Spectral Sampler</h2>
  <p>
    Click anywhere within your field polygon on the map. The Virtual Sampler instantly inspects the 10-meter pixel:
  </p>
  <ul>
    <li>Displays exact latitude and longitude.</li>
    <li>Shows localized pixel NDVI score and moisture percentage.</li>
    <li>Provides an instant agronomic recommendation (e.g., <em>"Noticeable nitrogen/moisture deficiency. Recommend targeted side-dressing."</em>).</li>
  </ul>

  <h2>9.4 Variable-Rate Input Prescription (VRA) & Fertilizer Economics</h2>
  <p>
    The greatest commercial benefit of satellite intelligence is eliminating wasteful fertilizer over-application. Traditional Malawian practice is "blanket broadcasting"—applying 2 bags of Urea per hectare uniformly across the entire farm. This wastes fertilizer in fertile areas and under-fertilizes poor soil.
  </p>
  <p>
    FarmPulse partitions your farm into <strong>three distinct vegetative management zones</strong>:
  </p>
  <table>
    <thead>
      <tr>
        <th>Field Zone</th>
        <th>Area & Vigor</th>
        <th>Blanket Practice</th>
        <th>Satellite VRA Rate</th>
        <th>Net Savings & Agronomic Dosing Instruction</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>North Quadrant</strong></td>
        <td>1.13 ha (45%)<br><span class="badge badge-green">NDVI 0.72 (Optimal)</span></td>
        <td>2.25 bags (112.5 kg)<br>MWK 162,000</td>
        <td><strong>0.90 bags (45.0 kg)</strong><br>MWK 64,800</td>
        <td><strong>Saves 1.35 bags (MWK 97,200).</strong> High natural fertility; reduce top-dressing by 60% to prevent stalk lodging.<br><em>Dose: 1 Coca-Cola bottle cap (5g) per 2 maize stations.</em></td>
      </tr>
      <tr>
        <td><strong>Central Swale</strong></td>
        <td>0.88 ha (35%)<br><span class="badge badge-green">NDVI 0.65 (Good)</span></td>
        <td>1.75 bags (87.5 kg)<br>MWK 126,000</td>
        <td><strong>1.75 bags (87.5 kg)</strong><br>MWK 126,000</td>
        <td><strong>Balanced (Standard).</strong> Optimal soil moisture retention in swale.<br><em>Dose: 1 full fertilizer cup (10g) per maize station at 35 DAP.</em></td>
      </tr>
      <tr>
        <td><strong>Southern Ridge</strong></td>
        <td>0.50 ha (20%)<br><span class="badge badge-amber">NDVI 0.42 (Stressed)</span></td>
        <td>1.00 bag (50.0 kg)<br>MWK 72,000</td>
        <td><strong>0.60 bag (30.0 kg)</strong><br>MWK 43,200</td>
        <td><strong>Saves 0.40 bag (MWK 28,800).</strong> Shallow ridge prone to leaching; heavy fertilizer scorches roots.<br><em>Dose: Half cup (5g) buried 5cm away, covered with organic mulch.</em></td>
      </tr>
    </tbody>
  </table>

  <div class="callout-box">
    <div class="callout-title">Total Financial Impact Across a 2.5 Hectare Farm</div>
    Blanket Approach: 5.00 bags (MWK 360,000)<br>
    Satellite VRA Approach: 3.25 bags (MWK 234,000)<br>
    <strong>Direct Capital Saved: 1.75 bags (87.5 kg) = MWK 126,000 net savings (-35.0% fertilizer expenditure) with equal or higher harvest yield!</strong>
  </div>

  <h2>9.5 Worker Extension & Dispatch Tools</h2>
  <ul>
    <li><strong>Interactive Price Recalculator:</strong> Change fertilizer formulation (Urea, CAN, 23:21:0+4S) or edit the bag price. All numbers recalculate live.</li>
    <li><strong>Copy USSD Note (<span class="code-pill">*384*77#</span>):</strong> Copies a compact summary to the clipboard, formatted for instant SMS or USSD transmission to field workers.</li>
    <li><strong>Print Field Slip:</strong> Formats a clean printable instruction sheet for farm laborers with physical measuring cup instructions.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 10 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 10: Last-Mile USSD *384# Feature-Phone Terminal</h1>

  <h2>10.1 Bridging the Digital Divide</h2>
  <p>
    Approximately 75% of Malawian farmers own basic 2G feature phones (such as basic Nokia, Tecno, or Itel handsets) with no smartphone screens, web browsers, or mobile internet bundles. To ensure zero-data accessibility, FarmPulse includes a full <strong>USSD Terminal Engine</strong> (<span class="code-pill">/ussd/</span>).
  </p>

  <h2>10.2 How USSD Works</h2>
  <p>
    A farmer dials the shortcode <strong>*384*77#</strong> on any GSM network (Airtel Malawi or TNM). A fast, interactive menu appears instantly on their screen with zero data charges.
  </p>

  <h2>10.3 The USSD Menu Directory</h2>
  <div class="step-card">
    <strong>1. Mitengo ya Mbewu (Market Prices):</strong>
    <p style="margin: 4px 0 0 0; color: #475569; font-size: 9pt;">
      Select crop (1. Chimanga/Maize, 2. Mtedza/Groundnuts, 3. Soya, 4. Nyemba/Beans). The system returns live wholesale and farmgate prices for the farmer's nearest market hub.
    </p>
  </div>
  <div class="step-card">
    <strong>2. Weather & Dry-Spell Alert:</strong>
    <p style="margin: 4px 0 0 0; color: #475569; font-size: 9pt;">
      Provides a 3-day rainfall prediction in millimeters and indicates whether planting conditions are safe.
    </p>
  </div>
  <div class="step-card">
    <strong>3. Break-Even Price Check:</strong>
    <p style="margin: 4px 0 0 0; color: #475569; font-size: 9pt;">
      Enter your planned harvest bags to receive your minimum selling price per bag, protecting you from vendor underpayment.
    </p>
  </div>
  <div class="step-card">
    <strong>4. Uphungu wa Ulimi (Agronomic Advisory):</strong>
    <p style="margin: 4px 0 0 0; color: #475569; font-size: 9pt;">
      Step-by-step Chichewa advice on Fall Armyworm scouting, fertilizer micro-dosing, and post-harvest drying.
    </p>
  </div>
  <div class="step-card">
    <strong>5. Insurance Shield Status:</strong>
    <p style="margin: 4px 0 0 0; color: #475569; font-size: 9pt;">
      Check policy status and verify whether the satellite drought trigger has been activated in your district.
    </p>
  </div>

  <h2>10.4 The Interactive Screen Simulator</h2>
  <p>
    On the FarmPulse web platform, an interactive Nokia 3310 phone interface simulates live USSD sessions. You can click the physical keypad buttons to test session handling, verify menu responses, and train extension agents on USSD navigation.
  </p>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 11 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 11: Parametric Weather-Index Crop Insurance</h1>

  <h2>11.1 The Failure of Traditional Crop Insurance</h2>
  <p>
    Traditional agricultural indemnity insurance fails smallholders. When a drought strikes, an insurance company must send an adjuster to visit thousands of remote villages, inspect dead fields, and manually assess claims. Administrative costs exceed premium revenues, claims take 6 to 12 months to pay, and smallholders are often rejected.
  </p>

  <h2>11.2 What is Parametric Insurance?</h2>
  <p>
    <strong>Parametric (Index) Insurance</strong> replaces subjective human loss adjusters with objective, verifiable satellite and agrometeorological triggers.
  </p>
  <div class="callout-box">
    <div class="callout-title">The Parametric Guarantee</div>
    Payouts are not tied to an adjuster's opinion. Payouts are triggered automatically when an objective pre-agreed scientific index is crossed (e.g. 14 consecutive dry days during flowering).
  </div>

  <h2>11.3 The FarmPulse Drought Trigger Protocol</h2>
  <ol>
    <li><strong>Policy Definition:</strong> A farmer insures 2.0 ha of Maize with a sum insured of MWK 400,000 for a modest premium (e.g. MWK 28,000, often subsidized by commercial off-takers or government programs).</li>
    <li><strong>Monitoring Window:</strong> Satellite rainfall and DCCMS telemetry are monitored between January 1 and February 28 (the sensitive tasseling and cob formation phase).</li>
    <li><strong>The Trigger Condition:</strong> If the station records <strong>14 consecutive days with daily rainfall &lt; 1.5 mm</strong>, the policy automatically transitions to <span class="badge badge-red">Drought Triggered</span>.</li>
    <li><strong>Automated Mobile Money Payout:</strong> Payout funds are disbursed directly into the farmer's mobile money wallet (Airtel Money or TNM Mpamba) within 48 to 72 hours, allowing the family to purchase food or re-plant fast-maturing crops without sliding into debt.</li>
  </ol>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 12 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 12: Mlimi AI Agricultural Advisor (Bilingual)</h1>

  <h2>12.1 An Expert Agronomist in Your Pocket</h2>
  <p>
    Most Malawian agricultural extension officers have an unmanageable ratio of 1 officer to 2,500 farming households. Farmers cannot get timely answers when pests appear. <strong>Mlimi AI</strong> (<span class="code-pill">/advisor/</span>) is FarmPulse's intelligent agronomic assistant, fluent in both English and Chichewa.
  </p>

  <h2>12.2 Diagnostic Knowledgebase</h2>
  <p>
    Mlimi AI is specialized in Malawian farming systems and provides immediate actionable diagnoses:
  </p>
  <ul>
    <li><strong>Fall Armyworm (<em>Mbozi ya dende</em>):</strong> Scouting methods (inspecting 20 consecutive plants in a 'W' pattern), identifying "windowpane" leaf damage, and applying safe controls (e.g. bio-rational neem leaf extracts, fine sand/ash in maize funnels, or registered insecticides like Emamectin Benzoate).</li>
    <li><strong>Groundnut Rosette Virus:</strong> Diagnosing stunted, bushy plants with mottled yellow leaves; managing the aphid vector through early planting and recommended row spacing (30cm between ridges, 10cm between plants).</li>
    <li><strong>Maize Streak Virus:</strong> Identifying yellow chlorotic streaks transmitted by leafhoppers; selecting tolerant hybrid seed.</li>
    <li><strong>Soil Acidity & CAN vs. Urea:</strong> Advising when to switch from Urea to Calcium Ammonium Nitrate (CAN) on acidic tea soils in Thyolo/Mulanje to prevent soil acidification.</li>
  </ul>

  <h2>12.3 How to Interact with Mlimi AI</h2>
  <p>
    Simply type your question in English or Chichewa into the chat box (e.g., <em>"Mbewu zanga zikusonyeza masamba achikasu, ndichite chiyani?"</em>). Mlimi AI analyzes your farm's active soil type, crop, and district, and replies with structured, practical advice tailored to local input availability.
  </p>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 13 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 13: Offline Progressive Web App & Data Export</h1>

  <h2>13.1 Offline Resilience in Rural Areas</h2>
  <p>
    Rural connectivity in Malawi is prone to network dropouts and load shedding. FarmPulse is built as a <strong>Progressive Web App (PWA)</strong>:
  </p>
  <ul>
    <li><strong>Installable App:</strong> In Google Chrome, Safari, or Microsoft Edge, click <strong>"Add to Home Screen"</strong> or <strong>"Install FarmPulse"</strong>. It installs as a lightweight standalone app on your phone, tablet, or PC without going through an app store.</li>
    <li><strong>Offline Caching:</strong> A background Service Worker caches all previously viewed plans, farm profiles, and crop budgets. Even if cellular internet cuts out completely in the field, your farm records and maps remain viewable.</li>
  </ul>

  <h2>13.2 Exporting Your Farm Data</h2>
  <p>
    You own your farm data. Navigate to <strong>Settings → Export Farm Data</strong> to export:
  </p>
  <ul>
    <li><strong>CSV / Excel Format:</strong> Detailed financial budgets, crop schedules, and multi-year yield ledgers ready for presentation to commercial banks, micro-finance lenders, or off-take buyers.</li>
    <li><strong>JSON Format:</strong> Complete digital backup of all cadastral polygons, scenario simulations, and sensor history.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- CHAPTER 14 -->
<!-- ========================================================================= -->
<div class="page-break">
  <h1>Chapter 14: Glossary of Technical, Agronomic & Chichewa Terms</h1>

  <table>
    <thead>
      <tr>
        <th>Term / Abbreviation</th>
        <th>Definition & Context</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>AMIS</strong></td>
        <td>Agricultural Market Information System of Malawi; operates under the Ministry of Agriculture to track commodity prices across major trading hubs.</td>
      </tr>
      <tr>
        <td><strong>DCCMS</strong></td>
        <td>Department of Climate Change and Meteorological Services; Malawi's national weather monitoring authority.</td>
      </tr>
      <tr>
        <td><strong>DAP</strong></td>
        <td>Days After Planting; the standard agronomic calendar measurement tracking crop age from seed emergence.</td>
      </tr>
      <tr>
        <td><strong>NDVI</strong></td>
        <td>Normalized Difference Vegetation Index; satellite measurement of near-infrared chlorophyll reflectance (0.0 to 1.0) indicating crop vigor.</td>
      </tr>
      <tr>
        <td><strong>SAR</strong></td>
        <td>Synthetic Aperture Radar; orbital microwave sensors (Sentinel-1) measuring soil moisture through clouds.</td>
      </tr>
      <tr>
        <td><strong>VRA</strong></td>
        <td>Variable-Rate Application; the practice of tailoring fertilizer doses to specific intra-field soil/canopy zones rather than blanket broadcasting.</td>
      </tr>
      <tr>
        <td><strong>Basal Dressing</strong></td>
        <td>Compound fertilizer applied at planting (typically 23:21:0+4S in Malawi) to stimulate root development.</td>
      </tr>
      <tr>
        <td><strong>Top Dressing</strong></td>
        <td>Nitrogenous fertilizer applied at 21 to 35 DAP (typically Urea 46% N or CAN 28% N) to promote vegetative growth.</td>
      </tr>
      <tr>
        <td><strong>PICS Bags</strong></td>
        <td>Purdue Improved Crop Storage bags; hermetic, chemical-free triple-layer storage bags protecting grain against weevils.</td>
      </tr>
      <tr>
        <td><strong>Mlimi</strong></td>
        <td>Chichewa for "Farmer" or "Cultivator".</td>
      </tr>
      <tr>
        <td><strong>Chimanga</strong></td>
        <td>Chichewa for "Maize", the staple food grain of Malawi.</td>
      </tr>
      <tr>
        <td><strong>Mtedza</strong></td>
        <td>Chichewa for "Groundnuts" / "Peanuts".</td>
      </tr>
      <tr>
        <td><strong>Mbozi ya dende</strong></td>
        <td>Chichewa for "Fall Armyworm" (<em>Spodoptera frugiperda</em>).</td>
      </tr>
      <tr>
        <td><strong>Uphungu wa Ulimi</strong></td>
        <td>Chichewa for "Agricultural Extension Advisory / Guidance".</td>
      </tr>
    </tbody>
  </table>

  <div style="margin-top: 40px; padding: 20px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; text-align: center;">
    <div style="font-weight: 800; color: #062B20; font-size: 11pt; margin-bottom: 4px;">End of Official User Manual</div>
    <div style="color: #64748B; font-size: 8.5pt;">FarmPulse Malawi · Agricultural Intelligence for a Climate-Resilient Nation</div>
  </div>
</div>

</body>
</html>
"""

def generate_pdf():
    html_path = os.path.abspath("FarmPulse_Malawi_Complete_User_Manual.html")
    pdf_path = os.path.abspath("FarmPulse_Malawi_Complete_User_Manual.pdf")

    print(f"Writing HTML manual to: {html_path}")
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
        print(f"SUCCESS: Generated PDF at {pdf_path} ({size_kb:.1f} KB)")
    else:
        print(f"Error: PDF generation failed. Return code: {result.returncode}")
        print("Stderr:", result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_pdf()
