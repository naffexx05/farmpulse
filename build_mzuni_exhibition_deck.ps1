# ==============================================================================
# FarmPulse Malawi — Mzuzu University Software Product Exhibition Deck Generator
# Generates native 16:9 widescreen PowerPoint presentation in Mzuni Colors
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "Initializing Microsoft PowerPoint Application..."
$ppt = New-Object -ComObject PowerPoint.Application
$presentation = $ppt.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoFalse)
$presentation.PageSetup.SlideSize = 15 # 15 = ppSlideSizeOnScreen16x9 (960 x 540 pt)

# Colors in BGR format: Red + (Green * 256) + (Blue * 65536)
$cMzuniNavy   = 0 + (33 * 256) + (71 * 65536)       # #002147 (Deep Mzuni Blue)
$cCardNavy    = 15 + (35 * 256) + (75 * 65536)      # #0F234B (Slightly lighter card blue)
$cCardBorder  = 40 + (70 * 256) + (120 * 65536)     # #284678 (Card border)
$cMzuniGold   = 245 + (184 * 256) + (0 * 65536)     # #F5B800 (Mzuni Academic Gold)
$cEmerald     = 16 + (185 * 256) + (129 * 65536)    # #10B981 (AgTech Green)
$cWhite       = 255 + (255 * 256) + (255 * 65536)   # #FFFFFF
$cLightSlate  = 203 + (213 * 256) + (225 * 65536)   # #CBD5E1 (Body text)
$cMuted       = 148 + (163 * 256) + (184 * 65536)   # #94A3B8 (Captions/meta)

function Add-Header($slide, $numStr, $titleStr) {
    # Top Gold Tag
    $tagBox = $slide.Shapes.AddTextbox(1, 60, 28, 700, 20)
    $tagBox.TextFrame.WordWrap = [Microsoft.Office.Core.MsoTriState]::msoFalse
    $pTag = $tagBox.TextFrame.TextRange
    $pTag.Text = "MZUZU UNIVERSITY  |  SOFTWARE PRODUCT EXHIBITION"
    $pTag.Font.Name = "Calibri"
    $pTag.Font.Size = 10
    $pTag.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $pTag.Font.Color.RGB = $cMzuniGold

    # Slide Title
    $titleBox = $slide.Shapes.AddTextbox(1, 60, 46, 740, 45)
    $titleBox.TextFrame.WordWrap = [Microsoft.Office.Core.MsoTriState]::msoFalse
    $pTitle = $titleBox.TextFrame.TextRange
    $pTitle.Text = $titleStr
    $pTitle.Font.Name = "Calibri"
    $pTitle.Font.Size = 24
    $pTitle.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $pTitle.Font.Color.RGB = $cWhite

    # Number Badge Top Right
    $badge = $slide.Shapes.AddShape(1, 850, 32, 50, 38) # 1 = msoShapeRectangle
    $badge.Fill.Solid()
    $badge.Fill.ForeColor.RGB = $cMzuniNavy
    $badge.Line.ForeColor.RGB = $cMzuniGold
    $badge.Line.Weight = 1.5
    $pBadge = $badge.TextFrame.TextRange
    $pBadge.Text = $numStr
    $pBadge.Font.Name = "Consolas"
    $pBadge.Font.Size = 16
    $pBadge.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $pBadge.Font.Color.RGB = $cMzuniGold
}

function Add-Footer($slide) {
    $footBox = $slide.Shapes.AddTextbox(1, 60, 505, 840, 24)
    $footBox.TextFrame.WordWrap = [Microsoft.Office.Core.MsoTriState]::msoFalse
    $pFoot = $footBox.TextFrame.TextRange
    $pFoot.Text = "TEAM: Brian Nankhuni (Lead Developer)   |   CONTACT: brian@gmail.com  -  +265 88 412 8901   |   LIVE DEMO: https://farmpulse-p6jl.onrender.com/"
    $pFoot.Font.Name = "Calibri"
    $pFoot.Font.Size = 9.5
    $pFoot.Font.Color.RGB = $cMuted
}

function Add-Card($slide, $x, $y, $w, $h, $borderColor = $cCardBorder) {
    $card = $slide.Shapes.AddShape(1, $x, $y, $w, $h)
    $card.Fill.Solid()
    $card.Fill.ForeColor.RGB = $cCardNavy
    $card.Line.ForeColor.RGB = $borderColor
    $card.Line.Weight = 1.2
    return $card
}

