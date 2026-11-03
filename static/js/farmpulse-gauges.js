/**
 * FarmPulse Malawi - Visual Profit Speedometer & Breakeven Bag Stackers
 * Transforms financial spreadsheets into intuitive visual instruments.
 */

(function () {
  'use strict';

  function renderSpeedometer(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const value = options.value || 0;
    const min = options.min !== undefined ? options.min : -20;
    const max = options.max !== undefined ? options.max : 80;
    const unit = options.unit || '% ROI';
    const label = options.label || 'Profitability Meter';

    // Clamp value between min and max
    const clamped = Math.max(min, Math.min(max, value));
    const percentage = (clamped - min) / (max - min);

    // Speedometer angle from -135deg (extreme loss) to +135deg (peak profit)
    const angle = -135 + (percentage * 270);

    const isProfit = value > 0;
    const statusColor = value < 0 ? '#E76A6A' : (value < 15 ? '#F2B441' : '#8FCB62');
    const statusText = value < 0 ? 'Loss Territory' : (value < 15 ? 'Break-Even Zone' : 'High Profit Margin');

    container.innerHTML = `
      <div class="flex flex-col items-center justify-center p-3 text-center">
        <div class="relative w-48 h-28 overflow-hidden">
          <svg viewBox="0 0 200 120" class="w-full h-full">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#E76A6A" />
                <stop offset="35%" stop-color="#F2B441" />
                <stop offset="70%" stop-color="#8FCB62" />
                <stop offset="100%" stop-color="#4FB7D9" />
              </linearGradient>
            </defs>
            <!-- Background track -->
            <path d="M 25 105 A 75 75 0 0 1 175 105" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="14" stroke-linecap="round" />
            <!-- Gradient active arc -->
            <path d="M 25 105 A 75 75 0 0 1 175 105" fill="none" stroke="url(#gaugeGradient)" stroke-width="12" stroke-linecap="round" stroke-dasharray="235" stroke-dashoffset="0" />
            <!-- Center Pivot Pin -->
            <circle cx="100" cy="105" r="7" fill="#F1F5EC" />
            <!-- Needle -->
            <g class="fp-gauge-needle" style="transform-origin: 100px 105px; transform: rotate(${angle}deg);">
              <polygon points="98,105 102,105 100,32" fill="#F1F5EC" />
            </g>
          </svg>
        </div>
        <div class="mt-1">
          <div class="text-2xl font-black tracking-tight" style="color: ${statusColor};">
            ${value > 0 ? '+' : ''}${value}${unit}
          </div>
          <div class="text-xs font-semibold uppercase tracking-wider text-cream/70">${label}</div>
          <div class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold" style="background-color: ${statusColor}22; color: ${statusColor};">
            ${statusText}
          </div>
        </div>
      </div>
    `;
  }

  function renderBreakevenBags(containerId, totalBags = 40, costBags = 14) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const profitBags = Math.max(0, totalBags - costBags);
    const displayTotal = Math.min(30, totalBags); // Cap visual icons for screen space
    const costRatio = Math.round((costBags / totalBags) * displayTotal);

    let bagIconsHtml = '';
    for (let i = 0; i < displayTotal; i++) {
      const isCost = i < costRatio;
      const color = isCost ? '#F2B441' : '#8FCB62';
      const tooltip = isCost ? 'Input & Labour Cost Bag' : 'Pure Profit Bag';
      bagIconsHtml += `
        <span title="${tooltip}" class="inline-flex items-center justify-center p-1 rounded hover:scale-125 transition-transform cursor-pointer" style="color: ${color};">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 7h-3V6a4 44 0 0 0-8 0v1H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zm-9-1a2 2 0 0 1 4 0v1h-4V6z"/>
          </svg>
        </span>
      `;
    }

    container.innerHTML = `
      <div class="space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="text-muted">Total Yield: <strong class="text-cream">${totalBags} bags (50kg)</strong></span>
          <span class="text-leaf font-bold">${profitBags} Bags Net Profit</span>
        </div>
        <div class="p-3 rounded-xl bg-forest-900/60 border border-white/5 flex flex-wrap gap-1 items-center justify-center">
          ${bagIconsHtml}
        </div>
        <div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
          <div class="p-2 rounded-lg bg-amber-400/10 border border-amber-400/20 text-amber-300">
            <div class="font-bold">Cost Recovery (${costBags} bags)</div>
            <div class="text-[10px] opacity-80">Seeds, NPK, Urea, Labour</div>
          </div>
          <div class="p-2 rounded-lg bg-leaf/10 border border-leaf/20 text-leaf">
            <div class="font-bold">Surplus Profit (${profitBags} bags)</div>
            <div class="text-[10px] opacity-80">Take-home revenue</div>
          </div>
        </div>
      </div>
    `;
  }

  window.FarmPulseGauges = {
    renderSpeedometer: renderSpeedometer,
    renderBreakevenBags: renderBreakevenBags
  };
})();
