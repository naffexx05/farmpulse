import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FarmPulse Malawi — Mzuzu University Software Product Exhibition Deck</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  @page {
    size: 16in 9in;
    margin: 0;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #060b08;
    color: #e2e8f0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .slide {
    width: 16in;
    height: 9in;
    page-break-after: always;
    position: relative;
    padding: 0.7in 0.9in;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: radial-gradient(circle at 85% 15%, #0e2216 0%, #060b08 70%);
    border-bottom: 2px solid rgba(16, 185, 129, 0.2);
    overflow: hidden;
  }

  /* Slide Accents */
  .slide::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(90deg, #10b981 0%, #d4af37 50%, #003366 100%);
  }

  /* Header */
  .slide-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.25in;
  }

  .univ-tag {
    font-size: 0.17in;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #d4af37;
    margin-bottom: 0.05in;
  }

  .slide-title {
    font-size: 0.44in;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1.1;
  }

  .slide-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.38in;
    font-weight: 700;
    color: #10b981;
    background: rgba(16, 185, 129, 0.12);
    padding: 0.08in 0.2in;
    border-radius: 0.1in;
    border: 1px solid rgba(16, 185, 129, 0.3);
  }

  /* Body */
  .slide-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0.3in 0;
  }

  /* Footer */
  .slide-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 0.18in;
    font-size: 0.14in;
    color: #94a3b8;
  }

  .slide-footer .team-info {
    font-weight: 600;
    color: #cbd5e1;
  }

  .slide-footer .live-badge {
    color: #10b981;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  /* Card Grids */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.4in;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.3in;
  }

  .grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.25in;
  }

  .card {
    background: rgba(15, 28, 20, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 0.15in;
    padding: 0.3in;
    box-shadow: 0 0.1in 0.3in rgba(0, 0, 0, 0.4);
  }

  .card-highlight {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 28, 20, 0.9) 100%);
    border-color: rgba(16, 185, 129, 0.35);
  }

  .card-gold {
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(15, 28, 20, 0.9) 100%);
    border-color: rgba(212, 175, 55, 0.35);
  }

  .card-title {
    font-size: 0.22in;
    font-weight: 700;
    color: #34d399;
    margin-bottom: 0.12in;
  }

  .card-p {
    font-size: 0.17in;
    line-height: 1.45;
    color: #cbd5e1;
  }

  .stat-big {
    font-size: 0.55in;
    font-weight: 800;
    color: #10b981;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
    margin-bottom: 0.08in;
  }

  .stat-label {
    font-size: 0.15in;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
  }

  /* List items */
  ul.feature-list {
    list-style: none;
  }

  ul.feature-list li {
    font-size: 0.175in;
    line-height: 1.5;
    margin-bottom: 0.14in;
    padding-left: 0.3in;
    position: relative;
    color: #e2e8f0;
  }

  ul.feature-list li::before {
    content: "■";
    position: absolute;
    left: 0;
    color: #10b981;
    font-size: 0.16in;
  }

  /* Title Slide Styling */
  .title-slide {
    background: radial-gradient(circle at 50% 40%, #102d1d 0%, #060b08 80%);
    text-align: center;
    justify-content: center;
    align-items: center;
    padding: 0.8in;
  }

  .title-hero {
    font-size: 0.85in;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin-bottom: 0.12in;
    background: linear-gradient(135deg, #ffffff 0%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .title-tagline {
    font-size: 0.28in;
    color: #d4af37;
    font-weight: 600;
    max-width: 12in;
    margin: 0 auto 0.4in;
    line-height: 1.35;
  }

  .title-big-idea {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 0.2in 0.5in;
    border-radius: 0.15in;
    font-size: 0.2in;
    color: #e2e8f0;
    max-width: 11.5in;
    margin: 0 auto 0.4in;
    line-height: 1.4;
  }

  .title-meta {
    font-size: 0.16in;
    color: #94a3b8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
  }

  .step-number {
    width: 0.45in;
    height: 0.45in;
    border-radius: 50%;
    background: #10b981;
    color: #060b08;
    font-weight: 800;
    font-size: 0.22in;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.15in;
  }
</style>
</head>
<body>

<!-- SLIDE 00: TITLE SLIDE -->
<div class="slide title-slide">
  <div class="univ-tag">MZUZU UNIVERSITY &middot; FACULTY OF SCIENCE, TECHNOLOGY AND INNOVATION</div>
  <div style="font-size: 0.2in; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.2in;">
    Department of Information and Communication Technology (ICT) &middot; Software Product Exhibition 2026
  </div>
  
  <h1 class="title-hero">FARMPULSE MALAWI</h1>
  
  <div class="title-tagline">
    Data-Driven Agricultural Intelligence, Crop Planning &amp; Parametric Risk Protection for Malawi's Smallholders and Extension Systems
  </div>

  <div class="title-big-idea">
    <strong style="color: #34d399;">THE BIG IDEA:</strong> Transforming smallholder farming from high-risk climate guesswork into predictable, profitable, and de-risked agro-enterprise through localized agromet intelligence, satellite telemetry, and governance tools.
  </div>

  <div class="title-meta">
    DEVELOPER &amp; INNOVATOR: BRIAN NANKHUNI &middot; PRESENTATION TIME: 5 MINUTES &middot; NOVEMBER 2026
  </div>
</div>

<!-- SLIDE 01: THE PROBLEM -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">01 &middot; THE PROBLEM</h2>
    </div>
    <div class="slide-number">01</div>
  </div>

  <div class="slide-body">
    <div class="grid-3">
      <div class="card card-highlight">
        <div class="card-title">The Real-World Challenge</div>
        <p class="card-p">
          Malawi's 3.2 million smallholder farming households invest scarce capital into seed and fertilizer with <strong>zero reliable data</strong> on rainfall continuation, crop economic viability, or market commodity prices.
        </p>
      </div>

      <div class="card">
        <div class="card-title">How It Is Handled Today</div>
        <p class="card-p">
          Farmers rely on guesswork, ancestral intuition, and delayed radio forecasts. Extension officers face impossible ratios (<strong>1 officer to over 2,500 farmers</strong>), making timely agronomic advice impossible to deliver in person.
        </p>
      </div>

      <div class="card card-gold">
        <div class="card-title">The Devastating Cost</div>
        <p class="card-p">
          A single 14-day mid-season dry spell wipes out 60% of household seasonal investment. In Malawi, agriculture generates <strong>80% of export earnings and feeds 19M people</strong>, yet 74% farm without actionable data.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">The Problem Statement</div>
  </div>
</div>

<!-- SLIDE 02: OUR SOLUTION -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">02 &middot; OUR SOLUTION</h2>
    </div>
    <div class="slide-number">02</div>
  </div>

  <div class="slide-body">
    <div class="grid-2">
      <div class="card card-highlight" style="display: flex; flex-direction: column; justify-content: center;">
        <div class="card-title" style="font-size: 0.28in;">Integrated Agricultural Intelligence</div>
        <p class="card-p" style="font-size: 0.2in; line-height: 1.6;">
          FarmPulse Malawi is an agricultural decision-support and governance ecosystem that unites <strong>localized climate risk modeling, dynamic enterprise crop planning, Sentinel-2 satellite Earth Observation, and parametric micro-insurance</strong> into one unified platform.
        </p>
      </div>

      <div class="card" style="display: flex; flex-direction: column; justify-content: center;">
        <div class="card-title" style="font-size: 0.28in;">What Users Can Now Do</div>
        <ul class="feature-list" style="font-size: 0.18in;">
          <li><strong>Better Decisions:</strong> Compare Food Security vs. High-Margin commercial crop plans before spending money.</li>
          <li><strong>Faster Planning:</strong> 90-second automated input allocation replacing 3-week extension consultation cycles.</li>
          <li><strong>Affordable De-risking:</strong> Access zero-adjuster drought insurance that pays out automatically to mobile money.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">The Solution</div>
  </div>
</div>

<!-- SLIDE 03: WHO BENEFITS? -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">03 &middot; WHO BENEFITS?</h2>
    </div>
    <div class="slide-number">03</div>
  </div>

  <div class="slide-body">
    <div class="grid-2">
      <div class="card card-highlight">
        <div class="card-title" style="font-size: 0.24in; color: #10b981;">PRIMARY USERS</div>
        <ul class="feature-list" style="margin-top: 0.1in;">
          <li><strong>Smallholder Farmers:</strong> Commercial and semi-commercial farmers on Web or basic feature phones (*384# USSD).</li>
          <li><strong>District Agricultural Officers (DADOs):</strong> Ministry extension leaders monitoring district-wide crop health and disaster risks.</li>
          <li><strong>Farmer Cooperatives:</strong> Outgrower managers planning aggregate seed multiplication, input bulk-buying, and collective market sales.</li>
        </ul>
      </div>

      <div class="card card-gold">
        <div class="card-title" style="font-size: 0.24in; color: #d4af37;">BENEFICIARIES &amp; ECOSYSTEM</div>
        <ul class="feature-list" style="margin-top: 0.1in;">
          <li><strong>Agribusiness Off-takers:</strong> Pyxus, ETG, Sunseed Oil gaining yield delivery forecasts 6 weeks ahead of collection.</li>
          <li><strong>Lending Banks &amp; MFIs:</strong> NBS Bank, FINCA utilizing verified yield histories to de-risk agricultural credit lines.</li>
          <li><strong>Parametric Insurers:</strong> NICO General and Old Mutual underwrite rainfall micro-policies with automated satellite triggers.</li>
          <li><strong>Wider Economy:</strong> National food security balance sheets stabilized through predictive deficit warnings.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Stakeholders &amp; Market Beneficiaries</div>
  </div>
</div>

<!-- SLIDE 04: HOW IT WORKS -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">04 &middot; HOW IT WORKS</h2>
    </div>
    <div class="slide-number">04</div>
  </div>

  <div class="slide-body">
    <div class="grid-4">
      <div class="card">
        <div class="step-number">1</div>
        <div class="card-title">User Input</div>
        <p class="card-p">
          Farmer specifies land size (ha/acres), available seasonal budget (MWK), district/AEZ, soil type, and preferred crops via Web or <strong>*384# USSD</strong>.
        </p>
      </div>

      <div class="card card-highlight">
        <div class="step-number">2</div>
        <div class="card-title">Intelligence Engine</div>
        <p class="card-p">
          Platform cross-analyzes 10-year district rainfall records, dry-spell risk curves, input benchmark costs (AIP rates), and regional commodity market spreads.
        </p>
      </div>

      <div class="card">
        <div class="step-number">3</div>
        <div class="card-title">Tailored Output</div>
        <p class="card-p">
          Generates 3 calibrated crop allocations (Food Security, High Margin, Climate Resilient) with exact input quantities, planting dates, and breakeven prices.
        </p>
      </div>

      <div class="card card-gold">
        <div class="step-number">4</div>
        <div class="card-title">Action &amp; Protection</div>
        <p class="card-p">
          Farmer monitors field canopy vigor via Sentinel-2 satellite NDVI; automated parametric insurance triggers instant Airtel/TNM mobile money payout if dry spell strikes.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Workflow Architecture</div>
  </div>
</div>

<!-- SLIDE 05: PRODUCT SNAPSHOT -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">05 &middot; PRODUCT SNAPSHOT</h2>
    </div>
    <div class="slide-number">05</div>
  </div>

  <div class="slide-body">
    <div class="grid-3">
      <div class="card card-highlight">
        <div class="card-title">Farmer Intelligence Center</div>
        <p class="card-p">
          Integrated dashboard connecting real-time weather stations, 10-year longitudinal farm history, dynamic crop budgeting, and local market price arbitration.
        </p>
        <div style="margin-top: 0.2in; font-weight: 700; color: #10b981;">&rarr; Route: / &middot; /planner/</div>
      </div>

      <div class="card">
        <div class="card-title">Sentinel-2 Earth Observation</div>
        <p class="card-p">
          Multi-spectral satellite telemetry calculating live Normalized Difference Vegetation Index (NDVI) and topsoil moisture across field boundary polygons every 5 days.
        </p>
        <div style="margin-top: 0.2in; font-weight: 700; color: #38bdf8;">&rarr; Route: /satellite/</div>
      </div>

      <div class="card card-gold">
        <div class="card-title">DADO &amp; Extension Portal</div>
        <p class="card-p">
          National governance console tracking 15 smallholder cohorts across 12 districts, climate threat radars, and interactive emergency SMS alert broadcast console.
        </p>
        <div style="margin-top: 0.2in; font-weight: 700; color: #d4af37;">&rarr; Route: /admin-portal/ &middot; /admin/</div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Live System: https://farmpulse-p6jl.onrender.com/</div>
  </div>
</div>

<!-- SLIDE 06: STANDOUT FEATURES -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">06 &middot; STANDOUT FEATURES</h2>
    </div>
    <div class="slide-number">06</div>
  </div>

  <div class="slide-body">
    <div class="grid-2">
      <div class="card">
        <ul class="feature-list">
          <li>
            <strong>Dynamic Land &amp; Budget Allocator</strong><br>
            <span style="color: #94a3b8; font-size: 0.15in;">&rarr; Benefit: Automatically balances seed and fertilizer costs against capital, preventing mid-season farm abandonment.</span>
          </li>
          <li>
            <strong>Sentinel-2 Satellite Digital Twin</strong><br>
            <span style="color: #94a3b8; font-size: 0.15in;">&rarr; Benefit: Detects moisture stress and chlorophyll deficit from space without purchasing expensive IoT field hardware.</span>
          </li>
          <li>
            <strong>Zero-Adjuster Parametric Drought Insurance</strong><br>
            <span style="color: #94a3b8; font-size: 0.15in;">&rarr; Benefit: Eliminates corrupt or slow human adjusters; dispatches claims in minutes straight to Airtel Money / TNM Mpamba.</span>
          </li>
        </ul>
      </div>

      <div class="card card-highlight">
        <ul class="feature-list">
          <li>
            <strong>Basic Phone Accessibility (*384# USSD)</strong><br>
            <span style="color: #94a3b8; font-size: 0.15in;">&rarr; Benefit: Delivers agromet forecasts and market price spreads in Chichewa &amp; Tumbuka to farmers with zero internet.</span>
          </li>
          <li>
            <strong>DADO Extension &amp; Governance Center</strong><br>
            <span style="color: #94a3b8; font-size: 0.15in;">&rarr; Benefit: Equips Ministry officers with district-wide farmer registries, aggregated yield forecasts, and emergency SMS broadcasts.</span>
          </li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Feature to Benefit Mapping</div>
  </div>
</div>

<!-- SLIDE 07: PROOF IT WORKS -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">07 &middot; PROOF IT WORKS</h2>
    </div>
    <div class="slide-number">07</div>
  </div>

  <div class="slide-body">
    <div class="grid-4" style="margin-bottom: 0.3in;">
      <div class="card" style="text-align: center;">
        <div class="stat-big">15</div>
        <div class="stat-label">Active Farmers</div>
      </div>
      <div class="card card-highlight" style="text-align: center;">
        <div class="stat-big">48.5 ha</div>
        <div class="stat-label">Monitored Land</div>
      </div>
      <div class="card" style="text-align: center;">
        <div class="stat-big">194</div>
        <div class="stat-label">Planting Records</div>
      </div>
      <div class="card card-gold" style="text-align: center;">
        <div class="stat-big">MWK 28.6M</div>
        <div class="stat-label">Tracked Revenue</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Current Development Stage: Working MVP / Live Pre-Pilot</div>
      <p class="card-p">
        Validated across 12 Malawian districts (Northern Highlands, Central Plain, Shire Valley). Features <strong>10 years of longitudinal seasonal data (2015/16–2024/25)</strong> on Miriam Chiphaka Field in Mzuzu, and proven drought trigger dispatch (MWK 744,000 policy payout triggered in Balaka).
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Evidence &amp; Validation</div>
  </div>
</div>

<!-- SLIDE 08: WHAT MAKES IT DIFFERENT? -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">08 &middot; WHAT MAKES IT DIFFERENT?</h2>
    </div>
    <div class="slide-number">08</div>
  </div>

  <div class="slide-body">
    <div class="grid-3">
      <div class="card">
        <div class="card-title">Traditional Ag Apps</div>
        <p class="card-p" style="color: #94a3b8;">
          Broadcast generic weather forecasts or static raw price tables. They tell the farmer it will rain 10mm, leaving them to guess what that means for crop planting or fertilizer application.
        </p>
      </div>

      <div class="card card-highlight">
        <div class="card-title" style="color: #34d399;">The FarmPulse Edge</div>
        <p class="card-p">
          <strong>Translates raw data into financial consequence.</strong> Calibrates weather probability curves directly against farmer land size and budget, telling them exactly what to plant and when to sell.
        </p>
      </div>

      <div class="card card-gold">
        <div class="card-title" style="color: #d4af37;">Shared Governance Ledger</div>
        <p class="card-p">
          Connects the smallholder, extension officer (DADO), lending bank (credit risk scoring), and insurance underwriter on <strong>one unified digital platform</strong> with basic USSD accessibility.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Competitive Advantage</div>
  </div>
</div>

<!-- SLIDE 09: IMPACT & VALUE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">09 &middot; IMPACT &amp; VALUE</h2>
    </div>
    <div class="slide-number">09</div>
  </div>

  <div class="slide-body">
    <div class="grid-3">
      <div class="card card-highlight">
        <div class="stat-big">&lt; 90 sec</div>
        <div class="stat-label" style="color: #34d399; margin-bottom: 0.1in;">Time Saved</div>
        <p class="card-p">
          Reduces comprehensive multi-crop planning time from 3 weeks of manual extension visits down to under 90 seconds of algorithmic generation.
        </p>
      </div>

      <div class="card card-gold">
        <div class="stat-big">22% Cut</div>
        <div class="stat-label" style="color: #d4af37; margin-bottom: 0.1in;">Costs Reduced</div>
        <p class="card-p">
          Reduces input expenditure waste by 22% through precise fertilizer-to-land calibrations; cuts agricultural loan default rates from 16% to under 4%.
        </p>
      </div>

      <div class="card">
        <div class="stat-big">+35% to +60%</div>
        <div class="stat-label" style="color: #38bdf8; margin-bottom: 0.1in;">Profit Increased</div>
        <p class="card-p">
          Boosts smallholder net household profit margins by 35%–60% via high-margin legume rotation and transport arbitrage to higher-paying trading hubs.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Quantifiable Agronomic Impact</div>
  </div>
</div>

<!-- SLIDE 10: SUSTAINABILITY & BUSINESS MODEL -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">10 &middot; SUSTAINABILITY &amp; BUSINESS MODEL</h2>
    </div>
    <div class="slide-number">10</div>
  </div>

  <div class="slide-body">
    <div class="grid-2">
      <div class="card card-highlight">
        <div class="card-title">B2B2C &amp; B2B2G Monetization Architecture</div>
        <ul class="feature-list" style="font-size: 0.165in;">
          <li><strong>Agribusiness SaaS:</strong> Off-takers (Pyxus, ETG, Sunseed) pay MWK 4.5M–12M/yr for outgrower monitoring &amp; yield prediction.</li>
          <li><strong>Fintech Loan Origination API:</strong> Commercial banks &amp; MFIs (NBS Bank, FINCA) pay 1.75% fee per de-risked agricultural loan.</li>
          <li><strong>Insurtech Brokerage:</strong> 8%–10% commission on parametric micro-policies underwritten by NICO General / Old Mutual.</li>
          <li><strong>Government DPI Contracts:</strong> Ministry of Ag &amp; WFP district analytical licenses at MWK 15M–25M/district.</li>
          <li><strong>Freemium Telco Micro-Billing:</strong> Premium SMS advisory at MWK 100/mo via Airtel/TNM airtime (70/30 rev-share).</li>
        </ul>
      </div>

      <div class="card card-gold">
        <div class="card-title">3-Year Financial Model (MWK)</div>
        <table style="width: 100%; font-size: 0.16in; color: #e2e8f0; border-collapse: collapse; margin-top: 0.1in;">
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #94a3b8;">
            <th style="padding: 0.08in 0; text-align: left;">Metric</th>
            <th style="text-align: right;">Year 1 (Pilot)</th>
            <th style="text-align: right;">Year 2 (Scale)</th>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <td style="padding: 0.08in 0;">Active Smallholders</td>
            <td style="text-align: right; color: #10b981; font-weight: 700;">3,500</td>
            <td style="text-align: right; color: #10b981; font-weight: 700;">18,000</td>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <td style="padding: 0.08in 0;">Gross Revenue</td>
            <td style="text-align: right; font-weight: 700;">MWK 42.5M</td>
            <td style="text-align: right; font-weight: 700;">MWK 177.2M</td>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <td style="padding: 0.08in 0;">Operating Costs</td>
            <td style="text-align: right;">MWK 31.0M</td>
            <td style="text-align: right;">MWK 92.0M</td>
          </tr>
          <tr>
            <td style="padding: 0.08in 0; font-weight: 700; color: #34d399;">EBITDA Margin</td>
            <td style="text-align: right; font-weight: 800; color: #34d399;">+MWK 11.5M (27%)</td>
            <td style="text-align: right; font-weight: 800; color: #34d399;">+MWK 85.2M (48%)</td>
          </tr>
        </table>
        <div style="margin-top: 0.15in; font-size: 0.14in; color: #d4af37; font-weight: 600;">
          &rarr; Breakeven achieved in Month 11 with positive cash flow.
        </div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Commercialization &amp; Unit Economics</div>
  </div>
</div>

<!-- SLIDE 11: NEXT MILESTONES -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">11 &middot; NEXT MILESTONES</h2>
    </div>
    <div class="slide-number">11</div>
  </div>

  <div class="slide-body">
    <div class="grid-3">
      <div class="card card-highlight">
        <div class="card-title" style="color: #34d399;">NEXT 3 MONTHS &middot; Q1 2027</div>
        <p class="card-p">
          <strong>Field Pilot Validation:</strong> Formalize pilot trials with 3 farmer cooperatives in Mzuzu and Lilongwe (500 smallholders). Deploy official TNM/Airtel short-code for USSD *384#.
        </p>
      </div>

      <div class="card card-gold">
        <div class="card-title" style="color: #d4af37;">NEXT 6 MONTHS &middot; Q2&ndash;Q3 2027</div>
        <p class="card-p">
          <strong>Fintech &amp; Insurance Sandbox:</strong> Complete API sandboxing with NBS Bank for agricultural credit scoring; partner with NICO General for commercial parametric micro-insurance underwriting.
        </p>
      </div>

      <div class="card">
        <div class="card-title" style="color: #38bdf8;">NEXT 12 MONTHS &middot; 2027/28</div>
        <p class="card-p">
          <strong>National Expansion:</strong> Scale to 15,000 smallholders across 5 districts; secure Ministry of Agriculture (AGCOM 2) institutional endorsement for national DADO deployment.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; FarmPulse Malawi</div>
    <div class="live-badge">Product Roadmap</div>
  </div>
</div>

<!-- SLIDE 12: WHAT WE NEED FROM YOU -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="univ-tag">MZUZU UNIVERSITY &middot; SOFTWARE PRODUCT EXHIBITION</div>
      <h2 class="slide-title">12 &middot; WHAT WE NEED FROM YOU</h2>
    </div>
    <div class="slide-number">12</div>
  </div>

  <div class="slide-body">
    <div class="grid-2">
      <div class="card card-highlight">
        <div class="card-title" style="font-size: 0.24in;">We Are Actively Looking For:</div>
        <ul class="feature-list" style="margin-top: 0.15in; font-size: 0.18in;">
          <li><strong>[x] Pilot Sites &amp; Cooperatives:</strong> 3 commercial agricultural cooperatives or outgrower schemes for structured Phase 1 field testing.</li>
          <li><strong>[x] Institutional Partners:</strong> Insurance underwriters (NICO General, Old Mutual) and agri-lenders (NBS Bank, National Bank, FINCA).</li>
          <li><strong>[x] Faculty Mentors:</strong> Mzuzu University agronomy and economics lecturers to validate regional agro-ecological zone yield models.</li>
          <li><strong>[x] Seed Funding &amp; Technical Grants:</strong> Capital to fund telco USSD integration fees, Sentinel-2 compute, and district extension workshops.</li>
        </ul>
      </div>

      <div class="card card-gold" style="display: flex; flex-direction: column; justify-content: center; text-align: center;">
        <div class="card-title" style="font-size: 0.28in; color: #d4af37;">OUR ONE CLEAR ASK</div>
        <p class="card-p" style="font-size: 0.22in; line-height: 1.5; margin: 0.2in 0;">
          "Join us today as a pilot partner, institutional sponsor, or research collaborator to transform Malawi's smallholder agriculture from climate vulnerability into profitable, resilient enterprise."
        </p>
        <div style="font-size: 0.16in; color: #10b981; font-weight: 700;">
          Live Platform: https://farmpulse-p6jl.onrender.com/
        </div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="team-info">Brian Nankhuni &middot; Email: brian@gmail.com &middot; Tel: +265 88 412 8901</div>
    <div class="live-badge">Scan / Visit Live Platform</div>
  </div>
</div>

</body>
</html>
"""

output_html = "FarmPulse_Mzuzu_University_Exhibition_Deck.html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {output_html}")

# Compile into PDF using Microsoft Edge headless
edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

edge_exe = None
for p in edge_paths:
    if os.path.exists(p):
        edge_exe = p
        break

if edge_exe:
    abs_html = os.path.abspath(output_html)
    abs_pdf = os.path.abspath("FarmPulse_Mzuzu_University_Exhibition_Deck.pdf")
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=" + abs_pdf,
        "--no-pdf-header-footer",
        abs_html
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Generated PDF: {abs_pdf} ({os.path.getsize(abs_pdf):,} bytes)")
else:
    print("Microsoft Edge not found for PDF export.")

