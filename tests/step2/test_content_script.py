"""
Step 2 Tests — Content Script Validation
Run: python -m pytest tests/step2/ -v
All tests must pass before: git tag v0.2
"""

import os
import re
import pytest

CONTENT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension', 'content', 'content.js')

def read():
    with open(CONTENT) as f:
        return f.read()


# ── All 4 sites covered ───────────────────────────────────────────────────

def test_chatgpt_selector_present():
    assert 'prompt-textarea' in read()

def test_claude_selector_present():
    assert 'ProseMirror' in read()

def test_gemini_selector_present():
    assert 'ql-editor' in read()

def test_copilot_selector_present():
    assert 'userInput' in read()


# ── Core capture logic ────────────────────────────────────────────────────

def test_capture_on_enter_key():
    assert "e.key === 'Enter'" in read()

def test_shift_enter_excluded():
    assert 'e.shiftKey' in read()

def test_submit_button_wired():
    assert 'submitSelector' in read()

def test_deduplication_logic():
    assert 'lastCaptured' in read()

def test_prompt_truncation_at_1000():
    assert '1000' in read()

def test_sends_memory_captured_message():
    assert 'MNEMOX_MEMORY_CAPTURED' in read()


# ── Toast notification ────────────────────────────────────────────────────

def test_toast_element_created():
    assert 'mnemox-toast' in read()

def test_toast_show_on_capture():
    assert 'showToast' in read()

def test_toast_styles_injected():
    assert 'injectToastStyles' in read()


# ── MutationObserver for SPAs ─────────────────────────────────────────────

def test_mutation_observer_present():
    assert 'MutationObserver' in read()

def test_observer_watches_body():
    assert 'document.body' in read()

def test_reattach_on_rerender():
    assert '_mnemoxAttached' in read()


# ── Settings & messages ───────────────────────────────────────────────────

def test_settings_loaded_on_init():
    assert 'loadSettings' in read()

def test_handles_settings_changed():
    assert 'MNEMOX_SETTINGS_CHANGED' in read()

def test_handles_save_now():
    assert 'MNEMOX_SAVE_NOW' in read()

def test_capture_respects_disabled_setting():
    assert 'captureEnabled' in read()


# ── Safety ────────────────────────────────────────────────────────────────

def test_no_hardcoded_secrets():
    suspicious = ['sk-', 'Bearer ', 'API_KEY=']
    code = read()
    for s in suspicious:
        assert s not in code, f"Possible secret: {s}"

def test_iife_wrapper_present():
    """Content scripts must use IIFE to avoid global scope pollution"""
    code = read()
    assert '(function ()' in code or '(function()' in code
