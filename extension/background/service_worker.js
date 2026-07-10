// service_worker.js — Mnemox Background Service Worker
// Step 7: + Supabase Auth (JWT), Bearer token support, auth state management

const MNEMOX_VERSION = '0.7.0';

// Supabase project config — the anon/publishable key is safe to ship in
// client code (it's rate-limited and access is enforced by RLS policies).
// Previously this had no default and fell back to a placeholder domain,
// which meant sign up/sign in could never succeed in the shipped build.
const SUPABASE_URL = 'https://srkxoqqnrvwdwdeunomw.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_yXbccj_6BjAGisLfOwv1-w_ScPTqEPk';

// Where Supabase sends the browser after a confirmation-link click. This
// extension has no hosted app to land the token on, so we point it at the
// marketing site instead of leaving Supabase's project default in place
// (which is the Supabase-generated 'http://localhost:3000' -- that only
// exists on a developer's own machine, so every real user's confirmation
// link would land on a dead page). This URL must also be added to
// Authentication -> URL Configuration -> Redirect URLs in the Supabase
// dashboard, or Supabase silently ignores it and falls back to Site URL.
const EMAIL_REDIRECT_URL = 'https://mnemoxpro.com/';

const AI_HOSTS = [
  'chat.openai.com', 'chatgpt.com',
  'claude.ai', 'gemini.google.com', 'copilot.microsoft.com',
];

// ── Install / Startup ────────────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener(async ({ reason }) => {
  // 2026-07-09 fix: this used to unconditionally OVERWRITE chrome.storage.local
  // with empty defaults (memories: [], memoryCount: 0, auth cleared) whenever
  // reason === 'install'. That destroyed every captured memory -- this is
  // the actual root cause behind every "0 memories" reset seen throughout
  // testing, on every AI site, not a per-site capture bug. Manually removing
  // + re-loading an unpacked extension in chrome://extensions triggers a
  // genuine 'install' event even though it's "the same" extension to a
  // developer -- and even a plain reload can sometimes fire 'install'
  // rather than 'update' for unpacked extensions. Either way, storage must
  // never be blindly reset. Now only fills in keys that don't already
  // exist, so any real data already in storage survives.
  if (reason === 'install' || reason === 'update') {
    const existing = await chrome.storage.local.get(null);
    const defaults = {
      captureEnabled: true,
      injectEnabled: true,
      memoryCount: 0,
      memories: [],
      installedAt: Date.now(),
      backendUrl: 'https://mnemox-production.up.railway.app',
      apiKey: '',
      // Step 7: auth state
      authToken: null,
      authUser: null,
      authPlan: 'free',
    };
    const patch = {};
    for (const key in defaults) {
      if (!(key in existing)) patch[key] = defaults[key];
    }
    if (Object.keys(patch).length) {
      await chrome.storage.local.set(patch);
    }
    console.log(`[Mnemox v${MNEMOX_VERSION}] ${reason}. Preserved ${Object.keys(existing).length} existing keys, filled in ${Object.keys(patch).length} missing defaults. Memories on disk: ${(existing.memories || patch.memories || []).length}`);
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

    // ── Step 7: Auth messages ──────────────────────────────────────────────

    case 'MNEMOX_AUTH_SIGNIN':
      handleSignIn(message.payload, sendResponse);
      return true;

    case 'MNEMOX_AUTH_SIGNUP':
      handleSignUp(message.payload, sendResponse);
      return true;

    case 'MNEMOX_AUTH_SIGNOUT':
      handleSignOut(sendResponse);
      return true;

    case 'MNEMOX_AUTH_GET_STATE':
      handleGetAuthState(sendResponse);
      return true;

    case 'MNEMOX_PING':
      sendResponse({ status: 'ok', version: MNEMOX_VERSION });
      break;

    default:
      console.warn('[Mnemox SW] Unknown message:', message.type);
  }
});

// ── Auth Handlers (Step 7) ────────────────────────────────────────────────────

