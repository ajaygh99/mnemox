// dashboard.js — Mnemox Memory Dashboard logic
// Moved out of an inline <script> block in index.html because Manifest V3's
// default extension-page CSP (script-src 'self') blocks ALL inline script
// execution -- including inline <script> tags and onclick="..." attributes.
// That CSP violation is why the dashboard has always shown "0 memories": the
// entire script (loadData, the live-refresh listener, everything) silently
// never ran. Chrome's error console confirms this:
//   "Executing inline script violates the following Content Security Policy
//    directive: 'script-src 'self''... The action has been blocked."
//   at dashboard/index.html:263
// Fix: external script file (loads fine under 'self'), and every onclick=/
// onchange=/oninput= attribute converted to addEventListener wiring below.

// State
var allMemories = [];
var activeSource = ''; // '' = All. One of chatgpt/claude/gemini/copilot/perplexity/grok.
var settings = { captureEnabled: true, injectEnabled: true, backendUrl: '', apiKey: '' };
var filterTimer = null;

// Every source the dashboard knows how to count/filter/badge. Keep in sync
// with the chip buttons in index.html (#source-chips) and the source-*
// badge classes in the stylesheet.
var KNOWN_SOURCES = ['chatgpt', 'claude', 'gemini', 'copilot', 'perplexity', 'grok'];

function scheduleFilterMemories() {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(filterMemories, 100);
}

// Navigation
function showPage(name, btn) {
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById('page-' + name).classList.add('active');
  if (btn) btn.classList.add('active');
}

// Load data from chrome.storage.local
function loadData() {
  if (typeof chrome === 'undefined' || !chrome.storage) {
    // Dev mode outside extension -- use mock data
    allMemories = [
      { id: '1', content: 'Explain vector databases in simple terms', source: 'chatgpt', capturedAt: Date.now() - 86400000 },
      { id: '2', content: 'Write a Python FastAPI endpoint for user auth', source: 'claude', capturedAt: Date.now() - 3600000 },
      { id: '3', content: 'How do I reduce AI API costs for my startup', source: 'gemini', capturedAt: Date.now() - 1800000 },
    ];
    settings = { captureEnabled: true, injectEnabled: true, backendUrl: 'https://mnemox-production.up.railway.app', apiKey: '' };
    renderAll();
    return;
  }

  chrome.storage.local.get(
    ['memories', 'captureEnabled', 'injectEnabled', 'backendUrl', 'apiKey'],
    function(data) {
      allMemories = (data.memories || []).slice().reverse(); // newest first
      settings.captureEnabled = data.captureEnabled !== false;
      settings.injectEnabled  = data.injectEnabled  !== false;
      settings.backendUrl = data.backendUrl || '';
      settings.apiKey     = data.apiKey     || '';
      renderAll();
    }
  );
}

function renderAll() {
  renderStats();
  renderMemories(allMemories);
  renderSettings();
}

// Stats -- also drives the counts shown inside each filter chip.
function renderStats() {
  var counts = {};
  KNOWN_SOURCES.forEach(function(s) { counts[s] = 0; });
  allMemories.forEach(function(m) { if (counts[m.source] !== undefined) counts[m.source]++; });

  var totalEl = document.getElementById('chip-count-all');
  if (totalEl) totalEl.textContent = allMemories.length;

  KNOWN_SOURCES.forEach(function(s) {
    var el = document.getElementById('chip-count-' + s);
    if (el) el.textContent = counts[s];
  });
}

// Memory list -- filters by the active chip (activeSource) AND the search box.
function filterMemories() {
  var query = document.getElementById('mem-search').value.toLowerCase();
  var filtered = allMemories.filter(function(m) {
    var matchSource = !activeSource || m.source === activeSource;
    var matchText   = !query || m.content.toLowerCase().includes(query);
    return matchSource && matchText;
  });
  renderMemories(filtered);
}

// Chip click -- exactly one chip is active at a time (event delegation, same
// pattern as handleListClick below, since chips aren't static onclick attrs).
function handleChipClick(e) {
  var chip = e.target.closest('.chip');
  if (!chip) return;
  activeSource = chip.getAttribute('data-source') || '';
  document.querySelectorAll('#source-chips .chip').forEach(function(c) { c.classList.remove('active'); });
  chip.classList.add('active');
  filterMemories();
}