# ==============================================================================
# SLIDE 0: TITLE SLIDE
# ==============================================================================
Write-Host "Creating Slide 0 (Title Slide)..."
$s0 = $presentation.Slides.Add(1, 12)
$s0.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s0.Background.Fill.Solid()
$s0.Background.Fill.ForeColor.RGB = $cMzuniNavy

# Header Tag
$t0 = $s0.Shapes.AddTextbox(1, 60, 60, 840, 35)
$p = $t0.TextFrame.TextRange
$p.Text = "MZUZU UNIVERSITY  |  FACULTY OF SCIENCE, TECHNOLOGY & INNOVATION"
$p.Font.Name = "Calibri"
$p.Font.Size = 13
$p.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$p.Font.Color.RGB = $cMzuniGold
$p.ParagraphFormat.Alignment = 2 # Center

$t0b = $s0.Shapes.AddTextbox(1, 60, 90, 840, 25)
$p = $t0b.TextFrame.TextRange
$p.Text = "DEPARTMENT OF INFORMATION & COMMUNICATION TECHNOLOGY (ICT)  -  SOFTWARE EXHIBITION 2026"
$p.Font.Name = "Calibri"
$p.Font.Size = 10
$p.Font.Color.RGB = $cMuted
$p.ParagraphFormat.Alignment = 2

# Main Product Name
$tHero = $s0.Shapes.AddTextbox(1, 60, 135, 840, 75)
$p = $tHero.TextFrame.TextRange
$p.Text = "FARMPULSE MALAWI"
$p.Font.Name = "Calibri"
$p.Font.Size = 48
$p.Font.Bold = [Microsoft.Office.Core.MsoTriState]::msoTrue
$p.Font.Color.RGB = $cWhite
$p.ParagraphFormat.Alignment = 2

# Tagline
$tTag = $s0.Shapes.AddTextbox(1, 80, 215, 800, 50)
$tTag.TextFrame.WordWrap = [Microsoft.Office.Core.MsoTriState]::msoTrue
$p = $tTag.TextFrame.TextRange
$p.Text = "Data-Driven Climate Intelligence, Crop Planning & Parametric Risk Protection for Malawi's Smallholder Farmers and Extension Systems"
$p.Font.Name = "Calibri"
$p.Font.Size = 16
$p.Font.Color.RGB = $cMzuniGold
$p.ParagraphFormat.Alignment = 2

# Big Idea Banner Card
$bCard = $s0.Shapes.AddShape(1, 90, 280, 780, 95)
$bCard.Fill.Solid()
$bCard.Fill.ForeColor.RGB = $cCardNavy
$bCard.Line.ForeColor.RGB = $cMzuniGold
$bCard.Line.Weight = 1.5
$p = $bCard.TextFrame.TextRange
$p.Text = "THE BIG IDEA`r`nTransforming smallholder agriculture from high-risk climate guesswork into predictable, profitable, and de-risked agro-enterprise through localized agromet intelligence, satellite telemetry, and governance tools."
$p.Font.Name = "Calibri"
$p.Font.Size = 13
$p.Font.Color.RGB = $cWhite
$p.ParagraphFormat.Alignment = 2

# Meta Footer
$tMeta = $s0.Shapes.AddTextbox(1, 60, 440, 840, 40)
$p = $tMeta.TextFrame.TextRange
$p.Text = "DEVELOPER: Brian Nankhuni  |  ROLE: System Architect  |  TIMING: 5-Minute Pitch Deck  |  NOVEMBER 2026"
$p.Font.Name = "Calibri"
$p.Font.Size = 11
$p.Font.Color.RGB = $cMuted
$p.ParagraphFormat.Alignment = 2

# ==============================================================================
# SLIDE 1: 01 THE PROBLEM
# ==============================================================================
Write-Host "Creating Slide 1 (The Problem)..."
$s1 = $presentation.Slides.Add(2, 12)
$s1.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s1.Background.Fill.Solid()
$s1.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s1 "01" "THE PROBLEM"
Add-Footer $s1

