// popup.js — Mnemox Extension Popup Logic
// Step 7: + Auth state check, plan badge, sign out

const AI_SITES = {
  'chat.openai.com':       { name: 'ChatGPT', icon: '\u{1F916}' },
  'chatgpt.com':           { name: 'ChatGPT', icon: '\u{1F916}' },
  'claude.ai':             { name: 'Claude',  icon: '\u{1F9E0}' },
  'gemini.google.com':     { name: 'Gemini',  icon: '✨' },
  'copilot.microsoft.com': { name: 'Copilot', icon: '\u{1F537}' },
};

const PLAN_LABELS = { free: 'Free', pro: 'Pro ✦', team: 'Team ✦✦' };

// -- Auth gate --------------------------------------------------------------
async function checkAuth() {
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type: 'MNEMOX_AUTH_GET_STATE' }, resolve);
  });
}

// -- Load settings ------------------------------------------------------------
async function loadSettings() {
  return new Promise(resolve => {
    chrome.storage.local.get(
      { captureEnabled: true, injectEnabled: true, memoryCount: 0, authPlan: 'free' },
      resolve
    );
  });
}

async function saveSettings(patch) {
  return new Promise(resolve => chrome.storage.local.set(patch, resolve));
}

// -- Detect active AI site -----------------------------------------------------
async function detectActiveSite() {
  return new Promise(resolve => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (!tabs[0]?.url) return resolve(null);
      try {
        const host = new URL(tabs[0].url).hostname;
        resolve(AI_SITES[host] || null);
      } catch { resolve(null); }
    });
  });
}

// -- Memory stats (kept live) --------------------------------------------------
// 2026-07-09: this popup has no auto-refresh, and Chrome popups normally
// close on blur -- but right-click -> Inspect pins a popup open for
// debugging, decoupled from that auto-close behavior. A pinned-open popup's
// memory count used to go stale the instant a new memory was captured while
// it sat open, which looked exactly like a capture failure even when
// capture actually succeeded (this is what made the Claude capture bug
// look worse than it was during manual testing). Re-render whenever
// memoryCount changes in storage, same pattern as the dashboard's live
// refresh fix.
function renderMemoryStats(count, plan) {
  const countEl = document.getElementById('memory-count');
  if (countEl) countEl.textContent = count;

  if (plan === 'free') {
    const limitEl = document.getElementById('limit-notice');
    if (limitEl) {
      const pct = Math.min(100, Math.round((count / 50) * 100));
      limitEl.textContent = `${count}/50 memories (${pct}%)`;
      limitEl.style.display = 'block';
      limitEl.style.color = count >= 40 ? '#f87171' : '';
    }
  }
}

let mnemoxCurrentPlan = 'free';

if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.onChanged) {
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== 'local') return;
    if (changes.memoryCount) {
      renderMemoryStats(changes.memoryCount.newValue || 0, mnemoxCurrentPlan);
    }
  });
}

