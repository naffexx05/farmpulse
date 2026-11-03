/**
 * FarmPulse Malawi - Theme, Sound FX & Offline Telemetry Engine
 * Supports:
 * - "Midnight Forest" (dark OLED/field night) vs "Sunlight Field Mode" (high-contrast glare-resistant daylight)
 * - Live Network Telemetry (Online AMIS / Offline Cached Field Mode)
 * - Micro-Audio Synthesizer (Web Audio API tactile feedback for sliders, buttons, and arbitrage profit alerts)
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. Theme Engine (Sunlight Field Mode vs Midnight Forest)
  // =========================================================================
  const THEME_STORAGE_KEY = 'farmpulse-theme';

  function applyTheme(theme) {
    const root = document.documentElement;
    if (theme === 'sunlight') {
      root.classList.add('theme-sunlight');
      root.setAttribute('data-theme', 'sunlight');
    } else {
      root.classList.remove('theme-sunlight');
      root.setAttribute('data-theme', 'forest');
    }

    // Update theme toggle button UI if it exists
    updateThemeToggleUI(theme);

    // Dispatch event for components that need tile reload (e.g. Leaflet map)
    window.dispatchEvent(new CustomEvent('farmpulse:themechange', { detail: { theme } }));
  }

  function getStoredTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY) || 'forest';
  }

  function toggleTheme() {
    const current = getStoredTheme();
    const next = current === 'sunlight' ? 'forest' : 'sunlight';
    localStorage.setItem(THEME_STORAGE_KEY, next);
    applyTheme(next);
    FarmPulseSound.playClick();
  }

  function updateThemeToggleUI(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    const isSunlight = theme === 'sunlight';
    btn.setAttribute('aria-label', isSunlight ? 'Switch to Midnight Forest Mode' : 'Switch to Sunlight Field Mode');
    btn.setAttribute('title', isSunlight ? 'Switch to Midnight Forest (Low Glare)' : 'Switch to Sunlight Field Mode (Direct Sun)');

    const icon = btn.querySelector('[data-lucide]');
    if (icon) {
      icon.setAttribute('data-lucide', isSunlight ? 'moon' : 'sun');
      if (window.lucide) lucide.createIcons();
    }
    const label = btn.querySelector('.theme-label');
    if (label) {
      label.textContent = isSunlight ? 'Forest' : 'Sunlight';
    }
  }

  // Apply immediately before DOM render to prevent FOUC
  const savedTheme = getStoredTheme();
  applyTheme(savedTheme);

  // =========================================================================
  // 2. Synthesized Web Audio Micro-FX (Zero external assets required)
  // =========================================================================
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;
  let soundEnabled = localStorage.getItem('farmpulse-sound') !== 'false';

  function getAudioContext() {
    if (!audioCtx && AudioCtx) {
      audioCtx = new AudioCtx();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  window.FarmPulseSound = {
    isEnabled: () => soundEnabled,
    toggleSound: () => {
      soundEnabled = !soundEnabled;
      localStorage.setItem('farmpulse-sound', soundEnabled ? 'true' : 'false');
      if (soundEnabled) FarmPulseSound.playChime();
      return soundEnabled;
    },
    // Gentle tactile click
    playClick: () => {
      if (!soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.04);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.045);
      } catch (e) {}
    },
    // Positive harvest / profit chime (pleasant chord)
    playChime: () => {
      if (!soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
        notes.forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.06);
          gain.gain.setValueAtTime(0.06, ctx.currentTime + i * 0.06);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.06 + 0.25);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.06);
          osc.stop(ctx.currentTime + i * 0.06 + 0.26);
        });
      } catch (e) {}
    },
    // Alert / Dry spell warning tone
    playWarning: () => {
      if (!soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.setValueAtTime(330, ctx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.05, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.28);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.29);
      } catch (e) {}
    }
  };

  // =========================================================================
  // 3. Live Telemetry & Network Sync Status
  // =========================================================================
  function updateNetworkPill() {
    const pill = document.getElementById('network-telemetry-pill');
    if (!pill) return;
    const isOnline = navigator.onLine;

    if (isOnline) {
      pill.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all bg-leaf/15 text-leaf border-leaf/30';
      pill.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full bg-leaf animate-pulse"></span>
        <span class="hidden md:inline">Live Connected</span>
        <span class="text-[10px] text-cream/60 hidden lg:inline">AMIS/DCCMS</span>
      `;
    } else {
      pill.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all bg-amber-400/20 text-amber-300 border-amber-400/40';
      pill.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
        <span>Offline Field Mode</span>
        <span class="text-[10px] opacity-80 hidden lg:inline">(Cached)</span>
      `;
    }
  }

  // =========================================================================
  // 4. Initialization
  // =========================================================================
  document.addEventListener('DOMContentLoaded', function () {
    updateThemeToggleUI(getStoredTheme());
    updateNetworkPill();

    // Attach click listener to theme button
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
      btn.addEventListener('click', toggleTheme);
    }

    // Attach sound toggle if present
    const soundBtn = document.getElementById('sound-toggle-btn');
    if (soundBtn) {
      soundBtn.addEventListener('click', function () {
        const enabled = FarmPulseSound.toggleSound();
        const icon = soundBtn.querySelector('[data-lucide]');
        if (icon) {
          icon.setAttribute('data-lucide', enabled ? 'volume-2' : 'volume-x');
          if (window.lucide) lucide.createIcons();
        }
      });
    }

    // Attach network listeners
    window.addEventListener('online', updateNetworkPill);
    window.addEventListener('offline', updateNetworkPill);
  });

  // Expose global controller
  window.FarmPulseTheme = {
    toggle: toggleTheme,
    apply: applyTheme,
    get: getStoredTheme
  };
})();