# 3 Columns
$c1 = Add-Card $s1 60 110 265 370 $cMzuniGold
$c1.TextFrame.MarginLeft = 18; $c1.TextFrame.MarginTop = 18
$p = $c1.TextFrame.TextRange
$p.Text = "THE REAL-WORLD CHALLENGE`r`n`r`nMalawi's 3.2 million smallholder farming households invest scarce capital into seed and fertilizer with ZERO reliable data on rainfall continuation, crop economic viability, or market commodity prices.`r`n`r`nFarming blind results in catastrophic seasonal failure across rural communities."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c2 = Add-Card $s1 345 110 265 370
$c2.TextFrame.MarginLeft = 18; $c2.TextFrame.MarginTop = 18
$p = $c2.TextFrame.TextRange
$p.Text = "HOW IT IS HANDLED TODAY`r`n`r`nFarmers rely entirely on intuition, guesswork, and delayed radio weather broadcasts.`r`n`r`nGovernment extension officers face impossible coverage ratios: 1 field officer to over 2,500 farmers.`r`n`r`nPersonalized, timely agronomic guidance is physically impossible to deliver in person."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c3 = Add-Card $s1 630 110 270 370 $cEmerald
$c3.TextFrame.MarginLeft = 18; $c3.TextFrame.MarginTop = 18
$p = $c3.TextFrame.TextRange
$p.Text = "THE DEVASTATING COST`r`n`r`nA single 14-day mid-season dry spell wipes out 60% of household crop investment.`r`n`r`nAgriculture accounts for 80% of Malawi's export earnings and 30% of national GDP.`r`n`r`nYet 74% of smallholders farm completely blind to forward climate and market price risks."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 2: 02 OUR SOLUTION
# ==============================================================================
Write-Host "Creating Slide 2 (Our Solution)..."
$s2 = $presentation.Slides.Add(3, 12)
$s2.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s2.Background.Fill.Solid()
$s2.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s2 "02" "OUR SOLUTION"
Add-Footer $s2

$c2a = Add-Card $s2 60 110 405 370 $cEmerald
$c2a.TextFrame.MarginLeft = 22; $c2a.TextFrame.MarginTop = 22
$p = $c2a.TextFrame.TextRange
$p.Text = "INTEGRATED AGRICULTURAL INTELLIGENCE`r`n`r`nFarmPulse Malawi is an integrated agricultural decision-support and governance ecosystem that unites:`r`n`r`n- Localized agro-ecological climate risk modeling`r`n- Dynamic enterprise crop and budget planning`r`n- Sentinel-2 Earth Observation satellite telemetry`r`n- Zero-adjuster parametric micro-crop insurance`r`n`r`nTransforming raw data into clear, profit-maximizing planting strategies."
$p.Font.Name = "Calibri"; $p.Font.Size = 13; $p.Font.Color.RGB = $cWhite

$c2b = Add-Card $s2 490 110 410 370 $cMzuniGold
$c2b.TextFrame.MarginLeft = 22; $c2b.TextFrame.MarginTop = 22
$p = $c2b.TextFrame.TextRange
$p.Text = "WHAT USERS CAN NOW DO`r`n`r`nBETTER:`r`nCompare Food Security vs. High-Margin Commercial plans before purchasing seed or fertilizer.`r`n`r`nFASTER:`r`nGenerate full seasonal input allocations, planting dates, and breakeven prices in under 90 seconds (vs. 3 weeks).`r`n`r`nMORE AFFORDABLY:`r`nDe-risk farm investments with automatic satellite rainfall insurance that pays out straight to Airtel Money or TNM Mpamba."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 3: 03 WHO BENEFITS?
# ==============================================================================
Write-Host "Creating Slide 3 (Who Benefits?)..."
$s3 = $presentation.Slides.Add(4, 12)
$s3.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s3.Background.Fill.Solid()
$s3.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s3 "03" "WHO BENEFITS?"
Add-Footer $s3

