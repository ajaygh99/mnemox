"""
Step 10 Tests -- Anonymous Mode / Second Chrome Web Store Rejection
Run: python -m pytest tests/step10/ -v

Chrome Web Store rejected the 2026-07-10 submission (v0.1.16) a second time,
this time for a different reason than tests/step9 guards against:

    Violation: Inaccurate Description - Non functional
    "Dashboard" -- not working or not reproducible in review.

Root cause: popup.js's init() unconditionally redirected to login.html
whenever the user wasn't signed in (see the exact code tests/step9 had
locked in). Sign-up requires email confirmation via Supabase, which a
reviewer cannot complete -- so the reviewer got stuck on the login screen
and never saw the popup's "View Memories" button, let alone the dashboard
page it opens. This had nothing to do with the dashboard's own code (the
CSP/inline-script bug from step6 was already fixed); the dashboard was
simply unreachable.

The fix: capture, inject, and the dashboard never actually needed a backend
account -- they all read/write chrome.storage.local directly (see
handleMemoryCaptured's local-first write and handleSearchMemories's local
keyword fallback in service_worker.js, both already backend-optional before
this change). Only cloud sync, backend semantic search, and paid plans need
a session. So popup.js now always renders; signing in is offered via an
explicit "Sign in" link, never forced.

These tests lock in that the popup and dashboard are reachable without an
account, so this rejection reason can't silently regress.
"""

import os
import re

EXT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')


def popup_js():
    with open(os.path.join(EXT, 'popup', 'popup.js')) as f:
        return f.read()


def popup_html():
    with open(os.path.join(EXT, 'popup', 'popup.html')) as f:
        return f.read()


def login_html():
    with open(os.path.join(EXT, 'popup', 'login.html')) as f:
        return f.read()


def login_js():
    with open(os.path.join(EXT, 'popup', 'login.js')) as f:
        return f.read()


def service_worker():
    with open(os.path.join(EXT, 'background', 'service_worker.js')) as f:
        return f.read()


# -- Core fix: no forced redirect ---------------------------------------------

def test_init_does_not_redirect_unconditionally():
    # init() legitimately contains 'login.html' now (the optional Sign in
    # link's click handler), so the check is that init() never RETURNS
    # early based on auth state before it finishes rendering the popup --
    # not that the string is absent altogether.
    body = popup_js()
    fn_match = re.search(r"async function init\(\)[\s\S]*?\n}", body)
    assert fn_match, "init() not found"
    init_body = fn_match.group(0)
    auth_idx = init_body.find('checkAuth()')
    settings_idx = init_body.find('loadSettings()')
    assert auth_idx != -1 and settings_idx != -1 and auth_idx < settings_idx
    assert 'return' not in init_body[auth_idx:settings_idx]


def test_init_computes_islogged_in_without_early_return_on_false():
    body = popup_js()
    assert 'const isLoggedIn' in body


# -- Dashboard / core features remain wired regardless of auth state ---------

def test_view_memories_button_wired_outside_any_auth_check():
    # The dashboard button listener must be reached on every init() call,
    # not just an authenticated branch.
    fn_match = re.search(r"async function init\(\)[\s\S]*?\n}", popup_js())
    assert fn_match
    assert "getElementById('view-memories-btn')" in fn_match.group(0)


def test_dashboard_reads_local_storage_directly():
    with open(os.path.join(EXT, 'dashboard', 'dashboard.js')) as f:
        dash = f.read()
    assert "chrome.storage.local.get(" in dash


def test_search_has_local_fallback_when_unauthenticated():
    # handleSearchMemories() must already degrade to a local keyword search
    # when there's no backend auth -- this is what makes it safe to let
    # signed-out users reach search at all.
    fn_match = re.search(r"async function handleSearchMemories[\s\S]*?\n}", service_worker())
    assert fn_match
    assert 'localKeywordSearch' in fn_match.group(0)


def test_capture_writes_to_local_storage_before_any_backend_call():
    fn_match = re.search(r"async function handleMemoryCaptured[\s\S]*?\n}", service_worker())
    assert fn_match
    body = fn_match.group(0)
    local_write_idx = body.find('chrome.storage.local.set(')
    backend_call_idx = body.find('saveToBackend(')
    assert local_write_idx != -1 and backend_call_idx != -1
    assert local_write_idx < backend_call_idx, \
        "local storage must be written before any optional backend sync"


# -- Sign-in stays available, just optional -----------------------------------

def test_signin_link_present_in_popup_html():
    assert 'id="signin-link"' in popup_html()

def test_signin_link_wired_in_popup_js():
    assert "getElementById('signin-link')" in popup_js()
    assert "getElementById('signin-link')?.addEventListener('click'" in popup_js()

def test_signout_rerenders_locally_instead_of_redirecting():
    fn_match = re.search(r"getElementById\('signout-btn'\)\?\.addEventListener[\s\S]*?\n  \}\);", popup_js())
    assert fn_match, "signout-btn click handler not found"
    assert "window.location.href = 'login.html'" not in fn_match.group(0)


def test_login_page_offers_a_way_back_without_signing_in():
    assert 'id="skip-login"' in login_html()
    assert "getElementById('skip-login')" in login_js()
    assert "popup.html" in login_js()
