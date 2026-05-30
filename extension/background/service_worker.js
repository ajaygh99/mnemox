// service_worker.js — Mnemox Background Service Worker
// Step 5: + Memory search via backend API, API config storage

const MNEMOX_VERSION = '0.5.0';

const AI_HOSTS = [
  'chat.openai.com', 'chatgpt.com',
  'claude.ai', 'gemini.google.com', 'copilot.microsoft.com',
];

// ── Install / Startup ────────────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === 'install') {
    chrome.storage.local.set({
      captureEnabled: true,
      injectEnabled: true,
      memoryCount: 0,
      memories: [],
      installedAt: Date.now(),
      // Backend config — user sets these in popup settings (Step 6)
      backendUrl: 'http://localhost:8000',
      apiKey: '',
    });
    console.log(`[Mnemox v${MNEMOX_VERSION}] Installed`);
  }
});

chrome.runtime.onStartup.addListener(() => {
  console.log(`[Mnemox v${MNEMOX_VERSION}] Service worker started`);
});

// ── Message Router ───────────────────────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {

    case 'MNEMOX_MEMORY_CAPTURED':
      handleMemoryCaptured(message.payload, sender, sendResponse);
      return true;

    case 'MNEMOX_SEARCH_MEMORIES':
      handleSearchMemories(message.payload, sendResponse);
      return true;

    case 'MNEMOX_GET_MEMORIES':
      handleGetMemories(message.payload, sendResponse);
      return true;

    case 'MNEMOX_GET_SETTINGS':
      handleGetSettings(sendResponse);
      return true;

    case 'MNEMOX_UPDATE_SETTINGS':
      handleUpdateSettings(message.payload, sendResponse);
      return true;

    case 'MNEMOX_PING':
      sendResponse({ status: 'ok', version: MNEMOX_VERSION });
      break;

    default:
      console.warn('[Mnemox SW] Unknown message:', message.type);
  }
});

// ── Handlers ─────────────────────────────────────────────────────────────────

async function handleMemoryCaptured(payload, sender, sendResponse) {
  try {
    const result = await chrome.storage.local.get(['memories', 'memoryCount', 'backendUrl', 'apiKey']);
    const memories = result.memories || [];
    const count = result.memoryCount || 0;

    const newMemory = {
      id: `mem_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      content: payload.content,
      source: payload.source,
      url: sender.url || '',
      capturedAt: Date.now(),
    };

    memories.push(newMemory);
    if (memories.length > 500) memories.shift();

    await chrome.storage.local.set({ memories, memoryCount: count + 1 });
    updateBadge(memories.length);

    // Also send to backend API (non-blocking — don't fail if backend is down)
    if (result.backendUrl && result.apiKey) {
      saveToBackend(newMemory, result.backendUrl, result.apiKey).catch(e =>
        console.warn('[Mnemox SW] Backend save failed (offline?):', e.message)
      );
    }

    sendResponse({ success: true, id: newMemory.id });
  } catch (err) {
    console.error('[Mnemox SW] Save error:', err);
    sendResponse({ success: false, error: err.message });
  }
}

async function handleSearchMemories(payload, sendResponse) {
  try {
    const { backendUrl, apiKey } = await chrome.storage.local.get(['backendUrl', 'apiKey']);

    if (!backendUrl || !apiKey) {
      // Backend not configured — fall back to local keyword search
      const { memories = [] } = await chrome.storage.local.get('memories');
      const results = localKeywordSearch(memories, payload.query, payload.limit || 5);
      return sendResponse({ success: true, results, source: 'local' });
    }

    // Call backend semantic search
    const response = await fetch(`${backendUrl}/memories/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({
        query: payload.query,
        limit: payload.limit || 5,
        score_threshold: payload.score_threshold || 0.65,
      }),
    });

    if (!response.ok) throw new Error(`Backend error: ${response.status}`);
    const data = await response.json();
    sendResponse({ success: true, results: data.results || [], source: 'backend' });

  } catch (err) {
    console.warn('[Mnemox SW] Search error:', err.message);
    // Graceful fallback to local search
    try {
      const { memories = [] } = await chrome.storage.local.get('memories');
      const results = localKeywordSearch(memories, payload.query, payload.limit || 5);
      sendResponse({ success: true, results, source: 'local_fallback' });
    } catch (e) {
      sendResponse({ success: false, error: err.message, results: [] });
    }
  }
}

async function handleGetMemories(payload, sendResponse) {
  const { memories = [] } = await chrome.storage.local.get('memories');
  const limit = payload?.limit || 20;
  sendResponse({ success: true, memories: memories.slice(-limit) });
}

async function handleGetSettings(sendResponse) {
  const settings = await chrome.storage.local.get([
    'captureEnabled', 'injectEnabled', 'memoryCount', 'backendUrl', 'apiKey'
  ]);
  sendResponse({ success: true, settings });
}

async function handleUpdateSettings(patch, sendResponse) {
  await chrome.storage.local.set(patch);
  sendResponse({ success: true });
}

// ── Backend API call ─────────────────────────────────────────────────────────
async function saveToBackend(memory, backendUrl, apiKey) {
  const response = await fetch(`${backendUrl}/memories`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify({
      content: memory.content,
      source: memory.source,
    }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// ── Local keyword fallback search (when backend not configured) ──────────────
function localKeywordSearch(memories, query, limit) {
  if (!query || !memories.length) return [];

  const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);

  return memories
    .map(function(m) {
      const text = m.content.toLowerCase();
      const score = queryWords.reduce(function(acc, word) {
        return acc + (text.includes(word) ? 1 : 0);
      }, 0) / queryWords.length;
      return { memory_id: m.id, score: score, source: m.source,
               content_preview: m.content.slice(0, 200), created_at: m.capturedAt };
    })
    .filter(function(r) { return r.score > 0; })
    .sort(function(a, b) { return b.score - a.score; })
    .slice(0, limit);
}

// ── Badge ─────────────────────────────────────────────────────────────────────
function updateBadge(count) {
  const text = count > 99 ? '99+' : String(count);
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color: '#7c3aed' });
}

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  try {
    const tab = await chrome.tabs.get(tabId);
    const isAI = tab.url && AI_HOSTS.some(h => tab.url.includes(h));
    if (!isAI) {
      chrome.action.setBadgeText({ text: '' });
    } else {
      const { memoryCount = 0 } = await chrome.storage.local.get('memoryCount');
      updateBadge(memoryCount);
    }
  } catch { /* tab closed */ }
});