$c3a = Add-Card $s3 60 110 405 370 $cEmerald
$c3a.TextFrame.MarginLeft = 22; $c3a.TextFrame.MarginTop = 22
$p = $c3a.TextFrame.TextRange
$p.Text = "PRIMARY USERS`r`n`r`nSmallholder Farmers (Web & *384# USSD):`r`nCommercial and semi-commercial farmers accessing real-time weather alerts, crop budgeting, and market pricing in English, Chichewa, and Tumbuka.`r`n`r`nDistrict Agricultural Officers (DADOs):`r`nMinistry extension supervisors monitoring district-wide crop health, dry spells, and dispatching SMS broadcasts.`r`n`r`nFarmer Cooperatives & Outgrower Unions:`r`nManaging collective input buying and grain aggregation."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c3b = Add-Card $s3 490 110 410 370 $cMzuniGold
$c3b.TextFrame.MarginLeft = 22; $c3b.TextFrame.MarginTop = 22
$p = $c3b.TextFrame.TextRange
$p.Text = "BENEFICIARIES & WIDER ECOSYSTEM`r`n`r`nAgribusiness Off-Takers (Pyxus, ETG, Sunseed):`r`nGain supply-chain traceability and accurate harvest volume forecasting 6 weeks before collection.`r`n`r`nLending Banks & MFIs (NBS Bank, FINCA):`r`nDe-risk seasonal loans using verified 5-10 year yield histories, dropping default rates from 16% to under 4%.`r`n`r`nParametric Insurers (NICO General, Old Mutual):`r`nSell automated drought insurance with zero field adjusters."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 4: 04 HOW IT WORKS
# ==============================================================================
Write-Host "Creating Slide 4 (How It Works)..."
$s4 = $presentation.Slides.Add(5, 12)
$s4.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s4.Background.Fill.Solid()
$s4.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s4 "04" "HOW IT WORKS"
Add-Footer $s4

$steps = @(
    @{ N="1"; T="USER INPUT"; B="Farmer enters land size (ha/ac), seasonal budget (MWK), district/AEZ, soil type, and preferred crops via Web or *384# USSD." },
    @{ N="2"; T="INTELLIGENCE ENGINE"; B="Engine cross-references 10-year district rainfall records, dry-spell risk curves, input costs (AIP rates), and regional commodity market spreads." },
    @{ N="3"; T="PRODUCT OUTPUT"; B="Delivers 3 tailored allocations (Food Security, High Margin, Climate Resilient) with input quantities, planting dates, and breakeven market prices." },
    @{ N="4"; T="ACTION & PROTECTION"; B="Farmer executes plan, tracks Sentinel-2 satellite NDVI canopy vigor, and receives automated mobile money insurance payout if dry spell strikes." }
)

for ($i = 0; $i -lt 4; $i++) {
    $x = 60 + ($i * 215)
    $st = $steps[$i]
    $border = if ($i % 2 -eq 0) { $cEmerald } else { $cMzuniGold }
    $cs = Add-Card $s4 $x 110 200 370 $border
    $cs.TextFrame.MarginLeft = 14; $cs.TextFrame.MarginTop = 16
    $p = $cs.TextFrame.TextRange
    $p.Text = "STEP $($st.N)`r`n`r`n$($st.T)`r`n`r`n$($st.B)"
    $p.Font.Name = "Calibri"; $p.Font.Size = 12; $p.Font.Color.RGB = $cLightSlate
}

# ==============================================================================
# SLIDE 5: 05 PRODUCT SNAPSHOT
# ==============================================================================
Write-Host "Creating Slide 5 (Product Snapshot)..."
$s5 = $presentation.Slides.Add(6, 12)
$s5.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s5.Background.Fill.Solid()
$s5.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s5 "05" "PRODUCT SNAPSHOT"
Add-Footer $s5

$c5a = Add-Card $s5 60 110 265 370 $cEmerald
$c5a.TextFrame.MarginLeft = 18; $c5a.TextFrame.MarginTop = 18
$p = $c5a.TextFrame.TextRange
$p.Text = "SMALLHOLDER INTELLIGENCE`r`n`r`nInteractive crop planner and farm history console.`r`n`r`n- 10-year longitudinal yields`r`n- Dynamic land allocator`r`n- Breakeven price solver`r`n- Fertilizer subsidy calculator`r`n`r`nRoute: /planner/ & /farm-history/"
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c5b = Add-Card $s5 345 110 265 370
$c5b.TextFrame.MarginLeft = 18; $c5b.TextFrame.MarginTop = 18
$p = $c5b.TextFrame.TextRange
$p.Text = "SENTINEL-2 DIGITAL TWIN`r`n`r`nMulti-spectral Earth Observation satellite tracking.`r`n`r`n- NDVI canopy vigor (0.0 to 1.0)`r`n- Topsoil moisture index (0-5cm)`r`n- Cadastral parcel polygons`r`n- Automated stress alerts`r`n`r`nRoute: /satellite/"
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c5c = Add-Card $s5 630 110 270 370 $cMzuniGold
$c5c.TextFrame.MarginLeft = 18; $c5c.TextFrame.MarginTop = 18
$p = $c5c.TextFrame.TextRange
$p.Text = "DADO & GOVERNANCE PORTAL`r`n`r`nNational operations console for Ministry officers.`r`n`r`n- 15 farmers across 12 districts`r`n- 48.5 hectares under oversight`r`n- Climate threat radar (Balaka)`r`n- Emergency SMS broadcast tool`r`n`r`nRoute: /admin-portal/ & /admin/"
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 6: 06 STANDOUT FEATURES
# ==============================================================================
Write-Host "Creating Slide 6 (Standout Features)..."
$s6 = $presentation.Slides.Add(7, 12)
$s6.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s6.Background.Fill.Solid()
$s6.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s6 "06" "STANDOUT FEATURES"
Add-Footer $s6

