"""
Step 9 Tests -- Sign-Up Regression Guard
Run: python -m pytest tests/step9/ -v

Chrome Web Store rejected the 2026-07-08 submission because "Sign up for free"
was unreproducible. Root cause: service_worker.js's getSupabaseConfig() had no
real default and silently fell back to a placeholder domain
('https://your-project.supabase.co') with an empty apikey whenever
chrome.storage.local had no supabaseUrl/supabaseAnonKey set -- which was
always, since nothing in the codebase ever wrote those keys. Every sign up
and sign in attempt (including the reviewer's) was guaranteed to fail.

These tests lock in the fix so this can't silently regress again.
"""

import os
import re
import pytest

EXT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')


def sw():
    with open(os.path.join(EXT, 'background', 'service_worker.js')) as f:
        return f.read()


def login_js():
    with open(os.path.join(EXT, 'popup', 'login.js')) as f:
        return f.read()


def popup_js():
    with open(os.path.join(EXT, 'popup', 'popup.js')) as f:
        return f.read()


def popup_html():
    with open(os.path.join(EXT, 'popup', 'popup.html')) as f:
        return f.read()


# -- No placeholder / empty fallback -----------------------------------------

def test_no_placeholder_supabase_domain():
    assert 'your-project.supabase.co' not in sw()


def test_supabase_url_constant_defined_and_real():
    match = re.search(r"const\s+SUPABASE_URL\s*=\s*'([^']+)'", sw())
    assert match, "SUPABASE_URL constant not found in service_worker.js"
    url = match.group(1)
    assert url.startswith('https://') and '.supabase.co' in url
    assert 'your-project' not in url


def test_supabase_anon_key_constant_defined_and_nonempty():
    match = re.search(r"const\s+SUPABASE_ANON_KEY\s*=\s*'([^']*)'", sw())
    assert match, "SUPABASE_ANON_KEY constant not found in service_worker.js"
    assert len(match.group(1)) > 10


def test_get_supabase_config_defaults_to_real_constants():
    body = sw()
    fn_match = re.search(r"async function getSupabaseConfig[\s\S]*?\n}", body)
    assert fn_match, "getSupabaseConfig() not found"
    fn_body = fn_match.group(0)
    assert "SUPABASE_URL" in fn_body
    assert "SUPABASE_ANON_KEY" in fn_body
    assert "your-project.supabase.co" not in fn_body


# -- Sign up / sign in still wired to Supabase REST endpoints ----------------

def test_signup_hits_supabase_rest_endpoint():
    assert '/auth/v1/signup' in sw()


def test_signin_hits_supabase_rest_endpoint():
    assert '/auth/v1/token?grant_type=password' in sw()


def test_signup_sends_apikey_header():
    body = sw()
    signup_fn = re.search(r"async function handleSignUp[\s\S]*?\n}\n", body)
    assert signup_fn
    assert "'apikey': supabaseAnonKey" in signup_fn.group(0)


# -- Regression: confirmation email must not redirect to a dead localhost link
# 2026-07-08 manual test: clicking the Supabase confirmation email link sent
# the browser to localhost:3000#error=access_denied&error_code=otp_expired
# ("This site can't be reached"). Root cause: nothing set redirect_to on the
# signup call, so Supabase fell back to its project default Site URL, which
# is the dev placeholder http://localhost:3000. Fixed by passing an explicit
# redirect_to pointing at the live marketing site.

def test_email_redirect_url_constant_defined_and_not_localhost():
    match = re.search(r"const\s+EMAIL_REDIRECT_URL\s*=\s*'([^']+)'", sw())
    assert match, "EMAIL_REDIRECT_URL constant not found in service_worker.js"
    url = match.group(1)
    assert url.startswith('https://')
    assert 'localhost' not in url


def test_signup_passes_redirect_to_param():
    body = sw()
    signup_fn = re.search(r"async function handleSignUp[\s\S]*?\n}\n", body)
    assert signup_fn, "handleSignUp() not found"
    fn_body = signup_fn.group(0)
    assert 'redirect_to=' in fn_body
    assert 'EMAIL_REDIRECT_URL' in fn_body


# -- Regression: post-signup message must be unmissable, not a silent no-op --
# Manual test showed signing up gave no visible confirmation in the popup.
# Replaced the innerHTML += status line with a dedicated confirmation screen.

