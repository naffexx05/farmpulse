/**
 * FarmPulse Malawi - Universal Audio Voiceover & Chichewa Oral Accessibility
 * Features:
 * - Natural text-to-speech oral advisories for smallholder farmers and AEDO officers
 * - Chichewa and English voice synthesis
 * - Animated visual equalizer waves during active audio playback
 * - Bilingual transcript modal support
 */

(function () {
  'use strict';

  let currentUtterance = null;
  let activeAudioBtn = null;

  function stopSpeaking() {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    if (activeAudioBtn) {
      resetButtonUI(activeAudioBtn);
      activeAudioBtn = null;
    }
    currentUtterance = null;
  }

  function resetButtonUI(btn) {
    const originalText = btn.getAttribute('data-original-html');
    if (originalText) {
      btn.innerHTML = originalText;
    }
    btn.classList.remove('ring-2', 'ring-leaf', 'bg-leaf/20');
  }

  function speakText(text, lang = 'ch', btn = null) {
    if (!window.speechSynthesis) {
      alert("Text-to-speech audio is not supported in this browser.");
      return;
    }

    // Toggle off if already speaking the same button
    if (activeAudioBtn === btn && window.speechSynthesis.speaking) {
      stopSpeaking();
      return;
    }

    stopSpeaking();

    // Play subtle audio cue first
    if (window.FarmPulseSound) {
      window.FarmPulseSound.playChime();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.92; // Slightly measured pace for maximum clarity
    utterance.pitch = 1.0;

    // Pick best available voice (African / South African or English / fallback)
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.lang.startsWith('en-ZA') || v.lang.startsWith('en-GB') || v.lang.startsWith('en-US')) || voices[0];
    if (voice) utterance.voice = voice;

    if (btn) {
      activeAudioBtn = btn;
      if (!btn.getAttribute('data-original-html')) {
        btn.setAttribute('data-original-html', btn.innerHTML);
      }
      btn.classList.add('ring-2', 'ring-leaf', 'bg-leaf/20');
      btn.innerHTML = `
        <span class="inline-flex items-center gap-1">
          <span class="fp-eq-bar"></span>
          <span class="fp-eq-bar"></span>
          <span class="fp-eq-bar"></span>
          <span class="fp-eq-bar"></span>
        </span>
        <span class="text-xs font-bold text-leaf ml-1">Kuyankhula... (Speaking)</span>
      `;
    }

    utterance.onend = function () {
      if (btn) resetButtonUI(btn);
      activeAudioBtn = null;
      currentUtterance = null;
    };

    utterance.onerror = function () {
      if (btn) resetButtonUI(btn);
      activeAudioBtn = null;
      currentUtterance = null;
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  }

  // Auto-bind click handlers for elements with data-speak attributes
  document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
      const btn = e.target.closest('[data-fp-speak]');
      if (!btn) return;
      e.preventDefault();

      const text = btn.getAttribute('data-fp-speak') || btn.innerText;
      const lang = btn.getAttribute('data-lang') || 'ch';
      speakText(text, lang, btn);
    });
  });

  window.FarmPulseAudio = {
    speak: speakText,
    stop: stopSpeaking
  };
})();