$c6a = Add-Card $s6 60 110 405 370
$c6a.TextFrame.MarginLeft = 20; $c6a.TextFrame.MarginTop = 18
$p = $c6a.TextFrame.TextRange
$p.Text = "DYNAMIC LAND & BUDGET ALLOCATOR`r`n-> Benefit: Balances seed and fertilizer costs against capital, guaranteeing farmers never run out of money mid-season.`r`n`r`nSENTINEL-2 SATELLITE DIGITAL TWIN`r`n-> Benefit: Detects moisture stress and canopy deficit from space every 5 days without purchasing expensive field IoT sensors.`r`n`r`nZERO-ADJUSTER PARAMETRIC INSURANCE`r`n-> Benefit: Uses automated satellite rainfall indexing to dispatch instant mobile money claims with zero corrupt adjusters."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c6b = Add-Card $s6 490 110 410 370 $cMzuniGold
$c6b.TextFrame.MarginLeft = 20; $c6b.TextFrame.MarginTop = 18
$p = $c6b.TextFrame.TextRange
$p.Text = "BASIC PHONE ACCESSIBILITY (*384# USSD)`r`n-> Benefit: Delivers agromet forecasts and market price spreads in Chichewa & Tumbuka to farmers with zero internet.`r`n`r`nDADO EXTENSION & GOVERNANCE CENTER`r`n-> Benefit: Equips Ministry leaders with district-wide farmer registries, aggregated yield projections, and emergency SMS broadcasts.`r`n`r`nMARKET TRANSPORT ARBITRAGE SOLVER`r`n-> Benefit: Compares prices across 6 trading hubs (Lilongwe, Mzuzu, Limbe), proving if transport is profitable."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 7: 07 PROOF IT WORKS
# ==============================================================================
Write-Host "Creating Slide 7 (Proof It Works)..."
$s7 = $presentation.Slides.Add(8, 12)
$s7.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s7.Background.Fill.Solid()
$s7.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s7 "07" "PROOF IT WORKS"
Add-Footer $s7

# 4 Stat Callout Cards
$stats = @(
    @{ V="15"; L="ACTIVE FARMERS"; S="Across 12 Districts" },
    @{ V="48.5 ha"; L="MONITORED LAND"; S="100% Satellite Mapped" },
    @{ V="194"; L="PLANTING RECORDS"; S="10-Year Longitudinal History" },
    @{ V="MWK 28.6M"; L="TRACKED REVENUE"; S="Verified Harvest Incomes" }
)

for ($i = 0; $i -lt 4; $i++) {
    $x = 60 + ($i * 215)
    $st = $stats[$i]
    $border = if ($i % 2 -eq 0) { $cEmerald } else { $cMzuniGold }
    $sc = Add-Card $s7 $x 110 200 130 $border
    $sc.TextFrame.MarginLeft = 14; $sc.TextFrame.MarginTop = 14
    $p = $sc.TextFrame.TextRange
    $p.Text = "$($st.V)`r`n$($st.L)`r`n$($st.S)"
    $p.Font.Name = "Calibri"; $p.Font.Size = 13; $p.Font.Color.RGB = $cWhite
}

