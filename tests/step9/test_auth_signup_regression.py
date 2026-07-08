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