async function handleSignIn(payload, sendResponse) {
  try {
    const { backendUrl } = await chrome.storage.local.get('backendUrl');
    const { supabaseUrl, supabaseAnonKey } = await getSupabaseConfig(backendUrl);

    const response = await fetch(`${supabaseUrl}/auth/v1/token?grant_type=password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseAnonKey,
      },
      body: JSON.stringify({ email: payload.email, password: payload.password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return sendResponse({ success: false, error: data.error_description || data.msg || 'Sign in failed' });
    }

    // Store JWT + user info
    await chrome.storage.local.set({
      authToken: data.access_token,
      authRefreshToken: data.refresh_token,
      authUser: data.user,
      authPlan: data.user?.app_metadata?.plan || 'free',
      authExpiresAt: Date.now() + (data.expires_in * 1000),
    });

    sendResponse({ success: true, user: data.user });
  } catch (err) {
    console.error('[Mnemox SW] Sign in error:', err);
    sendResponse({ success: false, error: err.message });
  }
}

async function handleSignUp(payload, sendResponse) {
  try {
    const { backendUrl } = await chrome.storage.local.get('backendUrl');
    const { supabaseUrl, supabaseAnonKey } = await getSupabaseConfig(backendUrl);

    const response = await fetch(`${supabaseUrl}/auth/v1/signup?redirect_to=${encodeURIComponent(EMAIL_REDIRECT_URL)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseAnonKey,
      },
      body: JSON.stringify({ email: payload.email, password: payload.password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return sendResponse({ success: false, error: data.error_description || data.msg || 'Sign up failed' });
    }

    // Check if email confirmation is needed
    if (data.user && !data.session) {
      return sendResponse({ success: true, needsConfirmation: true });
    }

    if (data.session) {
      await chrome.storage.local.set({
        authToken: data.session.access_token,
        authRefreshToken: data.session.refresh_token,
        authUser: data.user,
        authPlan: 'free',
        authExpiresAt: Date.now() + (data.session.expires_in * 1000),
      });
    }

    sendResponse({ success: true, needsConfirmation: false });
  } catch (err) {
    console.error('[Mnemox SW] Sign up error:', err);
    sendResponse({ success: false, error: err.message });
  }
}

async function handleSignOut(sendResponse) {
  await chrome.storage.local.set({
    authToken: null,
    authRefreshToken: null,
    authUser: null,
    authPlan: 'free',
    authExpiresAt: null,
  });
  sendResponse({ success: true });
}

async function handleGetAuthState(sendResponse) {
  const state = await chrome.storage.local.get([
    'authToken', 'authUser', 'authPlan', 'authExpiresAt'
  ]);

  const isLoggedIn = !!(state.authToken && state.authExpiresAt && Date.now() < state.authExpiresAt);
  sendResponse({
    isLoggedIn,
    user: isLoggedIn ? state.authUser : null,
    plan: isLoggedIn ? state.authPlan : 'free',
    token: isLoggedIn ? state.authToken : null,
  });
}

// Get Supabase config — defaults to the shipped project config; storage
// values (if ever set, e.g. for local dev against a different project)
// take precedence.
async function getSupabaseConfig(backendUrl) {
  const stored = await chrome.storage.local.get(['supabaseUrl', 'supabaseAnonKey']);
  return {
    supabaseUrl: stored.supabaseUrl || SUPABASE_URL,
    supabaseAnonKey: stored.supabaseAnonKey || SUPABASE_ANON_KEY,
  };
}

// ── Auth header helper ────────────────────────────────────────────────────────
async function getAuthHeaders() {
  const state = await chrome.storage.local.get(['authToken', 'apiKey']);
  if (state.authToken) {
    return { 'Authorization': `Bearer ${state.authToken}`, 'Content-Type': 'application/json' };
  }
  if (state.apiKey) {
    return { 'X-API-Key': state.apiKey, 'Content-Type': 'application/json' };
  }
  return { 'Content-Type': 'application/json' };
}

// ── Memory Handlers ───────────────────────────────────────────────────────────

async function handleMemoryCaptured(payload, sender, sendResponse) {
  // 2026-07-09: diagnostic logging -- see matching note in content.js.
  // These print in the SERVICE WORKER's own console (chrome://extensions ->
  // Mnemox -> "service worker" link -> Inspect), not the page console, so
  // they're easy to miss if you're only looking at the page's DevTools.
  console.log('[Mnemox SW] handleMemoryCaptured received:', payload && payload.source, payload && (payload.content || '').slice(0, 60));
  try {
    const result = await chrome.storage.local.get(['memories', 'memoryCount', 'backendUrl']);
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
    console.log('[Mnemox SW] Storage write confirmed. New total memories:', memories.length);
    updateBadge(memories.length);

    if (result.backendUrl) {
      const headers = await getAuthHeaders();
      saveToBackend(newMemory, result.backendUrl, headers).catch(e =>
        console.warn('[Mnemox SW] Backend save failed:', e.message)
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
    const { backendUrl } = await chrome.storage.local.get('backendUrl');
    const headers = await getAuthHeaders();

    // Need at least auth headers to call backend
    if (!backendUrl || (!headers['Authorization'] && !headers['X-API-Key'])) {
      const { memories = [] } = await chrome.storage.local.get('memories');
      const results = localKeywordSearch(memories, payload.query, payload.limit || 5);
      return sendResponse({ success: true, results, source: 'local' });
    }

    const response = await fetch(`${backendUrl}/memories/search`, {
      method: 'POST',
      headers,
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
    'captureEnabled', 'injectEnabled', 'memoryCount',
    'backendUrl', 'apiKey', 'authPlan', 'authUser',
  ]);
  sendResponse({ success: true, settings });
}

async function handleUpdateSettings(patch, sendResponse) {
  await chrome.storage.local.set(patch);
  sendResponse({ success: true });
}

// ── Backend API call ──────────────────────────────────────────────────────────
async function saveToBackend(memory, backendUrl, headers) {
  const response = await fetch(`${backendUrl}/memories`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content: memory.content, source: memory.source }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// ── Local keyword fallback ────────────────────────────────────────────────────
function localKeywordSearch(memories, query, limit) {
  if (!query || !memories.length) return [];
  const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
  return memories
    .map(m => {
      const text = m.content.toLowerCase();
      const score = queryWords.reduce((acc, word) => acc + (text.includes(word) ? 1 : 0), 0) / queryWords.length;
      return { memory_id: m.id, score, source: m.source,
               content_preview: m.content.slice(0, 200), created_at: m.capturedAt };
    })
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
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