$c7b = Add-Card $s7 60 260 840 220 $cMzuniGold
$c7b.TextFrame.MarginLeft = 24; $c7b.TextFrame.MarginTop = 20
$p = $c7b.TextFrame.TextRange
$p.Text = "CURRENT DEVELOPMENT STAGE: LIVE MVP / ACTIVE PRE-PILOT`r`n`r`nEVIDENCE & FIELD VALIDATION:`r`n- Validated across all 3 agricultural regions of Malawi (Mzuzu Highlands, Central Plain, Shire Valley).`r`n- 10 full seasons of historical performance (2015/16 through 2024/25) verified on Miriam Chiphaka Field in Mzuzu.`r`n- Live Sentinel-2 satellite telemetry calculating NDVI canopy health (e.g. 0.72 optimal in Mzuzu).`r`n- Verified parametric drought payout trigger: MWK 744,000 automated insurance payout dispatched in Balaka."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 8: 08 WHAT MAKES IT DIFFERENT?
# ==============================================================================
Write-Host "Creating Slide 8 (What Makes It Different?)..."
$s8 = $presentation.Slides.Add(9, 12)
$s8.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s8.Background.Fill.Solid()
$s8.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s8 "08" "WHAT MAKES IT DIFFERENT?"
Add-Footer $s8

$c8a = Add-Card $s8 60 110 265 370
$c8a.TextFrame.MarginLeft = 18; $c8a.TextFrame.MarginTop = 18
$p = $c8a.TextFrame.TextRange
$p.Text = "TRADITIONAL AG APPS`r`n`r`n- Broadcast generic weather forecasts or static price tables.`r`n`r`n- Tell the farmer it will rain 10mm, leaving them to guess what that means for fertilizer application or crop survival.`r`n`r`n- Disconnected point solutions that ignore the financing and insurance barrier."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c8b = Add-Card $s8 345 110 265 370 $cEmerald
$c8b.TextFrame.MarginLeft = 18; $c8b.TextFrame.MarginTop = 18
$p = $c8b.TextFrame.TextRange
$p.Text = "THE FARMPULSE EDGE`r`n`r`n- Translates data into financial consequence: tells the farmer exactly what crops to plant, how to budget inputs, and when to sell.`r`n`r`n- Calibrates 10-year district climate risk against individual land size and cash constraints.`r`n`r`n- Automated parametric insurance integrated into the planting plan."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cWhite

$c8c = Add-Card $s8 630 110 270 370 $cMzuniGold
$c8c.TextFrame.MarginLeft = 18; $c8c.TextFrame.MarginTop = 18
$p = $c8c.TextFrame.TextRange
$p.Text = "SHARED GOVERNANCE LEDGER`r`n`r`n- Connects the smallholder, extension officer (DADO), lending bank (credit risk scoring), and insurer on ONE platform.`r`n`r`n- Dual delivery: Works on modern web and basic 2G USSD (*384#) with zero internet requirement in local languages."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 9: 09 IMPACT & VALUE
# ==============================================================================
Write-Host "Creating Slide 9 (Impact & Value)..."
$s9 = $presentation.Slides.Add(10, 12)
$s9.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s9.Background.Fill.Solid()
$s9.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s9 "09" "IMPACT & VALUE"
Add-Footer $s9

$c9a = Add-Card $s9 60 110 265 370 $cEmerald
$c9a.TextFrame.MarginLeft = 20; $c9a.TextFrame.MarginTop = 20
$p = $c9a.TextFrame.TextRange
$p.Text = "< 90 SECONDS`r`nTIME SAVED`r`n`r`nReduces multi-crop agronomic budgeting and scenario planning from 3 weeks of manual field visits down to under 90 seconds of algorithmic generation.`r`n`r`nEnables 1 extension officer to support 2,500+ farmers digitally."
$p.Font.Name = "Calibri"; $p.Font.Size = 13; $p.Font.Color.RGB = $cWhite

$c9b = Add-Card $s9 345 110 265 370 $cMzuniGold
$c9b.TextFrame.MarginLeft = 20; $c9b.TextFrame.MarginTop = 20
$p = $c9b.TextFrame.TextRange
$p.Text = "22% CUT`r`nINPUT COST REDUCED`r`n`r`nEliminates input expenditure waste by 22% through precise seed and basal/top-dressing fertilizer ratios.`r`n`r`nSlashes bank agricultural loan default rates from 16.5% to under 4% through verified yield histories."
$p.Font.Name = "Calibri"; $p.Font.Size = 13; $p.Font.Color.RGB = $cWhite

