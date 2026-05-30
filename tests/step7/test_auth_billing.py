"""
Step 7 Tests — Supabase Auth + Stripe Billing + Team Memory
Run: python -m pytest tests/step7/ -v
All must pass before: git tag v0.7
"""

import os
import pytest

BACKEND = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
EXT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')

def read(filename, base=None):
    base = base or BACKEND
    with open(os.path.join(base, filename)) as f:
        return f.read()

def ext(path):
    with open(os.path.join(EXT, path)) as f:
        return f.read()


# ── File existence ─────────────────────────────────────────────────────────────

def test_auth_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'auth.py'))

def test_billing_py_exists():
    assert os.path.exists(os.path.join(BACKEND, 'billing.py'))

def test_supabase_schema_step7_exists():
    assert os.path.exists(os.path.join(BACKEND, 'supabase_schema_step7.sql'))

def test_login_html_exists():
    assert os.path.exists(os.path.join(EXT, 'popup', 'login.html'))

def test_login_js_exists():
    assert os.path.exists(os.path.join(EXT, 'popup', 'login.js'))


# ── requirements.txt ──────────────────────────────────────────────────────────

def test_stripe_in_requirements():
    assert 'stripe' in read('requirements.txt').lower()

def test_pyjwt_in_requirements():
    assert 'pyjwt' in read('requirements.txt').lower() or 'jwt' in read('requirements.txt').lower()


# ── config.py ─────────────────────────────────────────────────────────────────

def test_stripe_secret_key_in_config():
    assert 'stripe_secret_key' in read('config.py')

def test_stripe_webhook_secret_in_config():
    assert 'stripe_webhook_secret' in read('config.py')

def test_stripe_pro_price_id_in_config():
    assert 'stripe_pro_price_id' in read('config.py')

def test_stripe_team_price_id_in_config():
    assert 'stripe_team_price_id' in read('config.py')

def test_supabase_jwt_secret_in_config():
    assert 'supabase_jwt_secret' in read('config.py')


# ── auth.py ───────────────────────────────────────────────────────────────────

def test_decode_supabase_jwt_function():
    assert 'decode_supabase_jwt' in read('auth.py')

def test_get_current_user_function():
    assert 'get_current_user' in read('auth.py')

def test_current_user_class():
    assert 'class CurrentUser' in read('auth.py')

def test_memory_namespace_property():
    assert 'memory_namespace' in read('auth.py')

def test_team_namespace_logic():
    assert 'team:' in read('auth.py')

def test_require_plan_function():
    assert 'require_plan' in read('auth.py')

def test_plan_order_defined():
    assert 'plan_order' in read('auth.py')

def test_bearer_token_supported():
    assert 'Bearer' in read('auth.py')

def test_legacy_api_key_fallback():
    assert 'x_api_key' in read('auth.py')

def test_memory_limit_by_plan():
    assert 'memory_limit' in read('auth.py')

def test_free_plan_limit_50():
    assert '50' in read('auth.py')


# ── billing.py ────────────────────────────────────────────────────────────────

def test_plans_dict_defined():
    assert 'PLANS' in read('billing.py')

def test_free_plan_in_plans():
    assert '"free"' in read('billing.py') or "'free'" in read('billing.py')

def test_pro_plan_in_plans():
    assert '"pro"' in read('billing.py') or "'pro'" in read('billing.py')

def test_team_plan_in_plans():
    assert '"team"' in read('billing.py') or "'team'" in read('billing.py')

def test_get_or_create_customer_function():
    assert 'get_or_create_customer' in read('billing.py')

def test_create_checkout_session_function():
    assert 'create_checkout_session' in read('billing.py')

def test_create_billing_portal_session_function():
    assert 'create_billing_portal_session' in read('billing.py')

def test_handle_stripe_webhook_function():
    assert 'handle_stripe_webhook' in read('billing.py')

def test_webhook_signature_verification():
    assert 'construct_event' in read('billing.py')

def test_subscription_created_handled():
    assert 'subscription.created' in read('billing.py')

def test_subscription_deleted_handled():
    assert 'subscription.deleted' in read('billing.py')

def test_update_user_plan_function():
    assert '_update_user_plan' in read('billing.py')


# ── main.py ───────────────────────────────────────────────────────────────────

def test_auth_me_endpoint():
    assert '/auth/me' in read('main.py')

def test_billing_plans_endpoint():
    assert '/billing/plans' in read('main.py')

def test_billing_checkout_endpoint():
    assert '/billing/checkout' in read('main.py')

def test_billing_portal_endpoint():
    assert '/billing/portal' in read('main.py')

def test_stripe_webhook_endpoint():
    assert '/billing/webhook' in read('main.py')

def test_team_endpoint():
    assert '/team' in read('main.py')

def test_team_invite_endpoint():
    assert '/team/invite' in read('main.py')

