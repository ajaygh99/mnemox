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
    # 2026-07-09: dashboard JS moved out of an inline <script> block (blocked
    # entirely by MV3's default CSP -- see tests/step6 for the full story)
    # into an external dashboard.js. Concatenate both so existing assertions
    # about dashboard behavior don't care which file a string lives in.
    with open(os.path.join(EXT, 'dashboard', 'index.html')) as f:
        html = f.read()
    with open(os.path.join(EXT, 'dashboard', 'dashboard.js')) as f:
        js = f.read()
    return html + '\n' + js


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


# -- Regression: dashboard must not use inline scripts (CSP-blocked) ----------
# 2026-07-09: Chrome's extension error console showed the true root cause of
# the "dashboard always shows 0 memories" bug: MV3's default CSP for
# extension pages is "script-src 'self'", which blocks ALL inline script
# execution -- both inline <script>...</script> blocks and inline
# onclick=/onchange=/oninput= attributes (including ones injected via
# innerHTML, like the old expandMemory()/deleteMemory() buttons). The
# dashboard's entire script -- loadData(), the onChanged listener, the
# version display -- silently never ran, on every single page load, the
# whole time. This had nothing to do with live-refresh or duplicate
# extension copies; both of those were red herrings chased before the real
# error surfaced in chrome://extensions -> Errors. Fixed by moving all JS to
# an external dashboard.js (allowed under 'self') and wiring every control
# with addEventListener / event delegation instead of inline handlers.

def test_dashboard_html_has_no_inline_script_block():
    with open(os.path.join(EXT, 'dashboard', 'index.html')) as f:
        html = f.read()
    assert '<script>' not in html, \
        "inline <script> blocks are silently blocked by MV3's default CSP"


def test_dashboard_html_loads_external_script():
    with open(os.path.join(EXT, 'dashboard', 'index.html')) as f:
        html = f.read()
    assert '<script src="dashboard.js">' in html


def test_dashboard_html_has_no_inline_event_handlers():
    with open(os.path.join(EXT, 'dashboard', 'index.html')) as f:
        html = f.read()
    for attr in ('onclick=', 'onchange=', 'oninput=', 'onsubmit='):
        assert attr not in html, \
            attr + ' is an inline script and is silently blocked by MV3 CSP'


def test_dashboard_js_file_exists():
    assert os.path.exists(os.path.join(EXT, 'dashboard', 'dashboard.js'))


def test_dashboard_js_generated_cards_use_data_attributes_not_onclick():
    with open(os.path.join(EXT, 'dashboard', 'dashboard.js')) as f:
        js = f.read()
    # memoryCard() builds HTML via innerHTML -- inline onclick= there is
    # JUST as CSP-blocked as a static onclick= in the HTML file itself.
    fn_match = re.search(r"function memoryCard[\s\S]*?\n}", js)
    assert fn_match, "memoryCard() not found"
    assert 'onclick=' not in fn_match.group(0)
    assert 'data-action=' in fn_match.group(0)


def test_dashboard_js_wires_events_programmatically():
    with open(os.path.join(EXT, 'dashboard', 'dashboard.js')) as f:
        js = f.read()
    assert 'addEventListener' in js
    assert 'function wireUpEvents' in js


# -- Regression: Enter-key capture must use a pre-mutation text snapshot ------
# 2026-07-09 manual test: sent a message on claude.ai with the default
# settings (captureEnabled + injectEnabled both on) and it never showed up
# in the dashboard, despite chatgpt/gemini captures working. Root cause:
# the Enter-key handler's capture step re-read the prompt box's LIVE DOM 80ms
# later (config.getPromptText(promptEl)) instead of using the 'text' snapshot
# already captured synchronously the moment Enter was pressed. Claude's
# ProseMirror editor can clear/mutate its content well before that 80ms
# timeout fires (from our own injection rewriting the box, or from Claude's
# own send handling), so the delayed re-read intermittently read an empty
# string and capturePrompt() silently discarded it (content.js aborts on
# text.length < 4). The sibling non-inject branch already used the correct
# snapshot -- only the inject branch (captureEnabled+injectEnabled together,
# which is the DEFAULT config) had the bug, so it hit every user by default.

def content_js():
    with open(os.path.join(EXT, 'content', 'content.js')) as f:
        return f.read()