def test_confirmation_screen_function_exists():
    assert 'function showConfirmationScreen' in login_js()


def test_signup_handler_calls_confirmation_screen():
    assert 'showConfirmationScreen(email)' in login_js()


def test_confirmation_screen_shows_users_email():
    fn_match = re.search(r"function showConfirmationScreen[\s\S]*?\n}\n", login_js())
    assert fn_match
    assert 'strong.textContent = email' in fn_match.group(0)


# -- Regression guard: verified working flow (2026-07-08 manual pass) --------
# Manual test confirmed: sign up -> confirmation email delivered -> confirm
# link -> sign in -> popup shows authenticated view -> "View Memories" opens
# the dashboard. Lock in the wiring so it can't silently break.

def test_popup_redirects_unauthenticated_to_login():
    body = popup_js()
    assert "window.location.href = 'login.html'" in body
    assert 'isLoggedIn' in body


def test_view_memories_button_exists_in_html():
    assert 'id="view-memories-btn"' in popup_html()


def test_view_memories_button_opens_dashboard():
    body = popup_js()
    assert "getElementById('view-memories-btn')" in body
    assert "dashboard/index.html" in body


def test_dashboard_html_exists():
    assert os.path.exists(os.path.join(EXT, 'dashboard', 'index.html'))


# -- Regression: dashboard must live-refresh, not just load once --------------
# 2026-07-08 manual test: captured 2 memories while the dashboard tab was
# already open; it kept showing "0 Total memories" because loadData() only
# ever ran once at page load with no chrome.storage.onChanged listener.

def dashboard_html():
    with open(os.path.join(EXT, 'dashboard', 'index.html')) as f:
        return f.read()


def test_dashboard_has_storage_onchanged_listener():
    assert 'chrome.storage.onChanged.addListener' in dashboard_html()


def test_dashboard_onchanged_listener_calls_loaddata():
    body = dashboard_html()
    idx = body.find('chrome.storage.onChanged.addListener')
    assert idx != -1, "onChanged listener not found"
    assert 'loadData();' in body[idx:idx + 400]


def test_dashboard_onchanged_watches_memories_key():
    body = dashboard_html()
    idx = body.find('chrome.storage.onChanged.addListener')
    assert idx != -1
    assert 'changes.memories' in body[idx:idx + 400]


# -- Regression: version/extension-ID must be visible in the UI ---------------
# 2026-07-09 manual test: dashboard showed 0 memories while the popup showed
# a nonzero count, on a genuinely fresh tab (not a stale-load issue). Root
# cause investigation found the storage read/write path is correct end to
# end -- the likely explanation is that two separate unpacked copies of the
# extension got loaded at different times (user was confused between two
# project folders throughout this project), each with its own extension ID
# and therefore its own separate chrome.storage.local. Surfacing the manifest
# version + runtime extension ID in both the popup and dashboard lets this be
# diagnosed at a glance instead of guessing.

def test_dashboard_shows_dynamic_version_not_hardcoded():
    body = dashboard_html()
    assert 'id="sidebar-version"' in body
    assert 'v0.6.0 . Mnemox<' not in body, \
        "sidebar footer must not be a hardcoded stale version string"


def test_dashboard_version_reads_from_manifest():
    body = dashboard_html()
    # sidebar-version appears twice: once as the HTML element id, once again
    # inside the showVersion() script block near the end of the file that
    # actually populates it. Search from the last occurrence (the script).
    idx = body.rfind('sidebar-version')
    assert idx != -1
    tail = body[idx:idx + 900]
    assert 'chrome.runtime.getManifest().version' in tail
    assert 'chrome.runtime.id' in tail


def test_popup_shows_dynamic_version():
    assert 'id="popup-version"' in popup_html()


def test_popup_version_reads_from_manifest():
    body = popup_js()
    idx = body.find('function showVersion')
    assert idx != -1, "showVersion() not found in popup.js"
    fn_body = body[idx:idx + 500]
    assert 'chrome.runtime.getManifest().version' in fn_body
    assert 'chrome.runtime.id' in fn_body


def test_popup_calls_showversion_on_load():
    assert "addEventListener('DOMContentLoaded', showVersion)" in popup_js()