def test_get_current_user_used_in_memories():
    assert 'get_current_user' in read('main.py')

def test_memory_namespace_used():
    assert 'memory_namespace' in read('main.py')

def test_free_plan_limit_enforced():
    assert '402' in read('main.py')

def test_require_plan_used_for_team():
    assert 'require_plan' in read('main.py')

def test_version_updated_to_0_7():
    assert '0.7.0' in read('main.py')


# ── models.py ─────────────────────────────────────────────────────────────────

def test_user_profile_model():
    assert 'UserProfile' in read('models.py')

def test_checkout_request_model():
    assert 'CheckoutRequest' in read('models.py')

def test_checkout_response_model():
    assert 'CheckoutResponse' in read('models.py')

def test_billing_portal_models():
    assert 'BillingPortalRequest' in read('models.py')

def test_team_invite_model():
    assert 'TeamInvite' in read('models.py')

def test_team_response_model():
    assert 'TeamResponse' in read('models.py')

def test_plans_response_model():
    assert 'PlansResponse' in read('models.py')


# ── Extension: service_worker.js ──────────────────────────────────────────────

def test_auth_signin_message():
    assert 'MNEMOX_AUTH_SIGNIN' in ext('background/service_worker.js')

def test_auth_signup_message():
    assert 'MNEMOX_AUTH_SIGNUP' in ext('background/service_worker.js')

def test_auth_signout_message():
    assert 'MNEMOX_AUTH_SIGNOUT' in ext('background/service_worker.js')

def test_auth_get_state_message():
    assert 'MNEMOX_AUTH_GET_STATE' in ext('background/service_worker.js')

def test_bearer_token_in_auth_headers():
    assert 'Bearer' in ext('background/service_worker.js')

def test_get_auth_headers_function():
    assert 'getAuthHeaders' in ext('background/service_worker.js')

def test_auth_token_stored():
    assert 'authToken' in ext('background/service_worker.js')

def test_version_updated_to_0_7():
    assert '0.7.0' in ext('background/service_worker.js')


# ── Extension: login.html + login.js ─────────────────────────────────────────

def test_login_form_has_email_field():
    assert 'email' in ext('popup/login.html').lower()

def test_login_form_has_password_field():
    assert 'password' in ext('popup/login.html').lower()

def test_signup_form_present():
    assert 'signup' in ext('popup/login.html').lower()

def test_login_js_sends_signin_message():
    assert 'MNEMOX_AUTH_SIGNIN' in ext('popup/login.js')

def test_login_js_sends_signup_message():
    assert 'MNEMOX_AUTH_SIGNUP' in ext('popup/login.js')

def test_login_js_redirects_on_success():
    assert 'popup.html' in ext('popup/login.js')

def test_email_confirmation_handled():
    assert 'needsConfirmation' in ext('popup/login.js')


# ── Extension: popup.js ───────────────────────────────────────────────────────

def test_popup_checks_auth_state():
    assert 'MNEMOX_AUTH_GET_STATE' in ext('popup/popup.js')

def test_popup_redirects_if_not_logged_in():
    assert 'login.html' in ext('popup/popup.js')

def test_popup_shows_plan_badge():
    assert 'plan-badge' in ext('popup/popup.js')

def test_popup_shows_signout():
    assert 'signout' in ext('popup/popup.js').lower()

def test_popup_shows_free_limit():
    assert 'limit' in ext('popup/popup.js').lower()


# ── Schema ────────────────────────────────────────────────────────────────────

def test_teams_table_in_schema():
    assert 'teams' in read('supabase_schema_step7.sql')

def test_team_members_table_in_schema():
    assert 'team_members' in read('supabase_schema_step7.sql')

def test_subscriptions_table_in_schema():
    assert 'subscriptions' in read('supabase_schema_step7.sql')

def test_stripe_customer_id_in_schema():
    assert 'stripe_customer_id' in read('supabase_schema_step7.sql')

def test_plan_check_constraint_in_schema():
    content = read('supabase_schema_step7.sql')
    assert 'free' in content and 'pro' in content and 'team' in content

def test_rls_enabled_for_teams():
    assert 'ROW LEVEL SECURITY' in read('supabase_schema_step7.sql')


# ── .env.example ─────────────────────────────────────────────────────────────

def test_stripe_secret_key_in_env():
    assert 'STRIPE_SECRET_KEY' in read('.env.example')

def test_stripe_webhook_secret_in_env():
    assert 'STRIPE_WEBHOOK_SECRET' in read('.env.example')

def test_stripe_pro_price_in_env():
    assert 'STRIPE_PRO_PRICE_ID' in read('.env.example')

def test_stripe_team_price_in_env():
    assert 'STRIPE_TEAM_PRICE_ID' in read('.env.example')

def test_jwt_secret_in_env():
    assert 'SUPABASE_JWT_SECRET' in read('.env.example')
