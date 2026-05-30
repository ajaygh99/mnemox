// popup.js — Mnemox Extension Popup Logic
// Step 1: UI wiring, settings persistence, site detection

const AI_SITES = {
  'chat.openai.com': { name: 'ChatGPT', icon: '🤖' },
  'chatgpt.com':     { name: 'ChatGPT', icon: '🤖' },
  'claude.ai':       { name: 'Claude',  icon: '🧠' },
  'gemini.google.com': { name: 'Gemini', icon: '✨' },
  'copilot.microsoft.com': { name: 'Copilot', icon: '🔷' },
};

// ── Load settings from chrome.storage ──────────────────────────────────────
async function loadSettings() {
  return new Promise(resolve => {
    chrome.storage.local.get(
      { captureEnabled: true, injectEnabled: true, memoryCount: 0 },
      resolve
    );
  });
}

async function saveSettings(patch) {
  return new Promise(resolve => {
    chrome.storage.local.set(patch, resolve);
  });
}

// ── Detect which AI site is active ─────────────────────────────────────────
async function detectActiveSite() {
  return new Promise(resolve => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (!tabs[0]?.url) return resolve(null);
      try {
        const hostname = new URL(tabs[0].url).hostname;
        resolve(AI_SITES[hostname] || null);
      } catch {
        resolve(null);
      }
    });
  });
}

// ── Render UI ───────────────────────────────────────────────────────────────
function renderSiteBadge(site) {
  const icon = document.getElementById('siteIcon');
  const name = document.getElementById('siteName');
  const status = document.getElementById('siteStatus');

  if (site) {
    icon.textContent = site.icon;
    name.textContent = site.name;
    status.textContent = 'Memory injection active ✓';
    status.style.color = '#22c55e';
  } else {
    icon.textContent = '🌐';
    name.textContent = 'No AI tool detected';
    status.textContent = 'Open ChatGPT, Claude, Gemini or Copilot';
    status.style.color = '#6b7280';
  }
}

function renderToggles(settings) {
  const captureToggle = document.getElementById('captureToggle');
  const injectToggle  = document.getElementById('injectToggle');
  captureToggle.classList.toggle('on', settings.captureEnabled);
  injectToggle.classList.toggle('on',  settings.injectEnabled);
}

function renderMemoryCount(count) {
  document.getElementById('memoryCount').textContent = count;
}

// ── Toggle handlers ─────────────────────────────────────────────────────────
window.toggleCapture = async function () {
  const settings = await loadSettings();
  const next = !settings.captureEnabled;
  await saveSettings({ captureEnabled: next });
  document.getElementById('captureToggle').classList.toggle('on', next);
  notifyContentScript({ type: 'MNEMOX_SETTINGS_CHANGED', captureEnabled: next });
};

window.toggleInject = async function () {
  const settings = await loadSettings();
  const next = !settings.injectEnabled;
  await saveSettings({ injectEnabled: next });
  document.getElementById('injectToggle').classList.toggle('on', next);
  notifyContentScript({ type: 'MNEMOX_SETTINGS_CHANGED', injectEnabled: next });
};

// ── Button handlers ─────────────────────────────────────────────────────────
document.getElementById('viewMemoriesBtn').addEventListener('click', () => {
  chrome.tabs.create({ url: chrome.runtime.getURL('dashboard/index.html') });
});

document.getElementById('saveNowBtn').addEventListener('click', async () => {
  const btn = document.getElementById('saveNowBtn');
  btn.textContent = '✅ Saved!';
  btn.disabled = true;
  notifyContentScript({ type: 'MNEMOX_SAVE_NOW' });
  setTimeout(() => {
    btn.textContent = '💾 Save Current Context';
    btn.disabled = false;
  }, 2000);
});

// ── Send message to active tab's content script ─────────────────────────────
function notifyContentScript(message) {
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (tabs[0]?.id) {
      chrome.tabs.sendMessage(tabs[0].id, message).catch(() => {
        // Tab may not have content script — safe to ignore
      });
    }
  });
}

// ── Init ────────────────────────────────────────────────────────────────────
(async () => {
  const [settings, site] = await Promise.all([loadSettings(), detectActiveSite()]);
  renderSiteBadge(site);
  renderToggles(settings);
  renderMemoryCount(settings.memoryCount);
})();