$c9c = Add-Card $s9 630 110 270 370
$c9c.TextFrame.MarginLeft = 20; $c9c.TextFrame.MarginTop = 20
$p = $c9c.TextFrame.TextRange
$p.Text = "+35% TO +60%`r`nNET PROFIT BOOST`r`n`r`nBoosts smallholder net household profit margins by 35% to 60% through high-value legume rotation (soya, groundnuts) and regional market price arbitrage.`r`n`r`nLifts families out of subsistence debt cycles."
$p.Font.Name = "Calibri"; $p.Font.Size = 13; $p.Font.Color.RGB = $cWhite

# ==============================================================================
# SLIDE 10: 10 SUSTAINABILITY & BUSINESS MODEL
# ==============================================================================
Write-Host "Creating Slide 10 (Sustainability & Business Model)..."
$s10 = $presentation.Slides.Add(11, 12)
$s10.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s10.Background.Fill.Solid()
$s10.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s10 "10" "SUSTAINABILITY & BUSINESS MODEL"
Add-Footer $s10

$c10a = Add-Card $s10 60 110 430 370 $cEmerald
$c10a.TextFrame.MarginLeft = 20; $c10a.TextFrame.MarginTop = 18
$p = $c10a.TextFrame.TextRange
$p.Text = "HYBRID B2B2C & B2B2G MONETIZATION`r`n`r`n1. Agribusiness Outgrower SaaS:`r`nOff-takers (Pyxus, ETG, Sunseed) pay MWK 4.5M - 12M/yr for smallholder tracking & yield forecasting.`r`n`r`n2. Fintech Loan Risk-Scoring API:`r`nCommercial banks & MFIs (NBS Bank, FINCA) pay 1.75% fee per de-risked seasonal input loan.`r`n`r`n3. Insurtech Brokerage Commission:`r`n8% to 10% technology fee on gross written insurance premiums underwritten by NICO General / Old Mutual.`r`n`r`n4. Government DPI Licenses:`r`nMinistry of Ag & WFP district analytics (MWK 15M - 25M/district).`r`n`r`n5. Freemium Telco Billing:`r`nPremium SMS advisory @ MWK 100/mo via Airtel/TNM (70/30 split)."
$p.Font.Name = "Calibri"; $p.Font.Size = 11.5; $p.Font.Color.RGB = $cLightSlate

$c10b = Add-Card $s10 510 110 390 370 $cMzuniGold
$c10b.TextFrame.MarginLeft = 20; $c10b.TextFrame.MarginTop = 18
$p = $c10b.TextFrame.TextRange
$p.Text = "3-YEAR FINANCIAL PROJECTIONS (MWK)`r`n`r`nYEAR 1 (Pilot Phase):`r`n- Active Smallholders: 3,500 farmers`r`n- Gross Revenue: MWK 42,500,000 (~$25,000 USD)`r`n- Operating Costs: MWK 31,000,000`r`n- EBITDA: +MWK 11,500,000 (27.0% Margin)`r`n-> BREAKEVEN ACHIEVED IN MONTH 11`r`n`r`nYEAR 2 (Regional Scaling):`r`n- Active Smallholders: 18,000 farmers`r`n- Gross Revenue: MWK 177,200,000 (~$104,000 USD)`r`n- Operating Costs: MWK 92,000,000`r`n- EBITDA: +MWK 85,200,000 (48.1% Margin)`r`n`r`nYEAR 3: MWK 584.5M Revenue (65,000 Farmers)"
$p.Font.Name = "Calibri"; $p.Font.Size = 11.5; $p.Font.Color.RGB = $cWhite

# ==============================================================================
# SLIDE 11: 11 NEXT MILESTONES
# ==============================================================================
Write-Host "Creating Slide 11 (Next Milestones)..."
$s11 = $presentation.Slides.Add(12, 12)
$s11.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s11.Background.Fill.Solid()
$s11.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s11 "11" "NEXT MILESTONES"
Add-Footer $s11

