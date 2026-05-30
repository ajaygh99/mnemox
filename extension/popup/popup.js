// popup.js — Mnemox Extension Popup Logic
// Step 7: + Auth state check, plan badge, sign out

const AI_SITES = {
  'chat.openai.com':       { name: 'ChatGPT', icon: '🤖' },
  'chatgpt.com':           { name: 'ChatGPT', icon: '🤖' },
  'claude.ai':             { name: 'Claude',  icon: '🧠' },
  'gemini.google.com':     { name: 'Gemini',  icon: '✨' },
  'copilot.microsoft.com': { name: 'Copilot', icon: '🔷' },
};

const PLAN_LABELS = { free: 'Free', pro: 'Pro ✦', team: 'Team ✦✦' };

// ── Auth gate ─────────────────────────────────────────────────────────────────
async function checkAuth() {
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type: 'MNEMOX_AUTH_GET_STATE' }, resolve);
  });
}

// ── Load settings ─────────────────────────────────────────────────────────────
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

// ── Detect active AI site ─────────────────────────────────────────────────────
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

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  // Step 7: check auth first
  const authState = await checkAuth();

  if (!authState || !authState.isLoggedIn) {
    // Redirect to login page
    window.location.href = 'login.html';
    return;
  }

  const settings = await loadSettings();
  const site = await detectActiveSite();

  // Plan badge
  const plan = authState.plan || 'free';
  const planEl = document.getElementById('plan-badge');
  if (planEl) {
    planEl.textContent = PLAN_LABELS[plan] || plan;
    planEl.className = 'plan-badge plan-' + plan;
  }

  // User email
  const userEl = document.getElementById('user-email');
  if (userEl && authState.user) {
    userEl.textContent = authState.user.email;
  }

  // Memory count
  const countEl = document.getElementById('memory-count');
  if (countEl) countEl.textContent = settings.memoryCount || 0;

  // Free plan limit warning
  if (plan === 'free') {
    const limitEl = document.getElementById('limit-notice');
    if (limitEl) {
      const count = settings.memoryCount || 0;
      const pct = Math.min(100, Math.round((count / 50) * 100));
      limitEl.textContent = `${count}/50 memories (${pct}%)`;
      limitEl.style.display = 'block';
      if (count >= 40) limitEl.style.color = '#f87171';
    }
  }

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

  // Sign out
  document.getElementById('signout-btn')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'MNEMOX_AUTH_SIGNOUT' }, () => {
      window.location.href = 'login.html';
    });
  });
}

document.addEventListener('DOMContentLoaded', init);
