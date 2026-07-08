"""
Step 9 Tests — Sign-Up Regression Guard
Run: python -m pytest tests/step9/ -v

Chrome Web Store rejected the 2026-07-08 submission because "Sign up for free"
was unreproducible. Root cause: service_worker.js's getSupabaseConfig() had no
real default and silently fell back to a placeholder domain
('https://your-project.supabase.co') with an empty apikey whenever
chrome.storage.local had no supabaseUrl/supabaseAnonKey set — which was
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


# ── No placeholder / empty fallback ──────────────────────────────────────────

def test_no_placeholder_supabase_domain():
    assert 'your-project.supabase.co' not in sw(), (
        "service_worker.js still falls back to the placeholder Supabase domain — "
        "sign up/sign in will fail exactly like the Chrome Web Store rejection."
    )


def test_supabase_url_constant_defined_and_real():
    match = re.search(r"const\s+SUPABASE_URL\s*=\s*'([^']+)'", sw())
    assert match, "SUPABASE_URL constant not found in service_worker.js"
    url = match.group(1)
    assert url.startswith('https://') and '.supabase.co' in url
    assert 'your-project' not in url


def test_supabase_anon_key_constant_defined_and_nonempty():
    match = re.search(r"const\s+SUPABASE_ANON_KEY\s*=\s*'([^']*)'", sw())
    assert match, "SUPABASE_ANON_KEY constant not found in service_worker.js"
    assert len(match.group(1)) > 10, "SUPABASE_ANON_KEY must not be empty/placeholder"


def test_get_supabase_config_defaults_to_real_constants():
    body = sw()
    # getSupabaseConfig() must fall back to the real constants, not '' or a placeholder
    fn_match = re.search(r"async function getSupabaseConfig[\s\S]*?\n}", body)
    assert fn_match, "getSupabaseConfig() not found"
    fn_body = fn_match.group(0)
    assert "SUPABASE_URL" in fn_body
    assert "SUPABASE_ANON_KEY" in fn_body
    assert "your-project.supabase.co" not in fn_body
    assert "|| ''" not in fn_body.replace("supabaseAnonKey: stored.supabaseAnonKey || SUPABASE_ANON_KEY", "")


# ── Sign up / sign in still wired to Supabase REST endpoints ────────────────

def test_signup_hits_supabase_rest_endpoint():
    assert '/auth/v1/signup' in sw()


def test_signin_hits_supabase_rest_endpoint():
    assert '/auth/v1/token?grant_type=password' in sw()


def test_signup_sends_apikey_header():
    body = sw()
    signup_fn = re.search(r"async function handleSignUp[\s\S]*?\n}\n", body)
    assert signup_fn
    assert "'apikey': supabaseAnonKey" in signup_fn.group(0)