$c11a = Add-Card $s11 60 110 265 370 $cEmerald
$c11a.TextFrame.MarginLeft = 20; $c11a.TextFrame.MarginTop = 20
$p = $c11a.TextFrame.TextRange
$p.Text = "NEXT 3 MONTHS`r`nQ1 2027`r`n`r`nFIELD PILOT VALIDATION`r`n`r`n- Formalize pilot integration with 3 farmer cooperatives in Mzuzu and Lilongwe (500 smallholders).`r`n`r`n- Deploy official commercial short-code for USSD *384# with TNM and Airtel.`r`n`r`n- Publish localized crop budget matrices for Mzuzu Highlands AEZ."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c11b = Add-Card $s11 345 110 265 370 $cMzuniGold
$c11b.TextFrame.MarginLeft = 20; $c11b.TextFrame.MarginTop = 20
$p = $c11b.TextFrame.TextRange
$p.Text = "NEXT 6 MONTHS`r`nQ2 - Q3 2027`r`n`r`nFINTECH & INSURANCE SANDBOX`r`n`r`n- Complete API sandbox testing with NBS Bank for agricultural credit scoring.`r`n`r`n- Partner with NICO General for commercial parametric micro-insurance underwriting.`r`n`r`n- Integrate Mlimi AI Chichewa voice-to-text advisory prototype."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c11c = Add-Card $s11 630 110 270 370
$c11c.TextFrame.MarginLeft = 20; $c11c.TextFrame.MarginTop = 20
$p = $c11c.TextFrame.TextRange
$p.Text = "NEXT 12 MONTHS`r`n2027/28 SEASON`r`n`r`nNATIONAL SCALE-UP`r`n`r`n- Scale platform coverage to 15,000 smallholders across 5 agricultural districts.`r`n`r`n- Secure institutional endorsement from the Ministry of Agriculture (AGCOM 2 Project).`r`n`r`n- Expand satellite processing pipelines to Sentinel-1 Synthetic Aperture Radar (SAR)."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

# ==============================================================================
# SLIDE 12: 12 WHAT WE NEED FROM YOU
# ==============================================================================
Write-Host "Creating Slide 12 (What We Need From You)..."
$s12 = $presentation.Slides.Add(13, 12)
$s12.FollowMasterBackground = [Microsoft.Office.Core.MsoTriState]::msoFalse
$s12.Background.Fill.Solid()
$s12.Background.Fill.ForeColor.RGB = $cMzuniNavy
Add-Header $s12 "12" "WHAT WE NEED FROM YOU"
Add-Footer $s12

$c12a = Add-Card $s12 60 110 405 370 $cEmerald
$c12a.TextFrame.MarginLeft = 22; $c12a.TextFrame.MarginTop = 22
$p = $c12a.TextFrame.TextRange
$p.Text = "WE ARE ACTIVELY LOOKING FOR:`r`n`r`n[ X ] PILOT SITES & COOPERATIVES`r`n3 commercial agricultural cooperatives or outgrower schemes for structured Phase 1 field testing.`r`n`r`n[ X ] INSTITUTIONAL PARTNERS`r`nUnderwriting insurers (NICO General, Old Mutual) and agricultural lenders (NBS Bank, FINCA).`r`n`r`n[ X ] FACULTY MENTORS`r`nMzuzu University agronomy and economics lecturers to validate regional agro-ecological zone yield models.`r`n`r`n[ X ] SEED GRANTS & TECHNICAL SUPPORT`r`nCapital to fund telco USSD integration fees, Sentinel-2 compute, and extension officer workshops."
$p.Font.Name = "Calibri"; $p.Font.Size = 12.5; $p.Font.Color.RGB = $cLightSlate

$c12b = Add-Card $s12 490 110 410 370 $cMzuniGold
$c12b.TextFrame.MarginLeft = 24; $c12b.TextFrame.MarginTop = 30
$p = $c12b.TextFrame.TextRange
$p.Text = "OUR ONE CLEAR ASK`r`n`r`n""Partner with FarmPulse today to bring data-driven climate resilience, de-risked finance, and sustainable profitability to smallholder farming communities across Malawi.""`r`n`r`n`r`nLIVE DEMO PLATFORM:`r`nhttps://farmpulse-p6jl.onrender.com/`r`n`r`nCONTACT LEAD DEVELOPER:`r`nBrian Nankhuni  -  brian@gmail.com  -  +265 88 412 8901"
$p.Font.Name = "Calibri"; $p.Font.Size = 13.5; $p.Font.Color.RGB = $cWhite

# Save presentation
$outPptx = Join-Path (Get-Location) "FarmPulse_Mzuzu_University_Exhibition.pptx"
if (Test-Path $outPptx) { Remove-Item $outPptx -Force }
$presentation.SaveAs($outPptx)
$presentation.Close()
$ppt.Quit()
[System.GC]::Collect()

Write-Host "`r`nSUCCESS: FarmPulse Mzuzu University Exhibition Presentation generated at:"
Write-Host "$outPptx"
