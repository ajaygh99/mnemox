"""
Step 1 Tests — Manifest & File Structure Validation
Run: python -m pytest tests/step1/ -v
All tests must pass before: git tag v0.1
"""

import json
import os
import pytest

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')


def load_manifest():
    path = os.path.join(BASE, 'manifest.json')
    with open(path) as f:
        return json.load(f)


# ── Manifest tests ─────────────────────────────────────────────────────────

def test_manifest_exists():
    assert os.path.exists(os.path.join(BASE, 'manifest.json')), \
        "manifest.json missing"

def test_manifest_version_3():
    m = load_manifest()
    assert m['manifest_version'] == 3, "Must use Manifest V3"

def test_manifest_has_name():
    m = load_manifest()
    assert 'Mnemox' in m['name'], "Product name missing from manifest"

def test_manifest_host_permissions():
    m = load_manifest()
    hosts = m.get('host_permissions', [])
    required = ['chat.openai.com', 'claude.ai', 'gemini.google.com', 'copilot.microsoft.com']
    for host in required:
        assert any(host in h for h in hosts), f"Missing host permission: {host}"

def test_manifest_background_service_worker():
    m = load_manifest()
    bg = m.get('background', {})
    assert 'service_worker' in bg, "background.service_worker missing"
    assert bg['service_worker'] == 'background/service_worker.js'

def test_manifest_action_popup():
    m = load_manifest()
    assert m.get('action', {}).get('default_popup') == 'popup/popup.html'

def test_manifest_content_scripts_cover_all_sites():
    m = load_manifest()
    scripts = m.get('content_scripts', [])
    all_matches = [match for s in scripts for match in s.get('matches', [])]
    sites = ['chat.openai.com', 'claude.ai', 'gemini.google.com', 'copilot.microsoft.com']
    for site in sites:
        assert any(site in match for match in all_matches), \
            f"Content script not targeting: {site}"


# ── File structure tests ────────────────────────────────────────────────────

def test_popup_html_exists():
    assert os.path.exists(os.path.join(BASE, 'popup', 'popup.html'))

def test_popup_js_exists():
    assert os.path.exists(os.path.join(BASE, 'popup', 'popup.js'))

def test_service_worker_exists():
    assert os.path.exists(os.path.join(BASE, 'background', 'service_worker.js'))

def test_content_script_exists():
    assert os.path.exists(os.path.join(BASE, 'content', 'content.js'))


# ── Content sanity tests ────────────────────────────────────────────────────

def test_service_worker_handles_ping():
    path = os.path.join(BASE, 'background', 'service_worker.js')
    with open(path) as f:
        code = f.read()
    assert 'MNEMOX_PING' in code, "Service worker must handle MNEMOX_PING"

def test_service_worker_handles_memory_captured():
    path = os.path.join(BASE, 'background', 'service_worker.js')
    with open(path) as f:
        code = f.read()
    assert 'MNEMOX_MEMORY_CAPTURED' in code

def test_content_script_detects_all_sites():
    path = os.path.join(BASE, 'content', 'content.js')
    with open(path) as f:
        code = f.read()
    for site in ['chatgpt', 'claude', 'gemini', 'copilot']:
        assert site in code, f"Content script missing site: {site}"

def test_popup_js_has_toggle_handlers():
    path = os.path.join(BASE, 'popup', 'popup.js')
    with open(path) as f:
        code = f.read()
    assert 'captureToggle' in code or 'capture-toggle' in code
    assert 'injectToggle' in code or 'inject-toggle' in code

def test_no_secrets_in_code():
    """Ensure no API keys or secrets are hardcoded"""
    suspicious = ['sk-', 'Bearer=', 'API_KEY=', 'SECRET=']
    for root, _, files in os.walk(BASE):
        for fname in files:
            if not fname.endswith(('.js', '.json', '.html')):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath) as f:
                content = f.read()
            for pattern in suspicious:
                assert pattern not in content, \
                    f"Possible secret found in {fname}: '{pattern}'"