function renderMemories(list) {
  var el = document.getElementById('memory-list');
  if (!list.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">\u{1F9E0}</div><div class="empty-text">No memories match your filter</div></div>';
    return;
  }
  el.innerHTML = list.map(function(m) { return memoryCard(m); }).join('');
}

function memoryCard(m) {
  var date = new Date(m.capturedAt || m.created_at).toLocaleString();
  return '<div class="memory-card" id="card-' + m.id + '">' +
    '<div class="memory-source"><span class="source-badge source-' + m.source + '">' + m.source + '</span></div>' +
    '<div class="memory-body">' +
      '<div class="memory-text" id="text-' + m.id + '">' + escHtml(m.content) + '</div>' +
      '<div class="memory-meta">' + date + '</div>' +
    '</div>' +
    '<div class="memory-actions">' +
      '<button class="btn-icon" data-action="expand" data-id="' + m.id + '" title="Expand">⤢</button>' +
      '<button class="btn-icon btn-delete" data-action="delete" data-id="' + m.id + '" title="Delete">\u{1F5D1}</button>' +
    '</div>' +
  '</div>';
}

// Event delegation for dynamically-inserted card buttons (expand/delete) --
// these used to be onclick="..." attributes baked into the innerHTML string,
// which is just as much an inline-script CSP violation as a <script> tag.
function handleListClick(e) {
  var btn = e.target.closest('[data-action]');
  if (!btn) return;
  var id = btn.getAttribute('data-id');
  if (btn.getAttribute('data-action') === 'expand') expandMemory(id);
  if (btn.getAttribute('data-action') === 'delete') deleteMemory(id);
}

function expandMemory(id) {
  var el = document.getElementById('text-' + id);
  if (el) el.classList.toggle('expanded');
}

function deleteMemory(id) {
  allMemories = allMemories.filter(function(m) { return m.id !== id; });
  if (typeof chrome !== 'undefined' && chrome.storage) {
    chrome.storage.local.set({ memories: allMemories.slice().reverse(), memoryCount: allMemories.length });
  }
  var card = document.getElementById('card-' + id);
  if (card) { card.style.opacity = '0'; card.style.transition = 'opacity 0.2s'; setTimeout(function() { filterMemories(); renderStats(); }, 200); }
}

// Semantic Search
function semanticSearch() {
  var query = document.getElementById('sem-query').value.trim();
  var el = document.getElementById('search-results');
  if (!query) return;

  el.innerHTML = '<div class="empty-state"><div class="empty-icon">⏳</div><div class="empty-text">Searching...</div></div>';

  if (typeof chrome !== 'undefined' && chrome.runtime) {
    chrome.runtime.sendMessage({
      type: 'MNEMOX_SEARCH_MEMORIES',
      payload: { query: query, limit: 10, score_threshold: 0.5 },
    }, function(response) {
      if (response && response.success && response.results.length) {
        var matched = response.results.map(function(r) {
          return allMemories.find(function(m) { return m.id === r.memory_id; }) ||
            { id: r.memory_id, content: r.content_preview, source: r.source, capturedAt: r.created_at };
        });
        el.innerHTML = matched.map(function(m) { return memoryCard(m); }).join('');
      } else {
        el.innerHTML = '<div class="empty-state"><div class="empty-icon">\u{1F50D}</div><div class="empty-text">No similar memories found</div></div>';
      }
    });
  } else {
    // Dev fallback: keyword search
    var results = allMemories.filter(function(m) { return m.content.toLowerCase().includes(query.toLowerCase()); });
    el.innerHTML = results.length ? results.map(memoryCard).join('') :
      '<div class="empty-state"><div class="empty-icon">\u{1F50D}</div><div class="empty-text">No results</div></div>';
  }
}

// Settings
function renderSettings() {
  document.getElementById('s-backend-url').value = settings.backendUrl || '';
  document.getElementById('s-api-key').value     = settings.apiKey     || '';
  document.getElementById('t-capture').className = 'toggle' + (settings.captureEnabled ? ' on' : '');
  document.getElementById('t-inject').className  = 'toggle' + (settings.injectEnabled  ? ' on' : '');
}

