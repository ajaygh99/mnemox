"""
Step 6 Tests — Dashboard
Run: python -m pytest tests/step6/ -v
All must pass before: git tag v0.6
"""
import os
import pytest

DASH = os.path.join(os.path.dirname(__file__), '..', '..', 'extension', 'dashboard', 'index.html')
DASH_JS = os.path.join(os.path.dirname(__file__), '..', '..', 'extension', 'dashboard', 'dashboard.js')

def read():
    # 2026-07-09: the dashboard's JS used to be an inline <script> block
    # inside index.html. Manifest V3's default CSP (script-src 'self')
    # blocks ALL inline script execution in extension pages -- so that
    # inline block silently never ran, which was the real root cause of the
    # dashboard always showing "0 memories" (not a live-refresh problem).
    # Chrome's extension error console confirmed it: "Executing inline
    # script violates the following Content Security Policy directive:
    # script-src 'self'... The action has been blocked."
    # Fix: the JS now lives in an external dashboard.js file loaded via
    # <script src="dashboard.js">, which is allowed under 'self'. These
    # tests check the dashboard as a whole, so read() concatenates both
    # files -- most of the assertions below don't care which file a given
    # string lives in.
    with open(DASH) as f:
        html = f.read()
    with open(DASH_JS) as f:
        js = f.read()
    return html + '\n' + js

def test_dashboard_file_exists():
    assert os.path.exists(DASH)

def test_has_memories_page():
    assert 'page-memories' in read()

def test_has_search_page():
    assert 'page-search' in read()

def test_has_settings_page():
    assert 'page-settings' in read()

def test_stats_cards_present():
    # 2026-07-18: the four static stat cards (stat-total/stat-chatgpt/...)
    # were replaced by clickable filter chips -- see
    # test_source_chips_cover_six_platforms_and_stay_separate below for the
    # full regression coverage of that change.
    code = read()
    assert 'chip-count-all' in code
    assert 'chip-count-chatgpt' in code
    assert 'chip-count-claude' in code

def test_memory_list_render():
    assert 'renderMemories' in read()

def test_filter_by_source():
    assert 'filterMemories' in read()
    assert 'source-chips' in read()
    assert 'activeSource' in read()

def test_source_chips_cover_six_platforms_and_stay_separate():
    # 2026-07-18: the stat cards used to be non-clickable and merged Gemini
    # + Copilot into one combined count with no way to filter to just one of
    # them. Fixed by replacing the stats row with clickable chips (one per
    # source, always kept separate) and adding Perplexity + Grok as
    # additional filterable categories.
    code = read()
    for source in ('chatgpt', 'claude', 'gemini', 'copilot', 'perplexity', 'grok'):
        assert 'data-source="' + source + '"' in code
        assert 'chip-count-' + source in code
    assert 'Gemini + Copilot' not in code
    assert 'handleChipClick' in code

def test_search_input_present():
    assert 'mem-search' in read()

def test_delete_memory_function():
    assert 'deleteMemory' in read()

def test_expand_memory_function():
    assert 'expandMemory' in read()

def test_semantic_search_function():
    assert 'semanticSearch' in read()

def test_search_calls_service_worker():
    assert 'MNEMOX_SEARCH_MEMORIES' in read()

def test_backend_url_setting():
    assert 's-backend-url' in read()

def test_api_key_setting():
    assert 's-api-key' in read()

def test_save_backend_settings_function():
    assert 'saveBackendSettings' in read()

def test_connection_test_on_save():
    assert '/health' in read()

def test_capture_toggle():
    assert 't-capture' in read()
    assert 'captureEnabled' in read()

def test_inject_toggle():
    assert 't-inject' in read()
    assert 'injectEnabled' in read()

def test_toggle_setting_function():
    assert 'toggleSetting' in read()

def test_clear_all_memories():
    assert 'clearAllMemories' in read()

def test_clear_asks_confirmation():
    assert 'confirm(' in read()

def test_source_badges_all_4():
    code = read()
    assert 'source-chatgpt' in code
    assert 'source-claude' in code
    assert 'source-gemini' in code
    assert 'source-copilot' in code

def test_chrome_storage_used():
    assert 'chrome.storage.local' in read()

def test_dev_fallback_no_chrome():
    assert 'typeof chrome' in read()

def test_html_escape_function():
    assert 'escHtml' in read()

def test_brand_name_present():
    assert 'MNEMOX' in read()

def test_version_updated():
    # 2026-07-09: the dashboard footer used to hardcode a version string
    # ("v0.6.0 - Mnemox") that silently went stale with every release and
    # gave no way to tell which build was actually loaded. It's now rendered
    # dynamically from chrome.runtime.getManifest().version at runtime, so
    # there's no hardcoded version string to assert on here anymore --
    # assert the dynamic mechanism is wired up instead (see tests/step9 for
    # full regression coverage of this behavior).
    body = read()
    assert 'id="sidebar-version"' in body
    assert 'chrome.runtime.getManifest().version' in body

def test_settings_persisted_to_storage():
    assert 'chrome.storage.local.set' in read()

def test_newest_first_ordering():
    assert 'reverse()' in read()
