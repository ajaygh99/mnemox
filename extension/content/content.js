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
  var observerTimer = null;
  var lastInjectedContext = '';  // track what we injected to avoid double-inject
  var mnemoxOwnClick = false;
  // Prompt submission must never depend indefinitely on extension/backend
  // availability. This is the total time allowed for memory lookup.
  var INJECTION_BUDGET_MS = 350;
  var POST_INJECTION_SETTLE_MS = 20;
  var extensionContextInvalidated = false;

  var SITE_CONFIG = {
    chatgpt: {
      promptSelector: '#prompt-textarea, textarea[data-id="root"]',
      submitSelector: 'button[data-testid="send-button"], button[aria-label="Send prompt"]',
      getPromptText: function(el) { return el.innerText || el.value || ''; },
      setPromptText: function(el, text) { setContentEditable(el, text); },
    },
    claude: {
      // 2026-07-09 fix: the old selectors stopped matching Claude's current
      // UI entirely -- confirmed live via console: "No submit button
      // matched" AND every capture read an empty string. CSS attribute
      // selectors are case-sensitive by default; 'aria-label="Send Message"'
      // (capital M) most likely no longer matches Claude's actual label
      // ("Send message", lowercase, or something else entirely by now).
      // Broadened to case-insensitive (the trailing "i" flag) plus several
      // more resilient fallback patterns (data-testid, partial match on
      // "send") so a future minor label wording change doesn't silently
      // break capture again the same way.
      promptSelector: '.ProseMirror[contenteditable="true"], div[contenteditable="true"][data-placeholder], div[contenteditable="true"][aria-label*="message" i], div[contenteditable="true"][aria-label*="reply" i]',
      submitSelector: 'button[aria-label="Send Message" i], button[aria-label*="send" i], button[data-testid="send-button"], button[data-testid*="send" i], button[type="submit"]',
      getPromptText: function(el) {
        // Fallback chain: .innerText can read empty on some contenteditable
        // implementations (e.g. if the element is display:none at read
        // time, or text lives in a nested node .innerText doesn't walk the
        // way we expect). Try progressively less-precise reads before
        // giving up.
        var text = el.innerText || el.textContent || '';
        if (!text.trim()) {
          var p = el.querySelector('p, span, div');
          if (p) text = p.innerText || p.textContent || '';
        }
        return text;
      },
      setPromptText: function(el, text) { setContentEditable(el, text); },
    },
    gemini: {
      promptSelector: '.ql-editor[contenteditable="true"], rich-textarea .ql-editor',
      // 2026-07-10 fix: the old "button.send-button, button[aria-label=
      // \"Send message\"]" selector stopped matching anything on Gemini's
      // current UI -- confirmed live via chrome://extensions Errors panel:
      // "[Mnemox] No submit button matched on gemini for selector:
      // button.send-button, button[aria-label=\"Send message\"]". Broadened
      // with case-insensitive matching and more fallback patterns, same fix
      // already applied to Claude. Also see dispatchSyntheticSubmit() below
      // -- a general safety net for ALL sites so a stale selector here never
      // strands an injected message unsent again (which is what was
      // actually happening: e.preventDefault() paused the native submit,
      // injection ran, then no button matched to resume it).
      submitSelector: 'button.send-button, button[aria-label="Send message" i], button[aria-label*="send" i], button[data-test-id*="send" i], button[mattooltip*="send" i]',
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

  function notifyContextInvalidated() {
    if (extensionContextInvalidated) return;
    extensionContextInvalidated = true;
    console.info('[Mnemox] Extension was reloaded. Refresh this AI tab to reconnect capture and injection.');
    setTimeout(function() {
      if (!document.body) return;
      injectToastStyles();
      showToast('Mnemox updated', 'Refresh this tab to reconnect memory capture');
    }, 0);
  }

  // chrome.runtime.sendMessage can throw synchronously after an unpacked
  // extension is reloaded. Contain that lifecycle event so it never becomes
  // an uncaught extension error, and give the user an actionable notice.
  function safeSendMessage(message, callback) {
    if (extensionContextInvalidated) {
      if (callback) callback(null, new Error('Extension context invalidated'));
      return;
    }
    try {
      chrome.runtime.sendMessage(message, function(response) {
        var runtimeError = chrome.runtime.lastError;
        if (runtimeError) {
          if (/context invalidated/i.test(runtimeError.message || '')) {
            notifyContextInvalidated();
          }
          if (callback) callback(null, runtimeError);
          return;
        }
        if (callback) callback(response, null);
      });
    } catch (error) {
      if (/context invalidated/i.test(error.message || '')) {
        notifyContextInvalidated();
      }
      if (callback) callback(null, error);
    }
  }

  // ── Settings ────────────────────────────────────────────────────────────────
  function loadSettings() {
    return new Promise(function(resolve) {
      safeSendMessage({ type: 'MNEMOX_GET_SETTINGS' }, function(r) {
        if (r && r.success) settings = Object.assign({}, settings, r.settings);
        console.log('[Mnemox] Settings loaded on ' + CURRENT_SITE + ':', settings);
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
    var finished = false;
    function finish(memories) {
      if (finished) return;
      finished = true;
      clearTimeout(budgetTimer);
      callback(memories || []);
    }

    // A content-level watchdog protects submission even if the service
    // worker is suspended, crashes, or never invokes the response callback.
    var budgetTimer = setTimeout(function() {
      console.debug('[Mnemox] Injection budget reached; sending prompt without waiting for remote memory.');
      finish([]);
    }, INJECTION_BUDGET_MS);

    safeSendMessage({
      type: 'MNEMOX_SEARCH_MEMORIES',
      payload: { query: promptText, limit: 5, score_threshold: 0.65 },
    }, function(response, error) {
      if (error) {
        finish([]);
        return;
      }
      if (response && response.success && response.results && response.results.length > 0) {
        finish(response.results);
      } else {
        finish([]);
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
    // 2026-07-09: diagnostic logging added at every early-return point.
    // Capture kept silently failing on Claude with no visible signal why --
    // these logs turn the next test into an actual diagnosis instead of
    // another guess. Safe to remove once the real failure point is found
    // and fixed; until then this is cheap and only runs on Enter/submit.
    if (!settings.captureEnabled) {
      console.log('[Mnemox] Capture skipped: captureEnabled is false', settings);
      return;
    }
    var original = text;
    text = text.trim();
    // Strip injected context before saving — save only the user's original prompt
    var markerIdx = text.indexOf('[Mnemox Context');
    if (markerIdx === -1) markerIdx = text.indexOf('[End Mnemox Context]');
    if (markerIdx !== -1) {
      var endMarker = '[End Mnemox Context]\n\n';
      var endIdx = text.indexOf(endMarker);
      if (endIdx !== -1) text = text.slice(endIdx + endMarker.length).trim();
    }
    if (!text || text.length < 4) {
      console.log('[Mnemox] Capture skipped: text too short after trim/strip.',
        'original=' + JSON.stringify(original), 'stripped=' + JSON.stringify(text));
      return;
    }
    if (text === lastCaptured) {
      console.log('[Mnemox] Capture skipped: duplicate of last capture.', text.slice(0, 60));
      return;
    }
    lastCaptured = text;

    var stored = text.length > 1000 ? text.slice(0, 1000) + '...' : text;
    console.log('[Mnemox] Sending capture to service worker:', stored.slice(0, 60));
    safeSendMessage({
      type: 'MNEMOX_MEMORY_CAPTURED',
      payload: { content: stored, source: CURRENT_SITE },
    }, function(response, error) {
      if (error) {
        lastCaptured = '';
        return;
      }
      if (response && response.success) {
        console.log('[Mnemox] Capture confirmed saved, id=' + response.id);
        var preview = text.slice(0, 45) + (text.length > 45 ? '...' : '');
        showToast('Memory saved', '"' + preview + '"');
      } else {
        console.error('[Mnemox] Capture rejected by service worker:', response);
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
    // 2026-07-09: v0.1.13's broadened selectors did NOT fix Claude capture
    // reading empty text -- identical symptom before and after. That points
    // at a deeper problem than selector wording: possibly promptEl isn't
    // actually the element the user types into at all (our capture-phase
    // keydown listener fires for any Enter press that passes THROUGH
    // promptEl on its way down from document to the real target, which
    // includes promptEl being an ANCESTOR of the real input -- not
    // necessarily promptEl itself). Dumping the matched element's identity
    // and structure at wire-time, unconditionally, so this is visible
    // regardless of whether a later capture attempt succeeds or fails.
    try {
      console.log('[Mnemox] Prompt wired on ' + CURRENT_SITE + '. Matched element:', promptEl,
        'tag=' + promptEl.tagName, 'class=' + promptEl.className,
        'outerHTML(300)=' + promptEl.outerHTML.slice(0, 300));
    } catch (err) {
      console.log('[Mnemox] Prompt wired on ' + CURRENT_SITE + ' (element logging failed: ' + err.message + ')');
    }

    // 2026-07-09 fix -- ROOT CAUSE CONFIRMED via live console diagnostics:
    //   "promptEl===activeElement: false, activeElement tag: BODY"
    // at the exact moment our Enter keydown listener ran, with text already
    // empty. promptEl WAS the correct element (verified via the wire-time
    // dump: data-testid="chat-input", aria-label="Write your prompt to
    // Claude") -- this was never a wrong-element problem. It's a same-
    // element listener ORDERING race: Claude's own React onKeyDown handler
    // is attached to this same contenteditable div and clears/blurs it
    // synchronously before our listener runs, because same-element
    // same-phase listeners fire in attachment order and Claude's mounts
    // before our MutationObserver catches up to attach ours -- capture
    // phase doesn't help when both listeners are on the SAME element.
    //
    // Fix: stop trying to read the DOM at Enter time entirely. Track the
    // text continuously via 'input' events (which fire on every keystroke,
    // well before Enter), so by the time Enter fires we already have a
    // reliable snapshot captured independently of whatever Claude's own
    // handler does to the box afterward.
    var lastKnownText = '';
    promptEl.addEventListener('input', function() {
      lastKnownText = config.getPromptText(promptEl).trim();
    });

    // 2026-07-10 fix -- REAL DATA-LOSS BUG FOUND during live Gemini testing:
    // "[Mnemox] No submit button matched on gemini for selector: ...". That
    // warning alone looked cosmetic, but tracing the actual consequence
    // showed it wasn't: when injectEnabled is true, our Enter listener calls
    // e.preventDefault() to pause the native submit BEFORE it knows whether
    // a submit button can be found again afterward. If config.submitSelector
    // has gone stale (site markup changed, like Gemini's did), the resume
    // step below finds nothing to click and the message is silently
    // stranded in the box -- injected, but never actually sent.
    //
    // Fix: as a last resort when no selector matches, re-dispatch a REAL
    // Enter keydown/keypress/keyup sequence at the prompt element so the
    // site's OWN submit handler takes over, independent of whatever our
    // selector list guesses. This makes every site resilient to future
    // selector staleness, not just Gemini. Marked .mnemoxSynthetic so our
    // own capture-phase listener below recognizes and ignores it instead of
    // re-entering this same handler in a loop.
    function dispatchSyntheticSubmit() {
      ['keydown', 'keypress', 'keyup'].forEach(function(type) {
        var evt = new KeyboardEvent(type, {
          key: 'Enter', code: 'Enter', keyCode: 13, which: 13,
          bubbles: true, cancelable: true,
        });
        evt.mnemoxSynthetic = true;
        promptEl.dispatchEvent(evt);
      });
    }

    promptEl.addEventListener('keydown', function(e) {
      if (e.mnemoxSynthetic) return;  // our own synthetic-submit re-dispatch — don't re-enter
      if (e.key === 'Enter' && !e.shiftKey) {
        var liveText = config.getPromptText(promptEl).trim();
        // Prefer a fresh live read when it looks valid (covers ChatGPT/
        // Gemini/Copilot, where this always worked); fall back to the last
        // 'input'-tracked snapshot when the live read comes back empty/too
        // short, which is exactly what happens on Claude.
        var text = liveText.length >= 3 ? liveText : lastKnownText;
        console.log('[Mnemox] Enter pressed on ' + CURRENT_SITE + '. liveText length: ' + liveText.length +
          ', lastKnownText length: ' + lastKnownText.length + ', using: ' + (liveText.length >= 3 ? 'live' : 'lastKnown') +
          ', preview: ' + JSON.stringify(text.slice(0, 60)));
        if (!text || text.length < 3) {
          console.log('[Mnemox] Enter handler bailed: text too short (len=' + text.length + ') even after lastKnownText fallback');
          return;
        }

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
              var btnFound = false;
              for (var i = 0; i < submitSelectors.length; i++) {
                var btn = document.querySelector(submitSelectors[i].trim());
                if (btn) {
                  mnemoxOwnClick = true;
                  btn.click();
                  mnemoxOwnClick = false;
                  btnFound = true;
                  break;
                }
              }
              if (!btnFound) {
                console.debug('[Mnemox] No submit button matched on ' + CURRENT_SITE +
                  ' after injection -- falling back to a synthetic Enter so the message isn\'t stranded unsent.');
                dispatchSyntheticSubmit();
              }
            }, POST_INJECTION_SETTLE_MS);
          });
        } else {
          // Injection disabled — just capture
          setTimeout(function() { capturePrompt(text); }, 50);
        }
      }
    }, true);  // capture phase — runs before AI tool's own listeners

  }

  // One capture-phase delegated listener handles Send buttons that appear,
  // disappear, or are replaced as the AI site's SPA state changes. This
  // avoids treating the normal "button not rendered yet" state as an error.
  function handleSubmitClick(e) {
    if (mnemoxOwnClick) return;
    var target = e.target;
    if (!target || typeof target.closest !== 'function') return;
    var btn = target.closest(config.submitSelector);
    if (!btn) return;
    var promptEl = findPromptEl();
    if (!promptEl) return;
    var text = config.getPromptText(promptEl).trim();
    console.log('[Mnemox] Submit button clicked on ' + CURRENT_SITE + '.');
    setTimeout(function() { capturePrompt(text); }, 80);
  }

  // ── MutationObserver: handles SPA re-renders ─────────────────────────────
  function startObserver() {
    if (observer) return;
    var el = findPromptEl();
    if (el) attachPromptListeners(el);

    observer = new MutationObserver(function(mutations) {
      // AI chat pages stream many DOM mutations per second. Coalesce bursts
      // and only rescan when nodes were actually added.
      var hasAddedNodes = mutations.some(function(m) { return m.addedNodes.length > 0; });
      if (!hasAddedNodes || observerTimer) return;
      observerTimer = setTimeout(function() {
        observerTimer = null;
        var found = findPromptEl();
        if (found) attachPromptListeners(found);
      }, 50);
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
      document.addEventListener('click', handleSubmitClick, true);
      startObserver();
      safeSendMessage({ type: 'MNEMOX_PING' }, function(r) {
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
