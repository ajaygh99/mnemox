"""
Step 6 Tests — Dashboard
Run: python -m pytest tests/step6/ -v
All must pass before: git tag v0.6
"""
import os
import pytest

DASH = os.path.join(os.path.dirname(__file__), '..', '..', 'extension', 'dashboard', 'index.html')

def read():
    with open(DASH) as f:
        return f.read()

def test_dashboard_file_exists():
    assert os.path.exists(DASH)

def test_has_memories_page():
    assert 'page-memories' in read()

def test_has_search_page():
    assert 'page-search' in read()

def test_has_settings_page():
    assert 'page-settings' in read()

def test_stats_cards_present():
    code = read()
    assert 'stat-total' in code
    assert 'stat-chatgpt' in code
    assert 'stat-claude' in code

def test_memory_list_render():
    assert 'renderMemories' in read()

def test_filter_by_source():
    assert 'filterMemories' in read()
    assert 'mem-filter' in read()

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
    assert '0.6.0' in read()

def test_settings_persisted_to_storage():
    assert 'chrome.storage.local.set' in read()

def test_newest_first_ordering():
    assert 'reverse()' in read()