def test_keydown_capture_uses_text_snapshot_not_live_dom_read():
    body = content_js()
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", body)
    assert fn_match, "attachPromptListeners() not found"
    fn_body = fn_match.group(0)
    # The bug pattern: re-reading the DOM inside the delayed capture call.
    assert 'capturePrompt(config.getPromptText(promptEl))' not in fn_body, \
        "capture must not re-read the live DOM after a delay -- use the " \
        "'text' snapshot captured synchronously at keydown time instead"
    # Step 1 (unconditional, before the inject/no-inject branch) must use
    # the snapshot.
    step1 = fn_body[:fn_body.find('if (settings.injectEnabled)')]
    assert 'capturePrompt(text)' in step1


def test_submit_button_click_skips_own_synthetic_click():
    body = content_js()
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", body)
    assert fn_match
    fn_body = fn_match.group(0)
    assert 'mnemoxOwnClick' in fn_body, \
        "programmatic post-injection click should be flagged so the " \
        "submit-button listener doesn't redundantly re-capture"


# -- Regression: popup memory count must live-refresh too ---------------------
# 2026-07-09: while investigating the Claude capture race, a popup pinned
# open via right-click -> Inspect kept showing "0 memories saved" even after
# a new message was sent and (per the fixed content.js) actually captured.
# Root cause: popup.js has no chrome.storage.onChanged listener, so a
# popup that stays open (normally popups auto-close on blur, but Inspect
# pins them open, and users may also just glance back at an already-open
# popup) never picks up storage changes after its one-time init() read.
# This is the exact same class of bug as the dashboard's earlier stale-data
# issue -- fixed the same way.

def test_popup_has_storage_onchanged_listener():
    assert 'chrome.storage.onChanged.addListener' in popup_js()


def test_popup_onchanged_watches_memory_count():
    body = popup_js()
    idx = body.find('chrome.storage.onChanged.addListener')
    assert idx != -1
    assert 'changes.memoryCount' in body[idx:idx + 300]


def test_popup_render_memory_stats_function_exists():
    assert 'function renderMemoryStats' in popup_js()


def test_popup_init_uses_render_memory_stats():
    body = popup_js()
    fn_match = re.search(r"async function init\(\)[\s\S]*?\n}", body)
    assert fn_match, "init() not found"
    assert 'renderMemoryStats(' in fn_match.group(0)


# -- Diagnostics: capture path must be observable end to end -------------------
# 2026-07-09: after fixing the known Claude capture race (v0.1.8) and the
# stale-popup issue (v0.1.9), a fresh manual test still showed 0 memories
# captured on Claude, with no visible signal anywhere as to why. Rather than
# guess again, added console logging at every point capturePrompt() can
# silently bail (captureEnabled false, text too short after trim/strip,
# duplicate of lastCaptured, sendMessage failure) plus confirmation logging
# in the service worker's handleMemoryCaptured() (received + storage write
# confirmed). These are cheap (only run on Enter/submit) and turn the next
# manual test into an actual diagnosis.

