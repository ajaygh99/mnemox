"""Regression guards for the v0.1.18 behavior-preserving tuning pass."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_supabase_calls_do_not_block_async_event_loop():
    assert "asyncio.to_thread" in read("backend/database.py")


def test_health_dependencies_run_concurrently():
    assert "db_ok, vec_ok = await asyncio.gather" in read("backend/main.py")


def test_memory_list_and_count_run_concurrently():
    assert "memories, total = await asyncio.gather" in read("backend/main.py")


def test_embedding_cache_is_bounded():
    source = read("backend/embeddings.py")
    assert "EMBEDDING_CACHE_MAX_SIZE" in source
    assert "popitem(last=False)" in source


def test_dom_observer_coalesces_mutation_bursts():
    source = read("extension/content/content.js")
    assert "observerTimer" in source
    assert "hasAddedNodes" in source


def test_semantic_search_has_timeout_and_local_fallback_path():
    source = read("extension/background/service_worker.js")
    assert "new AbortController()" in source
    assert "controller.abort()" in source
    assert "local_fallback" in source


def test_dashboard_filter_is_debounced():
    source = read("extension/dashboard/dashboard.js")
    assert "scheduleFilterMemories" in source
    assert "setTimeout(filterMemories, 100)" in source


def test_content_script_has_hard_injection_budget():
    source = read("extension/content/content.js")
    assert "INJECTION_BUDGET_MS = 350" in source
    assert "if (finished) return" in source
    assert "POST_INJECTION_SETTLE_MS = 20" in source


def test_remote_search_budget_is_below_content_watchdog():
    source = read("extension/background/service_worker.js")
    assert "REMOTE_SEARCH_BUDGET_MS = 250" in source
    assert "controller.abort(), REMOTE_SEARCH_BUDGET_MS" in source


def test_dynamic_send_buttons_do_not_create_false_extension_errors():
    source = read("extension/content/content.js")
    assert "document.addEventListener('click', handleSubmitClick, true)" in source
    assert "console.warn('[Mnemox] No submit button matched" not in source
    assert "Candidate buttons on page" not in source


def test_extension_reload_is_contained_and_actionable():
    source = read("extension/content/content.js")
    assert "function safeSendMessage" in source
    assert "try {" in source
    assert "notifyContextInvalidated" in source
    assert "Refresh this tab to reconnect memory capture" in source
    assert source.count("chrome.runtime.sendMessage") == 2  # comment + wrapper only


def test_expected_latency_budget_does_not_emit_extension_warning():
    source = read("extension/content/content.js")
    assert "console.warn('[Mnemox] Injection budget reached" not in source


def test_release_version_is_0_1_21():
    assert '"version": "0.1.21"' in read("extension/manifest.json")
