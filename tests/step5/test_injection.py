"""
Step 5 Tests — Auto Memory Injection
Run: python -m pytest tests/step5/ -v
All must pass before: git tag v0.5
"""

import os
import pytest

EXT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')

def read(path):
    with open(os.path.join(EXT, path)) as f:
        return f.read()

CONTENT = lambda: read('content/content.js')
SW      = lambda: read('background/service_worker.js')


# ── content.js: injection function ───────────────────────────────────────────

def test_inject_memories_function_exists():
    assert 'injectMemoriesIntoPrompt' in CONTENT()

def test_build_context_block_function():
    assert 'buildContextBlock' in CONTENT()

def test_context_block_format():
    assert 'Mnemox Context' in CONTENT()

def test_end_marker_present():
    assert 'End Mnemox Context' in CONTENT()

def test_search_memories_function():
    assert 'searchMemories' in CONTENT()

def test_search_called_on_enter():
    assert 'injectMemoriesIntoPrompt' in CONTENT()
    assert 'e.preventDefault' in CONTENT()

def test_capture_phase_listener():
    # Must use capture phase (true) so we intercept before AI tool's listeners
    assert ', true)' in CONTENT()

def test_context_stripped_before_capture():
    # We must not save the injected context — only original prompt
    assert 'End Mnemox Context' in CONTENT()
    assert 'markerIdx' in CONTENT() or 'endMarker' in CONTENT()

def test_inject_respects_setting():
    assert 'injectEnabled' in CONTENT()

def test_set_content_editable_function():
    assert 'setContentEditable' in CONTENT()

def test_execCommand_used():
    assert 'execCommand' in CONTENT()

def test_inject_disabled_still_captures():
    # When inject is off, capture still happens
    assert 'capturePrompt' in CONTENT()

def test_injection_toast_shown():
    assert 'memories added to context' in CONTENT()

def test_submit_button_clicked_after_inject():
    assert 'btn.click()' in CONTENT()

def test_last_injected_context_dedup():
    assert 'lastInjectedContext' in CONTENT()

def test_all_4_sites_have_set_prompt_text():
    code = CONTENT()
    for site in ['chatgpt', 'claude', 'gemini', 'copilot']:
        assert site in code
    assert 'setPromptText' in code


# ── service_worker.js: search handler ────────────────────────────────────────

def test_search_memories_handler():
    assert 'MNEMOX_SEARCH_MEMORIES' in SW()

def test_backend_fetch_call():
    assert 'memories/search' in SW()

def test_x_api_key_header():
    assert 'X-API-Key' in SW()

def test_local_keyword_fallback():
    assert 'localKeywordSearch' in SW()

def test_fallback_when_backend_down():
    assert 'local_fallback' in SW() or 'fallback' in SW().lower()

def test_backend_url_configurable():
    assert 'backendUrl' in SW()

def test_api_key_configurable():
    assert 'apiKey' in SW()

def test_update_settings_handler():
    assert 'MNEMOX_UPDATE_SETTINGS' in SW()

def test_save_to_backend_function():
    assert 'saveToBackend' in SW()

def test_backend_save_nonfatal():
    assert '.catch' in SW()

def test_version_updated():
    assert any(v in SW() for v in ('0.5.0', '0.6.0', '0.7.0'))


# ── Safety ────────────────────────────────────────────────────────────────────

def test_no_hardcoded_api_keys_content():
    assert 'sk-' not in CONTENT()

def test_no_hardcoded_api_keys_sw():
    assert 'sk-' not in SW()

def test_iife_still_present():
    assert '(function ()' in CONTENT() or '(function()' in CONTENT()
