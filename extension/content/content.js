// content.js — Mnemox Content Script
// Step 5: Auto Memory Injection — silently prepends relevant memories before every prompt

(function () {
  'use strict';

  var SITE_MAP = {
    'chat.openai.com':       'chatgpt',
    'chatgpt.com':           'chatgpt',
    'claude.ai':             'claude',
    'gemini.google.com':     'gemini',
    'copilot.microsoft.com': 'copilot',
  };

  var CURRENT_SITE = SITE_MAP[window.location.hostname];
  if (!CURRENT_SITE) return;
  console.log('[Mnemox] Active on ' + CURRENT_SITE);

  var settings = { captureEnabled: true, injectEnabled: true };
  var lastCaptured = '';
  var observer = null;
  var lastInjectedContext = '';  // track what we injected to avoid double-inject

  var SITE_CONFIG = {
    chatgpt: {
      promptSelector: '#prompt-textarea, textarea[data-id="root"]',
      submitSelector: 'button[data-testid="send-button"], button[aria-label="Send prompt"]',
      getPromptText: function(el) { return el.innerText || el.value || ''; },
      setPromptText: function(el, text) { setContentEditable(el, text); },
    },
    claude: {
      promptSelector: '.ProseMirror[contenteditable="true"], div[contenteditable="true"][data-placeholder]',
      submitSelector: 'button[aria-label="Send Message"], button[type="submit"]',
      getPromptText: function(el) { return el.innerText || ''; },
      setPromptText: function(el, text) { setContentEditable(el, text); },
    },
    gemini: {
      promptSelector: '.ql-editor[contenteditable="true"], rich-textarea .ql-editor',
      submitSelector: 'button.send-button, button[aria-label="Send message"]',
      getPromptText: function(el) { return el.innerText || ''; },
      setPromptText: function(el, text) { setContentEditable(el, text); },
    },
    copilot: {
      promptSelector: '#userInput, textarea[name="userInput"], div[contenteditable="true"][role="textbox"]',
      submitSelector: 'button[aria-label="Submit"], button[type="submit"]',
      getPromptText: function(el) { return el.innerText || el.value || ''; },
      setPromptText: function(el, text) {
        if (el.tagName === 'TEXTAREA') {
          el.value = text;
          el.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
          setContentEditable(el, text);
        }
      },
    },
  };

  var config = SITE_CONFIG[CURRENT_SITE];

  // ── Settings ────────────────────────────────────────────────────────────────
  function loadSettings() {
    return new Promise(function(resolve) {
      chrome.runtime.sendMessage({ type: 'MNEMOX_GET_SETTINGS' }, function(r) {
        if (r && r.success) settings = Object.assign({}, settings, r.settings);
        resolve();
      });
    });
  }

  // ── DOM text setter for contenteditable elements ──────────────────────────
  function setContentEditable(el, text) {
    el.focus();
    // Select all and replace
    var selection = window.getSelection();
    var range = document.createRange();
    range.selectNodeContents(el);
    selection.removeAllRanges();
    selection.addRange(range);
    // Use execCommand for compatibility — inserts as plain text
    document.execCommand('insertText', false, text);
    // Fallback: set innerText + fire React/Vue input events
    if (el.innerText !== text) {
      el.innerText = text;
      el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  // ── Build context block from memories ────────────────────────────────────
  function buildContextBlock(memories, originalPrompt) {
    if (!memories || memories.length === 0) return originalPrompt;

    var lines = ['[Mnemox Context — Your relevant memories]'];
    memories.forEach(function(m, i) {
      lines.push((i + 1) + '. ' + m.content_preview);
    });
    lines.push('[End Mnemox Context]');
    lines.push('');
    lines.push(originalPrompt);

    return lines.join('\n');
  }

  // ── Search memories via service worker → backend ─────────────────────────
  function searchMemories(promptText, callback) {
    chrome.runtime.sendMessage({
      type: 'MNEMOX_SEARCH_MEMORIES',
      payload: { query: promptText, limit: 5, score_threshold: 0.65 },
    }, function(response) {
      if (response && response.success && response.results && response.results.length > 0) {
        callback(response.results);
      } else {
        callback([]);
      }
    });
  }

  // ── Inject memories into prompt box ──────────────────────────────────────
  function injectMemoriesIntoPrompt(promptEl, originalText, callback) {
    if (!settings.injectEnabled) return callback(false);
    if (!originalText || originalText.trim().length < 3) return callback(false);

    searchMemories(originalText, function(memories) {
      if (!memories.length) return callback(false);

      var enriched = buildContextBlock(memories, originalText);

      // Only inject if content actually changed
      if (enriched === lastInjectedContext) return callback(false);
      lastInjectedContext = enriched;

      config.setPromptText(promptEl, enriched);
      console.log('[Mnemox] Injected ' + memories.length + ' memories into prompt');
      callback(true, memories.length);
    });
  }

  // ── Toast notification ───────────────────────────────────────────────────
  function injectToastStyles() {
    if (document.getElementById('mnemox-toast-style')) return;
    var style = document.createElement('style');
    style.id = 'mnemox-toast-style';
    style.textContent =
      '#mnemox-toast{position:fixed;bottom:24px;right:24px;z-index:2147483647;' +
      'background:#1a1a2e;border:1px solid #7c3aed;color:#e5e7eb;padding:10px 16px;' +
      'border-radius:10px;font-size:13px;display:flex;align-items:center;gap:8px;' +
      'box-shadow:0 4px 20px rgba(124,58,237,0.3);transform:translateY(80px);opacity:0;' +
      'transition:transform 0.3s ease,opacity 0.3s ease;pointer-events:none;max-width:300px;}' +
      '#mnemox-toast.show{transform:translateY(0);opacity:1;}' +
      '#mnemox-toast .mnemox-icon{font-size:16px;flex-shrink:0;}' +
      '#mnemox-toast .mnemox-sub{font-size:11px;color:#9ca3af;margin-top:1px;}';
    document.head.appendChild(style);
  }

  var toastTimer = null;
  function showToast(message, sub) {
    var toast = document.getElementById('mnemox-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'mnemox-toast';
      toast.innerHTML = '<span class="mnemox-icon">bolt</span><div><div id="mnemox-toast-text"></div><div class="mnemox-sub" id="mnemox-toast-sub"></div></div>';
      document.body.appendChild(toast);
    }
    document.getElementById('mnemox-toast-text').textContent = message;
    document.getElementById('mnemox-toast-sub').textContent = sub || '';
    clearTimeout(toastTimer);
    toast.classList.add('show');
    toastTimer = setTimeout(function() { toast.classList.remove('show'); }, 3000);
  }

  // ── Capture prompt ───────────────────────────────────────────────────────
  function capturePrompt(text) {
    if (!settings.captureEnabled) return;
    text = text.trim();
    // Strip injected context before saving — save only the user's original prompt
    var markerIdx = text.indexOf('[Mnemox Context');
    if (markerIdx === -1) markerIdx = text.indexOf('[End Mnemox Context]');
    if (markerIdx !== -1) {
      var endMarker = '[End Mnemox Context]\n\n';
      var endIdx = text.indexOf(endMarker);
      if (endIdx !== -1) text = text.slice(endIdx + endMarker.length).trim();
    }
    if (!text || text.length < 4) return;
    if (text === lastCaptured) return;
    lastCaptured = text;

    var stored = text.length > 1000 ? text.slice(0, 1000) + '...' : text;
    chrome.runtime.sendMessage({
      type: 'MNEMOX_MEMORY_CAPTURED',
      payload: { content: stored, source: CURRENT_SITE },
    }, function(response) {
      if (response && response.success) {
        var preview = text.slice(0, 45) + (text.length > 45 ? '...' : '');
        showToast('Memory saved', '"' + preview + '"');
      }
    });
  }

  // ── Find prompt element ──────────────────────────────────────────────────
  function findPromptEl() {
    var selectors = config.promptSelector.split(', ');
    for (var i = 0; i < selectors.length; i++) {
      var el = document.querySelector(selectors[i].trim());
      if (el) return el;
    }
    return null;
  }

  // ── Wire prompt: capture + inject on submit ──────────────────────────────
  function attachPromptListeners(promptEl) {
    if (promptEl._mnemoxAttached) return;
    promptEl._mnemoxAttached = true;
    console.log('[Mnemox] Prompt wired on ' + CURRENT_SITE);

    // Set right before we programmatically click the submit button after
    // injection, so the submit-button click listener below (which also
    // fires on THIS synthetic click, since it's a real DOM click event)
    // knows capture was already handled for this message and skips its own
    // redundant, racier re-capture attempt.
    var mnemoxOwnClick = false;

    promptEl.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        var text = config.getPromptText(promptEl).trim();
        if (!text || text.length < 3) return;

        // Step 1: capture original prompt.
        // 2026-07-09 fix: this used to re-read config.getPromptText(promptEl)
        // live, 80ms later, instead of using the 'text' snapshot already
        // captured synchronously above. On Claude specifically, the prompt
        // box (a ProseMirror contenteditable) can get cleared or mutated
        // well before that 80ms timeout fires -- by our own injection logic
        // rewriting the box, or by Claude's own send handling -- so the
        // delayed re-read intermittently captured an empty string and
        // capturePrompt() silently aborted (it returns early when
        // text.length < 4). Using the already-known-good 'text' snapshot
        // makes capture immune to any DOM mutation that happens afterward.
        setTimeout(function() { capturePrompt(text); }, 80);

        // Step 2: inject memories BEFORE submit
        if (settings.injectEnabled) {
          e.preventDefault();   // pause submit
          e.stopPropagation();

          injectMemoriesIntoPrompt(promptEl, text, function(injected, count) {
            if (injected) {
              showToast(count + ' memories added to context', 'AI now knows your history');
            }
            // Resume submit after injection (or skip if no memories)
            setTimeout(function() {
              var submitSelectors = config.submitSelector.split(', ');
              for (var i = 0; i < submitSelectors.length; i++) {
                var btn = document.querySelector(submitSelectors[i].trim());
                if (btn) {
                  mnemoxOwnClick = true;
                  btn.click();
                  mnemoxOwnClick = false;
                  break;
                }
              }
            }, 120);
          });
        } else {
          // Injection disabled — just capture
          setTimeout(function() { capturePrompt(text); }, 50);
        }
      }
    }, true);  // capture phase — runs before AI tool's own listeners

    // Also wire submit button (for mouse clicks)
    config.submitSelector.split(', ').forEach(function(sel) {
      var btn = document.querySelector(sel.trim());
      if (btn && !btn._mnemoxAttached) {
        btn._mnemoxAttached = true;
        btn.addEventListener('click', function() {
          // Skip -- the keydown handler above already captured this message
          // (with a reliable pre-mutation snapshot) before triggering this
          // synthetic click as part of the injection flow.
          if (mnemoxOwnClick) return;
          var text = config.getPromptText(promptEl).trim();
          setTimeout(function() { capturePrompt(text); }, 80);
        });
      }
    });
  }

  // ── MutationObserver: handles SPA re-renders ─────────────────────────────
  function startObserver() {
    if (observer) return;
    var el = findPromptEl();
    if (el) attachPromptListeners(el);

    observer = new MutationObserver(function() {
      var found = findPromptEl();
      if (found) attachPromptListeners(found);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    console.log('[Mnemox] MutationObserver active on ' + CURRENT_SITE);
  }

  // ── Messages from popup ──────────────────────────────────────────────────
  chrome.runtime.onMessage.addListener(function(message) {
    if (message.type === 'MNEMOX_SETTINGS_CHANGED') {
      settings = Object.assign({}, settings, message);
    }
    if (message.type === 'MNEMOX_SAVE_NOW') {
      var el = findPromptEl();
      capturePrompt(el ? config.getPromptText(el) : '[' + CURRENT_SITE + '] ' + document.title);
    }
  });

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {
    loadSettings().then(function() {
      injectToastStyles();
      startObserver();
      chrome.runtime.sendMessage({ type: 'MNEMOX_PING' }, function(r) {
        console.log('[Mnemox] SW: ' + (r && r.status));
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