def test_capture_logs_when_capture_disabled():
    fn_match = re.search(r"function capturePrompt[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert "console.log('[Mnemox] Capture skipped: captureEnabled is false'" in fn_match.group(0)


def test_capture_logs_when_text_too_short():
    fn_match = re.search(r"function capturePrompt[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'text too short after trim/strip' in fn_match.group(0)


def test_capture_logs_before_sending_to_service_worker():
    fn_match = re.search(r"function capturePrompt[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'Sending capture to service worker' in fn_match.group(0)


def test_capture_logs_sendmessage_failure():
    fn_match = re.search(r"function capturePrompt[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'chrome.runtime.lastError' in fn_match.group(0)


def test_service_worker_logs_receipt_and_storage_write():
    body = sw()
    fn_match = re.search(r"async function handleMemoryCaptured[\s\S]*?\n\}", body)
    assert fn_match
    fn_body = fn_match.group(0)
    assert 'handleMemoryCaptured received' in fn_body
    assert 'Storage write confirmed' in fn_body


# -- Regression: onInstalled must never wipe existing data --------------------
# 2026-07-09: the SERVICE WORKER console (chrome://extensions -> Mnemox ->
# "service worker" -> Inspect) showed "[Mnemox v0.7.0] Installed" firing on
# what the user believed was just a routine extension reload. That log line
# only prints inside the reason === 'install' branch of onInstalled, which
# unconditionally called chrome.storage.local.set() with empty defaults --
# memories: [], memoryCount: 0, auth cleared. THIS was the real root cause
# behind every "0 memories" reset seen throughout this whole debugging
# session, on every AI site (ChatGPT, Gemini, Claude) -- not a per-site
# capture bug at all. Fixed by only filling in keys that don't already
# exist in storage, so a genuine 'install' firing (whether from Chrome
# dev-mode reload quirks or an actual remove+reload) can no longer destroy
# real data.

def test_oninstalled_does_not_call_storage_set_unconditionally():
    body = sw()
    fn_match = re.search(r"chrome\.runtime\.onInstalled\.addListener\([\s\S]*?\n\}\);", body)
    assert fn_match, "onInstalled listener not found"
    fn_body = fn_match.group(0)
    # The old destructive pattern: an unconditional .set({...defaults...})
    # as the only thing gating on reason === 'install'.
    assert 'chrome.storage.local.get(' in fn_body, \
        "onInstalled must read existing storage before writing any defaults"


def test_oninstalled_only_fills_missing_keys():
    body = sw()
    fn_match = re.search(r"chrome\.runtime\.onInstalled\.addListener\([\s\S]*?\n\}\);", body)
    assert fn_match
    fn_body = fn_match.group(0)
    assert 'if (!(key in existing))' in fn_body


def test_oninstalled_preserves_memories_key():
    body = sw()
    fn_match = re.search(r"chrome\.runtime\.onInstalled\.addListener\([\s\S]*?\n\}\);", body)
    assert fn_match
    fn_body = fn_match.group(0)
    # memories must appear inside the defaults object (as a fallback for a
    # TRULY fresh install), but never get force-written over existing data.
    assert "memories: []" in fn_body
    assert re.search(r"chrome\.storage\.local\.set\(\s*\{\s*\n?\s*captureEnabled", fn_body) is None, \
        "must not unconditionally overwrite storage with defaults anymore"


# -- Diagnostics: log the Enter keydown itself, not just capturePrompt() ------
# 2026-07-09: after the onInstalled fix, the service worker console showed
# ChatGPT and Gemini captures persisting correctly (0 -> 1 -> 2, no resets),
# but ZERO Claude captures ever arrived despite active chatting -- and none
# of the existing capturePrompt() diagnostic logs fired either. That means
# execution was dying between the Enter keydown and the capturePrompt() call,
# most likely at the pre-existing 'if (!text || text.length < 3) return'
# early-return, which had no logging at all. Added logging right at Enter
# keydown (before that check) and on submit-button clicks, so the exact
# failure point becomes visible on the next test.

def test_keydown_logs_on_every_enter_press():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    fn_body = fn_match.group(0)
    assert "console.log('[Mnemox] Enter pressed on '" in fn_body


def test_keydown_logs_when_bailing_on_short_text():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'Enter handler bailed: text too short' in fn_match.group(0)


def test_submit_button_click_is_logged():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'Submit button clicked on' in fn_match.group(0)


def test_warns_when_no_submit_button_matched():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'No submit button matched on' in fn_match.group(0)


# -- Regression: MNEMOX_VERSION must not be a second, unsynced version -------
# 2026-07-09: user noticed the service worker console showed "Mnemox v0.7.0"
# while the popup/dashboard footers correctly showed the real manifest
# version (0.1.11 at the time). MNEMOX_VERSION was a separately hardcoded
# constant nobody kept in sync -- a second, confusing version number on top
# of the earlier extension-ID mixup. Now reads the real manifest version.

def test_mnemox_version_reads_from_manifest_not_hardcoded():
    body = sw()
    match = re.search(r"const\s+MNEMOX_VERSION\s*=\s*(.+);", body)
    assert match, "MNEMOX_VERSION constant not found"
    value = match.group(1).strip()
    assert value == "chrome.runtime.getManifest().version", \
        "MNEMOX_VERSION must read the real manifest version, not a separate hardcoded string"


# -- Regression: Claude selectors must be resilient, not exact-case-only -----
# 2026-07-09 manual test (with the diagnostic logging above): confirmed both
# failures directly in the console --
#   "[Mnemox] Enter pressed on claude. Text length: 0"
#   "[Mnemox] No submit button matched on claude for selector:
#    button[aria-label=\"Send Message\"], button[type=\"submit\"]"
# CSS attribute selectors are case-sensitive by default -- Claude's actual
# current aria-label almost certainly no longer matches the hardcoded
# "Send Message" (capital M) exactly. Broadened to case-insensitive
# matching (the "i" flag) plus additional fallback patterns, and added a
# getPromptText() fallback chain (textContent, then a nested child) in case
# .innerText alone reads empty on Claude's current DOM structure.

def test_claude_submit_selector_is_case_insensitive():
    body = content_js()
    claude_match = re.search(r"claude:\s*\{[\s\S]*?\n    \},", body)
    assert claude_match, "claude site config not found"
    cfg = claude_match.group(0)
    assert 'submitSelector:' in cfg
    # case-insensitive attribute selector flag
    assert ' i]' in cfg or '" i,' in cfg or '"i"' in cfg or 'i\'' in cfg or re.search(r'"\s*i\s*\]', cfg), \
        "submitSelector should use case-insensitive ('i' flag) attribute matching"


def test_claude_submit_selector_has_fallback_patterns():
    body = content_js()
    claude_match = re.search(r"claude:\s*\{[\s\S]*?\n    \},", body)
    assert claude_match
    cfg = claude_match.group(0)
    assert 'data-testid' in cfg, "should fall back to data-testid, not just aria-label"


def test_claude_get_prompt_text_has_fallback_chain():
    body = content_js()
    claude_match = re.search(r"claude:\s*\{[\s\S]*?\n    \},", body)
    assert claude_match
    cfg = claude_match.group(0)
    assert 'textContent' in cfg, "getPromptText should fall back beyond just innerText"


def test_no_submit_button_dumps_candidates():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'Candidate buttons on page' in fn_match.group(0)


# 2026-07-09 note: the old "dump promptEl.outerHTML on empty-text capture
# failure" diagnostic (added in v0.1.13) was removed in v0.1.15 -- the
# input-tracking fix below (lastKnownText) resolves the empty-read case via
# fallback instead of just logging it, so that dump's bail-out path is no
# longer reachable in the same way and the diagnostic was retired along with
# the dead code it was inspecting.


# -- Diagnostics: verify promptEl is actually the focused element -------------
# 2026-07-09: v0.1.13's broadened Claude selectors did NOT fix the empty-text
# symptom -- identical "Text length: 0" on every Enter press, before and
# after. That rules out simple selector-wording drift and points at a
# structural issue: our capture-phase keydown listener fires for any Enter
# press that passes through promptEl on its way down to the real event
# target, which includes promptEl being an ANCESTOR of the real input, not
# necessarily the input itself. Added a definitive runtime check comparing
# promptEl against document.activeElement at the moment of the Enter press,
# plus an unconditional dump of the wired element's identity at wire-time.

def test_wire_time_dumps_matched_element():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'Matched element:' in fn_match.group(0)


# -- Real fix: continuous input-event text tracking (v0.1.15) -----------------
# 2026-07-09: the activeElement diagnostic above CONFIRMED the true root
# cause -- promptEl===document.activeElement was false and activeElement was
# <body> at the exact moment our Enter keydown listener ran, with text
# already empty, even though promptEl was independently confirmed to be the
# correct Claude input element. This is a same-element listener ORDERING
# race: Claude's own React onKeyDown handler is attached to the same
# contenteditable node and clears/blurs it synchronously before our listener
# runs, since same-element same-phase listeners fire in attachment order.
# Capture phase doesn't help when both listeners share one element.
#
# Fix: stop reading the DOM at Enter time. Track text continuously via an
# 'input' event listener (fires on every keystroke, well before Enter), and
# fall back to that snapshot whenever the live read at Enter time comes back
# empty/too short -- which is exactly what happens on Claude.

def test_input_listener_tracks_last_known_text():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    fn_body = fn_match.group(0)
    assert 'lastKnownText' in fn_body
    assert re.search(r"addEventListener\(\s*['\"]input['\"]", fn_body)


def test_enter_handler_falls_back_to_last_known_text():
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    fn_body = fn_match.group(0)
    # Keydown handler must prefer a fresh live read but fall back to the
    # input-tracked snapshot instead of bailing out immediately.
    keydown_match = re.search(r"addEventListener\(\s*['\"]keydown['\"][\s\S]*?\n      \}", fn_body)
    assert keydown_match
    keydown_body = keydown_match.group(0)
    assert 'liveText' in keydown_body
    assert 'lastKnownText' in keydown_body


def test_enter_handler_no_longer_bails_on_first_empty_read():
    # The old behavior returned immediately on an empty live read with no
    # fallback -- that's the exact bug that broke Claude capture. Assert the
    # bail-out message now reflects that a fallback was already attempted.
    fn_match = re.search(r"function attachPromptListeners[\s\S]*?\n  \}", content_js())
    assert fn_match
    assert 'even after lastKnownText fallback' in fn_match.group(0)