// -- Init ----------------------------------------------------------------------
// 2026-07-12 fix: this used to hard-redirect to login.html on every popup
// open whenever authState.isLoggedIn was false. Chrome Web Store rejected
// the build built on that flow -- not for the reason we expected (sign-up
// itself; see tests/step9's regression story) but for "Dashboard" being
// "not working or not reproducible" during review. Root cause: sign-up
// requires email confirmation, which a reviewer can't complete, so they got
// stuck on login.html and never reached the popup's "View Memories" button,
// let alone the dashboard page it opens -- even though the dashboard itself
// never touches the backend (it reads/writes chrome.storage.local
// directly, same as capture/inject/search's local fallback in
// service_worker.js). Only cloud sync, backend semantic search, and paid
// plans actually need a session. So the popup now always renders in a
// "local mode" when signed out; an account is offered via an explicit
// Sign in link, never forced.
async function init() {
  const authState = await checkAuth();
  const isLoggedIn = !!(authState && authState.isLoggedIn);

  const settings = await loadSettings();
  const site = await detectActiveSite();

  // Plan badge -- 'free' (local) when signed out, same tier as a free account.
  const plan = isLoggedIn ? (authState.plan || 'free') : 'free';
  mnemoxCurrentPlan = plan;
  const planEl = document.getElementById('plan-badge');
  if (planEl) {
    planEl.textContent = PLAN_LABELS[plan] || plan;
    planEl.className = 'plan-badge plan-' + plan;
  }

  // User row: signed-in email + Sign out, or a Sign in link in local mode.
  const userEl = document.getElementById('user-email');
  const signoutBtn = document.getElementById('signout-btn');
  const signinLink = document.getElementById('signin-link');
  if (isLoggedIn) {
    if (userEl && authState.user) userEl.textContent = authState.user.email;
    if (signoutBtn) signoutBtn.style.display = '';
    if (signinLink) signinLink.style.display = 'none';
  } else {
    if (userEl) userEl.textContent = 'Local mode (not signed in)';
    if (signoutBtn) signoutBtn.style.display = 'none';
    if (signinLink) signinLink.style.display = '';
  }

  // Memory count (kept live below via chrome.storage.onChanged, since a
  // popup can be pinned open for a while -- e.g. via right-click Inspect --
  // and its count would otherwise go stale the moment a new memory is
  // captured while it's sitting open).
  renderMemoryStats(settings.memoryCount || 0, plan);

  // Site badge
  const siteEl = document.getElementById('site-badge');
  if (siteEl) {
    if (site) {
      siteEl.textContent = `${site.icon} ${site.name}`;
      siteEl.style.display = 'inline-block';
    } else {
      siteEl.textContent = 'Not on an AI site';
      siteEl.style.color = '#6b7280';
    }
  }

  // Toggles
  const captureToggle = document.getElementById('capture-toggle');
  const injectToggle  = document.getElementById('inject-toggle');
  if (captureToggle) captureToggle.checked = settings.captureEnabled;
  if (injectToggle)  injectToggle.checked  = settings.injectEnabled;

  captureToggle?.addEventListener('change', () => {
    saveSettings({ captureEnabled: captureToggle.checked });
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, {
        type: 'MNEMOX_SETTINGS_CHANGED', captureEnabled: captureToggle.checked
      });
    });
  });

  injectToggle?.addEventListener('change', () => {
    saveSettings({ injectEnabled: injectToggle.checked });
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, {
        type: 'MNEMOX_SETTINGS_CHANGED', injectEnabled: injectToggle.checked
      });
    });
  });

  // Dashboard button
  document.getElementById('view-memories-btn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: chrome.runtime.getURL('dashboard/index.html') });
  });

  // Upgrade button (free plan)
  document.getElementById('upgrade-btn')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://mnemox.app/pricing' });
  });

  // Sign in (optional -- only navigates to login.html on explicit request,
  // never automatically; see the note above init()).
  document.getElementById('signin-link')?.addEventListener('click', () => {
    window.location.href = 'login.html';
  });

  // Sign out -- re-render this same popup in local mode instead of bouncing
  // to login.html, since an account was never required to use it.
  document.getElementById('signout-btn')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'MNEMOX_AUTH_SIGNOUT' }, () => {
      init();
    });
  });
}

document.addEventListener('DOMContentLoaded', init);

// Shows manifest version + this extension instance's runtime ID, so it's
// obvious which build is loaded and (more importantly) whether the popup and
// the dashboard tab are actually the same loaded extension. If two unpacked
// copies of Mnemox are ever loaded at once, they get different IDs and
// completely separate chrome.storage.local -- that shows up as the popup's
// memory count disagreeing with the dashboard's.
function showVersion() {
  var el = document.getElementById('popup-version');
  if (!el) return;
  if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getManifest) {
    var v = chrome.runtime.getManifest().version;
    var id = chrome.runtime.id || '';
    el.textContent = 'v' + v + ' · ' + id.slice(0, 8);
    el.title = 'Extension ID: ' + id;
  }
}

document.addEventListener('DOMContentLoaded', showVersion);
