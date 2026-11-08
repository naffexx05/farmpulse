/**
 * FarmPulse Malawi - Interactive Field Land Splitter Canvas
 * Enables smallholder farmers and agricultural officers to visually partition
 * a farm plot in real-time with 60 FPS financial and food security feedback.
 */

(function () {
  'use strict';

  class FieldSplitter {
    constructor(config) {
      this.totalLandHa = config.totalLandHa || 2.0;
      this.seasonalBudgetMwk = config.seasonalBudgetMwk || 450000;
      this.benchmarks = config.benchmarks || {};
      this.selectedCrops = config.selectedCrops || ['maize', 'groundnuts', 'soybeans'];
      this.districtSlug = config.districtSlug || 'lilongwe';
      
      // Default initial allocations
      this.allocations = {};
      this.isLocked = {};

      this.initAllocations();
    }

    initAllocations() {
      // Ensure at least staple maize + one legume if available
      const crops = this.selectedCrops.filter(slug => this.benchmarks[slug]);
      if (crops.length === 0) return;

      const hasMaize = crops.includes('maize');
      if (hasMaize && crops.length > 1) {
        const maizeShare = 0.55;
        this.allocations['maize'] = Math.round((this.totalLandHa * maizeShare) * 100) / 100;
        const remainder = Math.max(0, this.totalLandHa - this.allocations['maize']);
        const otherCrops = crops.filter(c => c !== 'maize');
        const sharePerOther = Math.round((remainder / otherCrops.length) * 100) / 100;

        otherCrops.forEach((c, idx) => {
          if (idx === otherCrops.length - 1) {
            // absorb rounding delta
            const allocatedSoFar = this.allocations['maize'] + (sharePerOther * (otherCrops.length - 1));
            this.allocations[c] = Math.max(0, Math.round((this.totalLandHa - allocatedSoFar) * 100) / 100);
          } else {
            this.allocations[c] = sharePerOther;
          }
        });
      } else {
        const equalShare = Math.round((this.totalLandHa / crops.length) * 100) / 100;
        crops.forEach(c => this.allocations[c] = equalShare);
      }
    }

    setCropArea(slug, areaHa) {
      areaHa = Math.max(0, Math.min(this.totalLandHa, parseFloat(areaHa) || 0));
      this.allocations[slug] = Math.round(areaHa * 100) / 100;
      if (window.FarmPulseSound) window.FarmPulseSound.playClick();
      this.render();
    }

    setSelectedCrops(newCropSlugs) {
      if (!Array.isArray(newCropSlugs)) return;
      const validCrops = newCropSlugs.filter(slug => this.benchmarks[slug]);
      if (validCrops.length === 0) return;

      this.selectedCrops = validCrops;

      // Remove allocations for deselected crops
      Object.keys(this.allocations).forEach(slug => {
        if (!validCrops.includes(slug)) {
          delete this.allocations[slug];
          delete this.isLocked[slug];
        }
      });

      // Retained crops that are still selected
      const retainedCrops = Object.keys(this.allocations);

      if (retainedCrops.length === 0) {
        // All crops changed, full re-init
        this.initAllocations();
      } else {
        const newlyAdded = validCrops.filter(slug => !retainedCrops.includes(slug));
        if (newlyAdded.length > 0) {
          let retainedTotal = 0;
          retainedCrops.forEach(slug => retainedTotal += (this.allocations[slug] || 0));
          let remainingLand = Math.max(0, this.totalLandHa - retainedTotal);

          if (remainingLand >= 0.1) {
            // Allocate remaining land across newly added crops
            const share = Math.round((remainingLand / newlyAdded.length) * 100) / 100;
            newlyAdded.forEach((slug, idx) => {
              if (idx === newlyAdded.length - 1) {
                const allocated = share * (newlyAdded.length - 1);
                this.allocations[slug] = Math.max(0.05, Math.round((remainingLand - allocated) * 100) / 100);
              } else {
                this.allocations[slug] = share;
              }
            });
          } else {
            // Rebalance so all crops get a meaningful slice
            this.initAllocations();
          }
        }
      }

      this.render();
    }

    setTotalLand(landHa) {
      const parsed = parseFloat(landHa);
      if (isNaN(parsed) || parsed <= 0) return;
      this.totalLandHa = Math.round(parsed * 100) / 100;
      this.initAllocations();
      this.render();
    }

    setSeasonalBudget(budgetMwk) {
      const parsed = parseFloat(budgetMwk);
      if (isNaN(parsed) || parsed < 0) return;
      this.seasonalBudgetMwk = Math.round(parsed);
      this.render();
    }

    adjustCropArea(slug, delta) {
      const current = this.allocations[slug] || 0;
      this.setCropArea(slug, current + delta);
    }

    toggleLock(slug) {
      this.isLocked[slug] = !this.isLocked[slug];
      if (window.FarmPulseSound) window.FarmPulseSound.playClick();
      this.render();
    }

    applyPreset(presetKey) {
      const crops = Object.keys(this.allocations);
      const hasMaize = crops.includes('maize');
      const otherCrops = crops.filter(c => c !== 'maize');

      if (presetKey === 'food_security') {
        // 70% Maize, 30% Legumes
        if (hasMaize) {
          this.allocations['maize'] = Math.round(this.totalLandHa * 0.70 * 100) / 100;
          const rem = this.totalLandHa - this.allocations['maize'];
          if (otherCrops.length > 0) {
            const each = Math.round((rem / otherCrops.length) * 100) / 100;
            otherCrops.forEach(c => this.allocations[c] = each);
          }
        }
      } else if (presetKey === 'balanced') {
        // 50% Maize, remaining evenly split
        if (hasMaize) {
          this.allocations['maize'] = Math.round(this.totalLandHa * 0.50 * 100) / 100;
          const rem = this.totalLandHa - this.allocations['maize'];
          if (otherCrops.length > 0) {
            const each = Math.round((rem / otherCrops.length) * 100) / 100;
            otherCrops.forEach(c => this.allocations[c] = each);
          }
        } else {
          this.autoBalance();
        }
      } else if (presetKey === 'cash_crop') {
        // 35% Maize, 65% Cash
        if (hasMaize) {
          this.allocations['maize'] = Math.round(this.totalLandHa * 0.35 * 100) / 100;
          const rem = this.totalLandHa - this.allocations['maize'];
          if (otherCrops.length > 0) {
            const each = Math.round((rem / otherCrops.length) * 100) / 100;
            otherCrops.forEach(c => this.allocations[c] = each);
          }
        }
      } else if (presetKey === 'equal') {
        const each = Math.round((this.totalLandHa / crops.length) * 100) / 100;
        crops.forEach(c => this.allocations[c] = each);
      }

      if (window.FarmPulseSound) window.FarmPulseSound.playChime();
      this.render();
    }

    autoBalance() {
      const crops = Object.keys(this.allocations);
      const unlockedCrops = crops.filter(c => !this.isLocked[c]);
      if (unlockedCrops.length === 0) return;

      let lockedArea = 0;
      crops.filter(c => this.isLocked[c]).forEach(c => lockedArea += this.allocations[c]);

      const available = Math.max(0, this.totalLandHa - lockedArea);
      const share = Math.round((available / unlockedCrops.length) * 100) / 100;

      unlockedCrops.forEach(c => {
        this.allocations[c] = share;
      });

      if (window.FarmPulseSound) window.FarmPulseSound.playClick();
      this.render();
    }

    calculateTotals() {
      let totalAllocatedHa = 0;
      let totalCostMwk = 0;
      let totalRevenueMwk = 0;
      let stapleHarvestKg = 0;
      let legumeAreaHa = 0;
      let totalBags50kg = 0;

      const items = [];

      for (const [slug, areaHa] of Object.entries(this.allocations)) {
        if (areaHa <= 0) continue;
        const bm = this.benchmarks[slug];
        if (!bm) continue;

        totalAllocatedHa += areaHa;
        const cost = areaHa * bm.cost_ha_mwk;
        const yieldKg = areaHa * bm.yield_kg_ha;
        const rev = yieldKg * bm.price_kg_mwk;
        const margin = rev - cost;
        const bePrice = yieldKg > 0 ? (cost / yieldKg) : 0;

        totalCostMwk += cost;
        totalRevenueMwk += rev;
        totalBags50kg += Math.round(yieldKg / 50);

        if (bm.is_staple) {
          stapleHarvestKg += yieldKg;
        } else {
          legumeAreaHa += areaHa;
        }

        items.push({
          slug,
          name: bm.name,
          category: bm.category,
          areaHa,
          cost,
          yieldKg,
          rev,
          margin,
          bePrice: Math.round(bePrice),
          color: bm.color || '#8FCB62'
        });
      }

      const totalMarginMwk = totalRevenueMwk - totalCostMwk;
      const roiPct = totalCostMwk > 0 ? Math.round((totalMarginMwk / totalCostMwk) * 100) : 0;
      
      // Staple Food Security (Malawi standard subsistence requirement = 1,200 kg per family / year)
      const foodSecurityPct = Math.min(200, Math.round((stapleHarvestKg / 1200) * 100));

      // Agro-Ecological Alignment Score & Climate Resilience Score (0-100)
      let aezWeightedScore = 0;
      const marginalWarnings = [];
      for (const item of items) {
        const bm = this.benchmarks[item.slug];
        if (bm) {
          const score = bm.regional_suitability_score || 75;
          aezWeightedScore += score * (item.areaHa / Math.max(0.01, totalAllocatedHa));
          if (bm.regional_suitability_tier === 'marginal' && item.areaHa > 0) {
            marginalWarnings.push(`${bm.name} (${item.areaHa.toFixed(1)} ha): ${bm.regional_rationale || 'Elevated agro-ecological risk in this zone'}`);
          }
        }
      }
      const aezScore = Math.min(100, Math.round(aezWeightedScore || 80));

      // Composite Resilience Score: Rewards legume rotation, drought tolerance, diversification & AEZ fit
      let resilienceScore = 40;
      if (totalAllocatedHa > 0) {
        const legumeRatio = legumeAreaHa / totalAllocatedHa;
        resilienceScore += Math.round(legumeRatio * 30);
        if (items.length >= 2) resilienceScore += 10;
        if (items.length >= 3) resilienceScore += 5;
        // Blend in AEZ match (40% weight)
        resilienceScore = Math.round((resilienceScore * 0.6) + (aezScore * 0.4));
      }
      resilienceScore = Math.min(100, resilienceScore);

      // Cost Breakeven in 50kg bags
      const avgPricePerBag = totalBags50kg > 0 ? (totalRevenueMwk / totalBags50kg) : 25000;
      const costBags = Math.round(totalCostMwk / avgPricePerBag);

      return {
        totalAllocatedHa: Math.round(totalAllocatedHa * 100) / 100,
        totalCostMwk: Math.round(totalCostMwk),
        totalRevenueMwk: Math.round(totalRevenueMwk),
        totalMarginMwk: Math.round(totalMarginMwk),
        roiPct,
        foodSecurityPct,
        resilienceScore,
        aezScore,
        marginalWarnings,
        stapleHarvestKg: Math.round(stapleHarvestKg),
        totalBags50kg,
        costBags,
        items
      };
    }

    render() {
      const totals = this.calculateTotals();

      // 1. Render Visual Parcel Strip
      const stripContainer = document.getElementById('field-parcel-strip');
      if (stripContainer) {
        if (totals.totalAllocatedHa === 0) {
          stripContainer.innerHTML = `
            <div class="h-full flex items-center justify-center text-xs text-cream/40 italic">
              Adjust sliders below to allocate crops across your ${this.totalLandHa} ha field.
            </div>
          `;
        } else {
          let segmentsHtml = '';
          totals.items.forEach(item => {
            const pct = Math.max(4, Math.round((item.areaHa / this.totalLandHa) * 100));
            segmentsHtml += `
              <div 
                class="h-full flex flex-col justify-center px-2 text-forest-950 font-bold text-xs truncate transition-all duration-300 relative group"
                style="width: ${pct}%; background-color: ${item.color};"
                title="${item.name}: ${item.areaHa} ha (${pct}%)"
              >
                <div class="truncate flex items-center gap-1">
                  <span>${item.name}</span>
                  <span class="text-[10px] opacity-75 font-mono">${item.areaHa} ha</span>
                </div>
              </div>
            `;
          });

          // Unallocated space
          if (totals.totalAllocatedHa < this.totalLandHa) {
            const unallocHa = Math.round((this.totalLandHa - totals.totalAllocatedHa) * 100) / 100;
            const unallocPct = Math.round((unallocHa / this.totalLandHa) * 100);
            segmentsHtml += `
              <div 
                class="h-full flex items-center justify-center text-[10px] text-cream/40 font-mono bg-white/[0.03] border-l border-dashed border-white/20 transition-all duration-300"
                style="width: ${unallocPct}%;"
                title="Unallocated: ${unallocHa} ha"
              >
                ${unallocHa} ha unallocated
              </div>
            `;
          }
          stripContainer.innerHTML = segmentsHtml;
        }
      }

      // 2. Render Allocation Progress Bar & Land Status
      const landStatusEl = document.getElementById('splitter-land-status');
      if (landStatusEl) {
        const isExact = Math.abs(totals.totalAllocatedHa - this.totalLandHa) < 0.05;
        const isOver = totals.totalAllocatedHa > this.totalLandHa;
        const color = isExact ? 'text-leaf' : (isOver ? 'text-risk-high' : 'text-amber-300');
        const badge = isExact 
          ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-leaf/20 text-leaf">100% Fully Allocated</span>'
          : (isOver 
            ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-risk-high/20 text-risk-high">+${Math.round((totals.totalAllocatedHa - this.totalLandHa)*100)/100} ha Over Capacity</span>`
            : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400/20 text-amber-300">${Math.round((this.totalLandHa - totals.totalAllocatedHa)*100)/100} ha Remaining</span>`);
        
        landStatusEl.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <span class="text-cream/80">Field Partition: <strong class="${color} font-mono">${totals.totalAllocatedHa} ha</strong> / ${this.totalLandHa} ha</span>
            ${badge}
          </div>
        `;
      }

      // 3. Render Crop Sliders & Row Controls
      const controlsContainer = document.getElementById('splitter-controls-container');
      if (controlsContainer) {
        let rowsHtml = '';
        const crops = Object.keys(this.allocations);

        crops.forEach(slug => {
          const bm = this.benchmarks[slug];
          if (!bm) return;
          const area = this.allocations[slug] || 0;
          const isStaple = bm.is_staple;
          const locked = this.isLocked[slug];

          const suitBadge = bm.regional_suitability_tier === 'optimal'
            ? `<span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">Recommended</span>`
            : (bm.regional_suitability_tier === 'suitable'
              ? `<span class="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">Suitable</span>`
              : `<span class="text-[9px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-medium border border-rose-500/30" title="${bm.regional_rationale || ''}">Marginal Risk</span>`);

          const varietyTag = bm.regional_varieties ? `<span class="text-[9px] text-cream/40 font-mono">Seed: ${bm.regional_varieties.split(',')[0]}</span>` : '';

          rowsHtml += `
            <div class="p-3.5 rounded-xl bg-forest-900/60 border border-white/5 space-y-2">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full shrink-0" style="background-color: ${bm.color};"></span>
                  <div>
                    <div class="flex items-center gap-1.5">
                      <strong class="text-xs text-cream font-semibold">${bm.name}</strong>
                      ${suitBadge}
                    </div>
                    ${varietyTag}
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button 
                    type="button" 
                    onclick="window.farmPulseSplitter.toggleLock('${slug}')"
                    class="p-1 rounded text-cream/50 hover:text-cream transition-colors"
                    title="${locked ? 'Unlock allocation' : 'Lock allocation during auto-balance'}"
                  >
                    <i data-lucide="${locked ? 'lock' : 'unlock'}" class="w-3.5 h-3.5 ${locked ? 'text-amber-400' : ''}"></i>
                  </button>
                  <div class="flex items-center gap-1">
                    <button 
                      type="button" 
                      onclick="window.farmPulseSplitter.adjustCropArea('${slug}', -0.1)"
                      class="w-6 h-6 rounded bg-forest-800 text-cream text-xs font-bold hover:bg-forest-700 transition-colors"
                    >-</button>
                    <span class="font-mono text-xs font-bold text-cream w-12 text-center">${area.toFixed(1)} ha</span>
                    <button 
                      type="button" 
                      onclick="window.farmPulseSplitter.adjustCropArea('${slug}', 0.1)"
                      class="w-6 h-6 rounded bg-forest-800 text-cream text-xs font-bold hover:bg-forest-700 transition-colors"
                    >+</button>
                  </div>
                </div>
              </div>

              <!-- Range Slider -->
              <div class="flex items-center gap-3">
                <input 
                  type="range" 
                  min="0" 
                  max="${this.totalLandHa}" 
                  step="0.05" 
                  value="${area}"
                  oninput="window.farmPulseSplitter.setCropArea('${slug}', this.value)"
                  class="w-full accent-leaf h-1.5 bg-forest-800 rounded-lg cursor-pointer"
                />
                <span class="font-mono text-[11px] text-cream/60 w-10 text-right">${Math.round((area / this.totalLandHa)*100)}%</span>
              </div>

              <!-- Micro Breakdown -->
              <div class="grid grid-cols-3 gap-2 pt-1 border-t border-white/5 text-[10px] font-mono text-cream/70">
                <div>Est Cost: <strong class="text-cream">${Math.round(area * bm.cost_ha_mwk).toLocaleString()} MWK</strong></div>
                <div>Harvest: <strong class="text-cream">${Math.round(area * bm.yield_kg_ha).toLocaleString()} kg</strong></div>
                <div class="text-right">Break-Even: <strong class="text-amber-300">${bm.break_even_price_mwk} MWK/kg</strong></div>
              </div>
            </div>
          `;
        });

        controlsContainer.innerHTML = rowsHtml;
        if (window.lucide) lucide.createIcons();
      }

      // 4. Update Financial HUD & Metric Displays
      const costEl = document.getElementById('splitter-total-cost');
      if (costEl) costEl.textContent = 'MWK ' + totals.totalCostMwk.toLocaleString();

      const budgetDiffEl = document.getElementById('splitter-budget-diff');
      if (budgetDiffEl) {
        const diff = this.seasonalBudgetMwk - totals.totalCostMwk;
        if (diff >= 0) {
          budgetDiffEl.textContent = `Within Budget (+MWK ${diff.toLocaleString()} liquidity reserve)`;
          budgetDiffEl.className = 'text-[11px] text-leaf font-medium';
        } else {
          budgetDiffEl.textContent = `Exceeds Budget (-MWK ${Math.abs(diff).toLocaleString()} deficit)`;
          budgetDiffEl.className = 'text-[11px] text-risk-high font-medium';
        }
      }

      const revEl = document.getElementById('splitter-total-revenue');
      if (revEl) revEl.textContent = 'MWK ' + totals.totalRevenueMwk.toLocaleString();

      const marginEl = document.getElementById('splitter-total-margin');
      if (marginEl) {
        marginEl.textContent = 'MWK ' + totals.totalMarginMwk.toLocaleString();
        marginEl.className = 'font-display text-2xl font-bold font-mono ' + (totals.totalMarginMwk >= 0 ? 'text-leaf' : 'text-risk-high');
      }

      // 5. Update Speedometer & Breakeven Bag visualizers
      if (window.FarmPulseGauges) {
        window.FarmPulseGauges.renderSpeedometer('splitter-profit-speedometer', {
          value: totals.roiPct,
          min: -30,
          max: 90,
          unit: '% ROI',
          label: 'Field Profitability'
        });

        window.FarmPulseGauges.renderBreakevenBags(
          'splitter-breakeven-bags',
          Math.max(10, totals.totalBags50kg),
          Math.max(3, totals.costBags)
        );
      }

      // 6. Food Security & Climate Resilience HUD
      const foodSecEl = document.getElementById('splitter-food-security');
      if (foodSecEl) {
        const meetsSubsistence = totals.stapleHarvestKg >= 1200;
        foodSecEl.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <span class="text-cream/80">Staple Family Reserve: <strong class="${meetsSubsistence ? 'text-leaf' : 'text-amber-400'}">${totals.stapleHarvestKg.toLocaleString()} kg</strong></span>
            <span class="font-bold text-xs ${meetsSubsistence ? 'text-leaf' : 'text-amber-400'}">${totals.foodSecurityPct}% of 12-mo Needs</span>
          </div>
          <div class="w-full bg-forest-950 rounded-full h-2 mt-1.5 overflow-hidden">
            <div class="h-full rounded-full ${meetsSubsistence ? 'bg-leaf' : 'bg-amber-400'}" style="width: ${Math.min(100, totals.foodSecurityPct)}%;"></div>
          </div>
        `;
      }

      const resilienceEl = document.getElementById('splitter-resilience-score');
      if (resilienceEl) {
        const badgeEl = document.getElementById('splitter-resilience-badge');
        if (badgeEl) {
          if (totals.marginalWarnings && totals.marginalWarnings.length > 0) {
            badgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30';
            badgeEl.innerHTML = `<i data-lucide="alert-triangle" class="w-3 h-3 inline mr-1 text-amber-400"></i>AEZ Fit: <span id="splitter-resilience-score">${totals.resilienceScore}/100</span>`;
          } else {
            badgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-leaf/20 text-leaf border border-leaf/30';
            badgeEl.innerHTML = `<i data-lucide="shield-check" class="w-3 h-3 inline mr-1 text-leaf"></i>AEZ Fit: <span id="splitter-resilience-score">${totals.resilienceScore}/100</span>`;
          }
          if (window.lucide) lucide.createIcons();
        } else {
          resilienceEl.textContent = `${totals.resilienceScore}/100`;
        }
      }

      // 7. Update Hidden Form Data for "Save Plan"
      const hiddenInput = document.getElementById('custom-allocations-json-input');
      if (hiddenInput) {
        const payload = totals.items.map(i => ({
          slug: i.slug,
          area_ha: i.areaHa
        }));
        hiddenInput.value = JSON.stringify(payload);
      }

      // 8. Update Chichewa Oral Voiceover text
      const voiceBtn = document.getElementById('splitter-voice-btn');
      if (voiceBtn) {
        const chichewaText = `Ndondomeko yanu ya munda: Mwagawa maeka ${totals.totalAllocatedHa} pa malo okwana maeka ${this.totalLandHa}. Ndalama zofunika poyambira ndi Kwacha ${totals.totalCostMwk.toLocaleString()}. Mukakolola, phindu lanu loyembekezeka ndi Kwacha ${totals.totalMarginMwk.toLocaleString()}. Mbewu ya chakudya idzakwanira mabanja anu pa zana limodzi mwa zana.`;
        voiceBtn.setAttribute('data-fp-speak', chichewaText);
      }

      // 9. Sync with Real Input Cost Ledger if active
      if (typeof window.updateLedgerLandAreas === 'function' && totals.items) {
        const areaMap = {};
        totals.items.forEach(i => {
          areaMap[i.slug] = i.areaHa;
        });
        window.updateLedgerLandAreas(areaMap);
      }
    }
  }

  window.initFarmPulseSplitter = function (config) {
    const splitter = new FieldSplitter(config);
    window.farmPulseSplitter = splitter;
    splitter.render();
    return splitter;
  };
})();

