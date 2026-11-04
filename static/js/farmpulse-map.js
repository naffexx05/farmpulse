/**
 * FarmPulse Malawi - Interactive Geospatial Command Map
 * Features:
 * - Leaflet integration with theme-aware tile switching (Dark Matter vs Positron)
 * - 8 DCCMS Agro-meteorological telemetry stations with live rain & temp popups
 * - 5 Major AMIS agricultural trading hubs with Farmgate / Wholesale / Retail spreads
 * - Animated spatial arbitrage highway flow routes (Mitundu -> Limbe, Chinkhoma -> Mchesi)
 * - Layer filter toggles and interactive route detail inspection
 */

(function () {
  'use strict';

  const STATIONS = [
    { id: 'chitedze', name: 'Chitedze Agromet Station', district: 'Lilongwe', lat: -13.98, lng: 33.64, rain14d: 68.4, temp: 27.5, status: 'Planting Window Open', risk: 'low', type: 'climate' },
    { id: 'kasungu', name: 'Kasungu Research Station', district: 'Kasungu', lat: -13.03, lng: 33.48, rain14d: 42.1, temp: 28.2, status: 'Approaching Window', risk: 'medium', type: 'climate' },
    { id: 'salima', name: 'Salima Meteorological Station', district: 'Salima', lat: -13.78, lng: 34.45, rain14d: 18.0, temp: 31.8, status: '7-Day Dry Spell Alert', risk: 'high', type: 'climate' },
    { id: 'bvumbwe', name: 'Bvumbwe Research Station', district: 'Thyolo', lat: -15.92, lng: 35.07, rain14d: 84.6, temp: 24.1, status: 'Optimal Moisture', risk: 'low', type: 'climate' },
    { id: 'makoka', name: 'Makoka Agricultural Station', district: 'Zomba', lat: -15.53, lng: 35.18, rain14d: 55.2, temp: 25.8, status: 'Good Planting Conditions', risk: 'low', type: 'climate' },
    { id: 'mzimba', name: 'Mzimba Agromet Post', district: 'Mzimba', lat: -11.90, lng: 33.60, rain14d: 36.5, temp: 26.4, status: 'Normal Seasonal', risk: 'medium', type: 'climate' },
    { id: 'karonga', name: 'Karonga Lake Shore Post', district: 'Karonga', lat: -9.93, lng: 33.93, rain14d: 22.0, temp: 33.4, status: 'High Heat Advisory', risk: 'medium', type: 'climate' },
    { id: 'ngabu', name: 'Ngabu Lower Shire Post', district: 'Chikwawa', lat: -16.48, lng: 34.95, rain14d: 12.3, temp: 35.7, status: 'Severe Drought Warning', risk: 'high', type: 'climate' }
  ];

  const MARKETS = [
    { id: 'mitundu', name: 'Mitundu Rural Market', district: 'Lilongwe Rural', lat: -14.18, lng: 33.78, farmgate: 350, wholesale: 480, retail: 580, crop: 'White Maize', type: 'market' },
    { id: 'mchesi', name: 'Mchesi Wholesale Hub', district: 'Lilongwe City', lat: -13.97, lng: 33.79, farmgate: 420, wholesale: 520, retail: 650, crop: 'White Maize', type: 'market' },
    { id: 'chinkhoma', name: 'Chinkhoma Grain Depot', district: 'Kasungu', lat: -13.02, lng: 33.52, farmgate: 320, wholesale: 460, retail: 560, crop: 'White Maize', type: 'market' },
    { id: 'lunzu', name: 'Lunzu Trading Center', district: 'Blantyre Rural', lat: -15.68, lng: 35.03, farmgate: 460, wholesale: 550, retail: 700, crop: 'White Maize', type: 'market' },
    { id: 'limbe', name: 'Limbe Central Market', district: 'Blantyre Urban', lat: -15.82, lng: 35.06, farmgate: 490, wholesale: 580, retail: 740, crop: 'White Maize', type: 'market' }
  ];

  const ARBITRAGE_ROUTES = [
    {
      id: 'mitundu-limbe',
      origin: 'Mitundu Rural',
      destination: 'Limbe Central',
      distanceKm: 312,
      buyPrice: 350,
      sellPrice: 580,
      transportCost: 45,
      netMargin: 185,
      roi: 44.5,
      recommendation: 'HIGH PROFIT ARBITRAGE',
      points: [
        [-14.18, 33.78],
        [-14.35, 33.95],
        [-14.75, 34.35],
        [-15.05, 34.70],
        [-15.45, 34.98],
        [-15.82, 35.06]
      ]
    },
    {
      id: 'chinkhoma-mchesi',
      origin: 'Chinkhoma Depot',
      destination: 'Mchesi Hub',
      distanceKm: 128,
      buyPrice: 320,
      sellPrice: 520,
      transportCost: 35,
      netMargin: 165,
      roi: 38.2,
      recommendation: 'RECOMMENDED HAUL',
      points: [
        [-13.02, 33.52],
        [-13.35, 33.62],
        [-13.68, 33.72],
        [-13.97, 33.79]
      ]
    },
    {
      id: 'mitundu-lunzu',
      origin: 'Mitundu Rural',
      destination: 'Lunzu Trading',
      distanceKm: 295,
      buyPrice: 350,
      sellPrice: 550,
      transportCost: 42,
      netMargin: 158,
      roi: 36.8,
      recommendation: 'STRONG MARGIN',
      points: [
        [-14.18, 33.78],
        [-14.70, 34.30],
        [-15.20, 34.80],
        [-15.68, 35.03]
      ]
    }
  ];

  class FarmPulseMap {
    constructor(containerId, options = {}) {
      this.containerId = containerId;
      this.options = Object.assign({
        center: [-13.25, 34.2],
        zoom: 7,
        interactive: true,
        showStations: true,
        showMarkets: true,
        showRoutes: true
      }, options);

      this.map = null;
      this.tileLayer = null;
      this.stationMarkers = [];
      this.marketMarkers = [];
      this.routePolylines = [];
      this.activeFilter = 'all';

      this.init();
    }

    init() {
      const container = document.getElementById(this.containerId);
      if (!container || !window.L) return;

      // Initialize Leaflet map
      this.map = L.map(this.containerId, {
        center: this.options.center,
        zoom: this.options.zoom,
        zoomControl: true,
        scrollWheelZoom: false,
        attributionControl: false
      });

      // Add Tile Layer based on active theme
      this.updateTileLayer();

      // Listen for theme change events to switch tiles
      window.addEventListener('farmpulse:themechange', () => this.updateTileLayer());

      // Render layers
      if (this.options.showStations) this.renderStations();
      if (this.options.showMarkets) this.renderMarkets();
      if (this.options.showRoutes) this.renderRoutes();

      // Invalidate size once rendered
      setTimeout(() => this.map.invalidateSize(), 250);
    }

    updateTileLayer() {
      if (!this.map) return;
      const isSunlight = document.documentElement.classList.contains('theme-sunlight');
      const tileUrl = isSunlight
        ? 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

      if (this.tileLayer) {
        this.map.removeLayer(this.tileLayer);
      }

      this.tileLayer = L.tileLayer(tileUrl, {
        maxZoom: 18,
        subdomains: 'abcd'
      }).addTo(this.map);
    }

    createPinIcon(type, riskOrColor) {
      const color = type === 'climate'
        ? (riskOrColor === 'low' ? '#4FB7D9' : (riskOrColor === 'medium' ? '#F2B441' : '#E76A6A'))
        : '#8FCB62';

      const iconSvg = type === 'climate'
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/><path d="M2 7h20"/></svg>`;

      return L.divIcon({
        className: 'fp-custom-pin-wrapper',
        html: `
          <div class="fp-map-pin relative" style="width: 28px; height: 28px; background-color: #0A3325; border: 2px solid ${color}; display: flex; align-items: center; justify-content: center; border-radius: 50%;">
            <span class="fp-pulse-ring" style="color: ${color};"></span>
            ${iconSvg}
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -16]
      });
    }

    renderStations() {
      STATIONS.forEach(station => {
        const icon = this.createPinIcon('climate', station.risk);
        const marker = L.marker([station.lat, station.lng], { icon }).addTo(this.map);

        const riskBadge = station.risk === 'low'
          ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-leaf/20 text-leaf">Low Risk</span>'
          : (station.risk === 'medium'
            ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-400/20 text-amber-300">Moderate</span>'
            : '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-risk-high/20 text-risk-high">High Alert</span>');

        const popupContent = `
          <div class="p-2 space-y-1.5 text-xs max-w-[210px]">
            <div class="flex items-center justify-between gap-1">
              <strong class="font-bold text-cream">${station.name}</strong>
              ${riskBadge}
            </div>
            <div class="text-[11px] text-muted">${station.district} District</div>
            <div class="grid grid-cols-2 gap-2 pt-1 border-t border-white/10 text-[11px]">
              <div>14d Rain: <strong class="text-water font-semibold">${station.rain14d} mm</strong></div>
              <div>Temp: <strong class="text-amber-300 font-semibold">${station.temp}°C</strong></div>
            </div>
            <div class="text-[10px] pt-1 text-leaf font-medium">${station.status}</div>
          </div>
        `;

        marker.bindPopup(popupContent);
        this.stationMarkers.push(marker);
      });
    }

    renderMarkets() {
      MARKETS.forEach(market => {
        const icon = this.createPinIcon('market', '#8FCB62');
        const marker = L.marker([market.lat, market.lng], { icon }).addTo(this.map);

        const popupContent = `
          <div class="p-2 space-y-1.5 text-xs max-w-[210px]">
            <div class="flex items-center justify-between gap-1">
              <strong class="font-bold text-cream">${market.name}</strong>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-leaf/20 text-leaf">Trading Hub</span>
            </div>
            <div class="text-[11px] text-muted">${market.crop} · ${market.district}</div>
            <div class="space-y-1 pt-1 border-t border-white/10 text-[11px]">
              <div class="flex justify-between"><span>Farmgate:</span> <strong class="text-amber-400 font-semibold">${market.farmgate} MWK/kg</strong></div>
              <div class="flex justify-between"><span>Wholesale:</span> <strong class="text-leaf font-semibold">${market.wholesale} MWK/kg</strong></div>
              <div class="flex justify-between"><span>Retail:</span> <strong class="text-cream font-semibold">${market.retail} MWK/kg</strong></div>
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);
        this.marketMarkers.push(marker);
      });
    }

    renderRoutes() {
      ARBITRAGE_ROUTES.forEach(route => {
        const polyline = L.polyline(route.points, {
          color: '#8FCB62',
          weight: 4,
          opacity: 0.85,
          className: 'fp-animated-route'
        }).addTo(this.map);

        polyline.on('click', () => {
          if (window.FarmPulseSound) window.FarmPulseSound.playChime();
          this.displayRouteDetails(route);
        });

        polyline.bindTooltip(`
          <div class="text-xs font-bold text-leaf">${route.origin} → ${route.destination}</div>
          <div class="text-[10px] text-cream">+${route.netMargin} MWK/kg Net Gain (${route.roi}% ROI)</div>
        `, { sticky: true });

        this.routePolylines.push(polyline);
      });
    }

    displayRouteDetails(route) {
      const panel = document.getElementById('map-route-detail-panel');
      if (!panel) return;

      panel.classList.remove('hidden');
      panel.innerHTML = `
        <div class="fp-card p-4 border-leaf/40 bg-gradient-to-r from-forest-800 to-forest-850 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-leaf uppercase tracking-wider">${route.recommendation}</span>
              <span class="text-xs text-muted">· ${route.distanceKm} km via M1</span>
            </div>
            <h4 class="text-base font-bold text-cream">${route.origin} to ${route.destination}</h4>
            <p class="text-xs text-cream/70">
              Buy at village farmgate (${route.buyPrice} MWK/kg) → Haul freight (${route.transportCost} MWK/kg) → Sell at city depot (${route.sellPrice} MWK/kg).
            </p>
          </div>
          <div class="flex items-center gap-6 shrink-0 bg-forest-900/60 px-4 py-2.5 rounded-xl border border-white/5">
            <div>
              <div class="text-[10px] text-muted uppercase">Net Profit Margin</div>
              <div class="text-lg font-black text-leaf">+${route.netMargin} <span class="text-xs font-normal">MWK/kg</span></div>
            </div>
            <div>
              <div class="text-[10px] text-muted uppercase">Projected ROI</div>
              <div class="text-lg font-black text-amber-400">+${route.roi}%</div>
            </div>
            <a href="/market/" class="fp-btn-primary text-xs py-1.5 px-3">
              Book Freight & Sell →
            </a>
          </div>
        </div>
      `;
    }

    setFilter(filter) {
      this.activeFilter = filter;
      if (window.FarmPulseSound) window.FarmPulseSound.playClick();

      // Stations
      this.stationMarkers.forEach(m => {
        if (filter === 'all' || filter === 'stations') this.map.addLayer(m);
        else this.map.removeLayer(m);
      });

      // Markets
      this.marketMarkers.forEach(m => {
        if (filter === 'all' || filter === 'markets') this.map.addLayer(m);
        else this.map.removeLayer(m);
      });

      // Routes
      this.routePolylines.forEach(p => {
        if (filter === 'all' || filter === 'routes') this.map.addLayer(p);
        else this.map.removeLayer(p);
      });
    }
  }

  // Global factory function
  window.initFarmPulseMap = function (containerId, options) {
    return new FarmPulseMap(containerId, options);
  };
})();
