/**
 * FarmPulse Malawi — Frontend Enhancement Suite v3.0
 * National Presentation Edition
 *
 * Modules:
 *  1. Page Entrance Animations (IntersectionObserver stagger)
 *  2. Animated Number Counters (KPI stat values)
 *  3. Animated Progress Bars
 *  4. Card Hover Lift System
 *  5. Button Ripple Effect
 *  6. Market Price Ticker Strip
 *  7. Mlimi AI Typing Effect
 *  8. Session Transcript Download
 *  9. Sunlight Mode Body Fix
 * 10. Gradient Border Cards
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. Page Entrance Animations
  // =========================================================================
  function initEntranceAnimations() {
    const style = document.createElement('style');
    style.textContent = `
      .fp-animate-in {
        opacity: 0;
        transform: translateY(14px);
        transition: opacity 0.42s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.42s cubic-bezier(0.22, 1, 0.36, 1);
      }
      .fp-animate-in.fp-visible {
        opacity: 1;
        transform: translateY(0);
      }
      .fp-animate-in[data-delay="1"] { transition-delay: 0.06s; }
      .fp-animate-in[data-delay="2"] { transition-delay: 0.12s; }
      .fp-animate-in[data-delay="3"] { transition-delay: 0.18s; }
      .fp-animate-in[data-delay="4"] { transition-delay: 0.24s; }
      .fp-animate-in[data-delay="5"] { transition-delay: 0.30s; }
      .fp-animate-in[data-delay="6"] { transition-delay: 0.36s; }
    `;
    document.head.appendChild(style);

    // Auto-mark cards, stat blocks, tables
    const selectors = [
      '.fp-card', '.fp-stat', 'table.fp-table',
      '.fp-kpi', '[class*="fp-badge"]'
    ];
    document.querySelectorAll(selectors.join(',')).forEach(function (el, i) {
      if (!el.classList.contains('fp-no-animate')) {
        el.classList.add('fp-animate-in');
        const delay = Math.min(i % 6 + 1, 6);
        el.setAttribute('data-delay', delay);
      }
    });

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('fp-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });

    document.querySelectorAll('.fp-animate-in').forEach(function (el) {
      observer.observe(el);
    });
  }

  // =========================================================================
  // 2. Animated Number Counters
  // =========================================================================
  function animateNumber(el) {
    var raw = el.getAttribute('data-fp-counter');
    if (!raw) return;
    var target = parseFloat(raw.replace(/,/g, ''));
    if (isNaN(target)) return;

    var prefix = el.getAttribute('data-fp-prefix') || '';
    var suffix = el.getAttribute('data-fp-suffix') || '';
    var decimals = parseInt(el.getAttribute('data-fp-decimals') || '0', 10);
    var duration = 900;
    var start = performance.now();

    function tick(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = target * eased;
      var formatted = decimals > 0
        ? value.toFixed(decimals)
        : Math.round(value).toLocaleString();
      el.textContent = prefix + formatted + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function initCounters() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateNumber(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    document.querySelectorAll('[data-fp-counter]').forEach(function (el) {
      observer.observe(el);
    });
  }

  // =========================================================================
  // 3. Animated Progress Bars
  // =========================================================================
  function initProgressBars() {
    var bars = document.querySelectorAll('[data-fp-bar]');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var bar = entry.target;
          var target = parseFloat(bar.getAttribute('data-fp-bar') || '0');
          bar.style.width = '0%';
          setTimeout(function () {
            bar.style.transition = 'width 0.9s cubic-bezier(0.22, 1, 0.36, 1)';
            bar.style.width = Math.min(target, 100) + '%';
          }, 80);
          observer.unobserve(bar);
        }
      });
    }, { threshold: 0.2 });

    bars.forEach(function (bar) { observer.observe(bar); });
  }

  // =========================================================================
  // 4. Card Hover Lift
  // =========================================================================
  function initCardHover() {
    var style = document.createElement('style');
    style.textContent = `
      .fp-card {
        transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.22s cubic-bezier(0.22, 1, 0.36, 1),
                    border-color 0.22s ease;
      }
      .fp-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3) !important;
      }
      html.theme-sunlight .fp-card:hover {
        box-shadow: 0 8px 24px rgba(10,41,26,0.12), 0 2px 6px rgba(10,41,26,0.08) !important;
      }
    `;
    document.head.appendChild(style);
  }

  // =========================================================================
  // 5. Button Ripple Effect
  // =========================================================================
  function initRipple() {
    var style = document.createElement('style');
    style.textContent = `
      .fp-btn-primary, .fp-btn-outline {
        position: relative;
        overflow: hidden;
      }
      .fp-ripple {
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: fp-ripple-anim 0.5s linear;
        background: rgba(255,255,255,0.22);
        pointer-events: none;
      }
      @keyframes fp-ripple-anim {
        to { transform: scale(4); opacity: 0; }
      }
    `;
    document.head.appendChild(style);

    function addRipple(e) {
      var btn = e.currentTarget;
      var rect = btn.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height);
      var ripple = document.createElement('span');
      ripple.className = 'fp-ripple';
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      btn.appendChild(ripple);
      setTimeout(function () { ripple.remove(); }, 500);
    }

    document.querySelectorAll('.fp-btn-primary, .fp-btn-outline').forEach(function (btn) {
      btn.addEventListener('click', addRipple);
    });
  }

  // =========================================================================
  // 6. Market Price Ticker Strip
  // =========================================================================
  function initTicker() {
    var container = document.getElementById('fp-market-ticker');
    if (!container) return;

    var style = document.createElement('style');
    style.textContent = `
      .fp-ticker-track {
        display: flex;
        gap: 0;
        animation: fp-ticker-scroll 42s linear infinite;
        white-space: nowrap;
      }
      .fp-ticker-track:hover { animation-play-state: paused; }
      @keyframes fp-ticker-scroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
      }
      .fp-ticker-sep {
        display: inline-flex;
        align-items: center;
        margin: 0 1.5rem;
        color: rgba(255,255,255,0.15);
      }
      html.theme-sunlight .fp-ticker-sep { color: rgba(10,41,26,0.15); }
    `;
    document.head.appendChild(style);

    // Fetch prices via Django URL encoded in the data attribute
    var apiUrl = container.getAttribute('data-src');
    if (!apiUrl) return;

    fetch(apiUrl)
      .then(function (r) { return r.json(); })
      .catch(function () { return null; })
      .then(function (data) {
        if (!data || !data.prices) return;
        var items = data.prices.map(function (p) {
          var dir = p.change >= 0 ? '+' : '';
          var color = p.change >= 0 ? '#8FCB62' : '#EF4444';
          return (
            '<span class="inline-flex items-center gap-2 px-2 text-[11px] font-semibold">' +
            '<span class="text-cream/50 font-normal text-[10px]">' + p.crop + '</span>' +
            '<span class="font-mono text-cream" style="letter-spacing:0.02em">MWK ' + Number(p.price).toLocaleString() + '</span>' +
            '<span style="color:' + color + ';font-size:10px">' + dir + p.change + '%</span>' +
            '</span>'
          );
        });
        var sep = '<span class="fp-ticker-sep">|</span>';
        var inner = items.join(sep);
        // Duplicate for seamless loop
        container.innerHTML =
          '<div class="fp-ticker-track">' + inner + sep + inner + sep + '</div>';
      });
  }

  // =========================================================================
  // 7. Mlimi AI Typing Effect
  // =========================================================================
  window.FarmPulseType = {
    type: function (el, text, speed) {
      speed = speed || 18;
      el.textContent = '';
      var i = 0;
      var cursor = document.createElement('span');
      cursor.className = 'fp-type-cursor';
      el.appendChild(cursor);

      // Inject cursor blink style once
      if (!document.getElementById('fp-type-style')) {
        var s = document.createElement('style');
        s.id = 'fp-type-style';
        s.textContent = '.fp-type-cursor{display:inline-block;width:2px;height:1em;background:currentColor;margin-left:1px;vertical-align:text-bottom;animation:fp-blink 1s step-end infinite;opacity:0.7;}@keyframes fp-blink{0%,100%{opacity:0.7}50%{opacity:0}}';
        document.head.appendChild(s);
      }

      function tick() {
        if (i < text.length) {
          el.insertBefore(document.createTextNode(text[i]), cursor);
          i++;
          setTimeout(tick, speed + (Math.random() * 12));
        } else {
          setTimeout(function () { cursor.remove(); }, 800);
        }
      }
      tick();
    }
  };

  // =========================================================================
  // 8. Advisory Download (Mlimi AI page)
  // =========================================================================
  function initAdvisoryDownload() {
    var btn = document.getElementById('fp-download-advisory');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var messages = document.querySelectorAll('[data-advisory-line]');
      if (!messages.length) return;
      var lines = [];
      lines.push('FarmPulse Malawi — Mlimi AI Advisory Transcript');
      lines.push('Generated: ' + new Date().toLocaleString('en-MW'));
      lines.push('='.repeat(60));
      lines.push('');
      messages.forEach(function (m) {
        lines.push(m.getAttribute('data-role') === 'user' ? 'FARMER:' : 'MLIMI AI:');
        lines.push(m.textContent.trim());
        lines.push('');
      });
      var blob = new Blob([lines.join('\n')], { type: 'text/plain' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'mlimi-advisory-' + Date.now() + '.txt';
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // =========================================================================
  // 9. Sunlight Mode — Body Tailwind Class Override
  //    The <body> has hardcoded Tailwind class `bg-forest-900`.
  //    This patch ensures sunlight mode properly overrides it.
  // =========================================================================
  function patchSunlightBody() {
    function applyBodyPatch(theme) {
      var body = document.body;
      if (!body) return;
      if (theme === 'sunlight') {
        body.setAttribute('data-theme', 'sunlight');
        body.style.backgroundColor = '#F4F6F3';
        body.style.color = '#111827';
      } else {
        body.removeAttribute('data-theme');
        body.style.backgroundColor = '';
        body.style.color = '';
      }
    }

    // Apply on theme change
    window.addEventListener('farmpulse:themechange', function (e) {
      applyBodyPatch(e.detail.theme);
    });

    // Apply once DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        var stored = localStorage.getItem('farmpulse-theme') || 'forest';
        applyBodyPatch(stored);
      });
    } else {
      var stored = localStorage.getItem('farmpulse-theme') || 'forest';
      applyBodyPatch(stored);
    }
  }

  // =========================================================================
  // 10. Gradient Border Cards — apply to .fp-card-gradient elements
  // =========================================================================
  function initGradientBorders() {
    var style = document.createElement('style');
    style.textContent = `
      .fp-card-gradient {
        position: relative;
        background: linear-gradient(145deg, #0F2214 0%, #142C1A 100%);
        border: none !important;
      }
      .fp-card-gradient::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(135deg, rgba(143,203,98,0.4) 0%, rgba(96,165,250,0.2) 50%, rgba(143,203,98,0.1) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: destination-out;
        mask-composite: exclude;
        pointer-events: none;
      }
      html.theme-sunlight .fp-card-gradient {
        background: linear-gradient(145deg, #FFFFFF 0%, #F5F9F5 100%);
      }
      html.theme-sunlight .fp-card-gradient::before {
        background: linear-gradient(135deg, rgba(61,122,20,0.35) 0%, rgba(79,183,217,0.2) 50%, rgba(61,122,20,0.1) 100%);
      }
    `;
    document.head.appendChild(style);
  }

  // =========================================================================
  // 11. Topbar scroll shadow
  // =========================================================================
  function initTopbarScrollShadow() {
    var header = document.querySelector('header');
    if (!header) return;
    window.addEventListener('scroll', function () {
      if (window.scrollY > 8) {
        header.style.boxShadow = '0 4px 24px rgba(0,0,0,0.35)';
      } else {
        header.style.boxShadow = '';
      }
    }, { passive: true });
  }

  // =========================================================================
  // 12. Active nav item glow
  // =========================================================================
  function initNavGlow() {
    var style = document.createElement('style');
    style.textContent = `
      .fp-nav-item-active {
        box-shadow: inset 3px 0 0 var(--fp-green) !important;
      }
      .fp-nav-item {
        transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
      }
    `;
    document.head.appendChild(style);
  }

  // =========================================================================
  // 13. Focus visible ring (accessibility)
  // =========================================================================
  function initFocusRing() {
    var style = document.createElement('style');
    style.textContent = `
      :focus-visible {
        outline: 2px solid var(--fp-green) !important;
        outline-offset: 2px !important;
      }
    `;
    document.head.appendChild(style);
  }

  // =========================================================================
  // Init
  // =========================================================================
  // Run immediately (before DOMContentLoaded) for FOUC prevention
  patchSunlightBody();

  document.addEventListener('DOMContentLoaded', function () {
    initEntranceAnimations();
    initCounters();
    initProgressBars();
    initCardHover();
    initRipple();
    initTicker();
    initAdvisoryDownload();
    initGradientBorders();
    initTopbarScrollShadow();
    initNavGlow();
    initFocusRing();
  });

})();