function toggleSetting(key, toggleId) {
  settings[key] = !settings[key];
  document.getElementById(toggleId).classList.toggle('on', settings[key]);
  if (typeof chrome !== 'undefined' && chrome.storage) {
    var patch = {}; patch[key] = settings[key];
    chrome.storage.local.set(patch);
  }
}

function saveBackendSettings() {
  var url = document.getElementById('s-backend-url').value.trim();
  var key = document.getElementById('s-api-key').value.trim();
  var statusEl = document.getElementById('conn-status');

  if (typeof chrome !== 'undefined' && chrome.storage) {
    chrome.storage.local.set({ backendUrl: url, apiKey: key });
  }

  statusEl.style.display = 'block';
  statusEl.textContent = 'Saving...';

  // Test connection
  if (url && key) {
    fetch(url + '/health', { headers: { 'X-API-Key': key } })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        statusEl.textContent = data.status === 'ok'
          ? 'Connected! Supabase: ' + (data.supabase_connected ? 'OK' : 'Error') + ' | Qdrant: ' + (data.qdrant_connected ? 'OK' : 'Error')
          : 'Backend reachable but degraded';
        statusEl.style.color = data.status === 'ok' ? '#22c55e' : '#f59e0b';
      })
      .catch(function() {
        statusEl.textContent = 'Saved locally (backend unreachable -- is it running?)';
        statusEl.style.color = '#f59e0b';
      });
  } else {
    statusEl.textContent = 'Settings saved (no backend URL provided -- using local mode)';
    statusEl.style.color = '#9ca3af';
  }
}

function clearAllMemories() {
  if (!confirm('Delete ALL memories permanently? This cannot be undone.')) return;
  allMemories = [];
  if (typeof chrome !== 'undefined' && chrome.storage) {
    chrome.storage.local.set({ memories: [], memoryCount: 0 });
  }
  renderAll();
  var el = document.getElementById('clear-status');
  el.style.display = 'block';
  el.textContent = 'All memories cleared.';
  el.style.color = '#f87171';
}

// Utility
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Version / build identity
function showVersion() {
  var el = document.getElementById('sidebar-version');
  if (!el) return;
  if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getManifest) {
    var v = chrome.runtime.getManifest().version;
    var id = chrome.runtime.id || '';
    el.textContent = 'v' + v + ' · Mnemox';
    el.title = 'Extension ID: ' + id;
  } else {
    el.textContent = 'Mnemox (dev)';
  }
}

// Wire up all controls (replaces the removed onclick/onchange/oninput attrs)
function wireUpEvents() {
  document.getElementById('nav-memories')?.addEventListener('click', function(e) { showPage('memories', e.currentTarget); });
  document.getElementById('nav-search')?.addEventListener('click', function(e) { showPage('search', e.currentTarget); });
  document.getElementById('nav-settings')?.addEventListener('click', function(e) { showPage('settings', e.currentTarget); });

  document.getElementById('mem-search')?.addEventListener('input', scheduleFilterMemories);
  document.getElementById('source-chips')?.addEventListener('click', handleChipClick);

  document.getElementById('sem-search-btn')?.addEventListener('click', semanticSearch);
  document.getElementById('save-backend-btn')?.addEventListener('click', saveBackendSettings);
  document.getElementById('clear-all-btn')?.addEventListener('click', clearAllMemories);

  document.getElementById('t-capture')?.addEventListener('click', function() { toggleSetting('captureEnabled', 't-capture'); });
  document.getElementById('t-inject')?.addEventListener('click', function() { toggleSetting('injectEnabled', 't-inject'); });

  document.getElementById('memory-list')?.addEventListener('click', handleListClick);
  document.getElementById('search-results')?.addEventListener('click', handleListClick);

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && document.getElementById('sem-query') === document.activeElement) {
      semanticSearch();
    }
  });
}

// Init
wireUpEvents();
showVersion();
loadData();

// Live-refresh: the dashboard is often left open in a tab while memories get
// captured elsewhere (popup, content script on an AI site). Re-run loadData()
// whenever the relevant keys change, from any part of the extension.
if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.onChanged) {
  chrome.storage.onChanged.addListener(function(changes, area) {
    if (area !== 'local') return;
    if (changes.memories || changes.captureEnabled || changes.injectEnabled ||
        changes.backendUrl || changes.apiKey) {
      loadData();
    }
  });
}
