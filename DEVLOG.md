# Mnemox — Developer Log

> One entry per step. Never skip writing this. It's your checkpoint record.

---

## Step 1 — Project Setup + Git Foundation
**Date:** 2026-05-29
**Status:** ✅ Complete
**Git tag:** `v0.1`

### What was built
- Chrome Extension Manifest V3 with host permissions for ChatGPT, Claude, Gemini, Copilot
- Popup UI (popup.html + popup.js) — toggle capture/inject, memory count display, site detection
- Background Service Worker — message routing, memory storage in chrome.storage.local, badge updates
- Content Script scaffold — site detection, settings load, message listener, placeholder for Step 2
- .gitignore, IDEAS.md, DEVLOG.md

### Tests passed
- [ ] Manifest validates (no errors in chrome://extensions)
- [ ] Popup loads without JS errors
- [ ] Service worker registers and logs startup message
- [ ] Content script detects correct site name on each AI tool
- [ ] Ping test: content → SW returns { status: 'ok' }

### Notes
- Icons are placeholder (Step 1 — add real PNGs before launch)
- Dashboard link in popup points to dashboard/index.html (built in Step 6)

---

## Step 2 — Chrome Extension UI + Content Script
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 3 — FastAPI Backend + Supabase Storage
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 4 — Vector Embeddings + Smart Memory Retrieval
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 5 — Auto Memory Injection into AI Prompts
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 6 — Dashboard
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 7 — Auth + Stripe + Teams
**Date:** TBD
**Status:** 🔲 Pending

---

## Step 8 — Testing + Launch
**Date:** TBD
**Status:** 🔲 Pending

## Step 7 — Supabase Auth + Stripe Billing + Team Memory (v0.7)

### What was built
- **auth.py**: JWT verification via Supabase (`decode_supabase_jwt`), `CurrentUser` dependency with `memory_namespace` (handles `team:{id}` shared vault), `require_plan()` factory for plan gating, legacy API key fallback
- **billing.py**: Stripe integration — `get_or_create_customer`, `create_checkout_session`, `create_billing_portal_session`, `handle_stripe_webhook` (subscription.created/updated/deleted → updates Supabase app_metadata)
- **config.py**: + `stripe_*` fields, `supabase_jwt_secret`
- **models.py**: + `UserProfile`, `CheckoutRequest/Response`, `BillingPortalRequest/Response`, `PlansResponse`, `TeamInvite`, `TeamResponse`
- **main.py**: All memory routes now use `get_current_user` dep. Free plan: 402 when limit (50) reached. New routes: `GET /auth/me`, `GET /billing/plans`, `POST /billing/checkout`, `POST /billing/portal`, `POST /billing/webhook`, `GET /team`, `POST /team/invite`
- **supabase_schema_step7.sql**: `teams`, `team_members`, `subscriptions` tables with RLS
- **extension/popup/login.html + login.js**: Full sign in / sign up UI, email confirmation flow, error states
- **extension/background/service_worker.js**: Auth message handlers (`MNEMOX_AUTH_SIGNIN/SIGNUP/SIGNOUT/GET_STATE`), `getAuthHeaders()` uses Bearer JWT or falls back to X-API-Key, auth state persisted in chrome.storage
- **extension/popup/popup.js + popup.html**: Auth gate on load (redirects to login.html if not signed in), plan badge (Free/Pro/Team), memory limit progress for Free, sign out button

### Plans
| Plan  | Price  | Memories | Features                    |
|-------|--------|----------|-----------------------------|
| Free  | $0     | 50       | All AI platforms            |
| Pro   | $9/mo  | ∞        | + Semantic search, priority |
| Team  | $29/mo | ∞        | + Shared vault, 10 members  |

### Tests: 84 passed ✅
### Git tag: v0.7

## Step 8 — End-to-End Testing + ProductHunt Launch (v0.8)

### What was built
- **tests/step8/test_e2e_api.py**: 48 real integration tests using FastAPI TestClient with mocked Supabase/Qdrant/OpenAI. Tests cover: health endpoint, all memory CRUD, search, billing plans, checkout, team plan gating, JWT auth edge cases (expired, wrong secret, no header), free plan 402 enforcement, team memory namespace sharing
- **landing/index.html**: Full Mnemox landing page — hero, how-it-works steps, feature grid, testimonials, pricing table (Free/Pro/Team), CTA band, footer. No build step, pure HTML/CSS
- **LAUNCH.md**: Complete launch playbook — ProductHunt tagline + description + maker comment, Chrome Web Store listing copy, Twitter thread, LinkedIn post, full pre-launch checklist, backend deployment guide, Stripe setup, target metrics table

### Tests: 48 new E2E integration tests (303 total) ✅
### Git tag: v0.8

### Total test count by step
| Step | Tests | What |
|------|-------|------|
| 1 | 16 | Extension structure, manifest |
| 2 | 22 | Content script, popup |
| 3 | 35 | FastAPI backend, Supabase |
| 4 | 39 | Vector embeddings, Qdrant |
| 5 | 30 | Memory injection, content script |
| 6 | 29 | Dashboard, settings |
| 7 | 84 | Auth, billing, team |
| 8 | 48 | E2E integration (real HTTP) |
| **Total** | **303** | **All passing ✅** |

## Step 10 — Chrome Web Store Rejection #2: Anonymous Mode (v0.1.17)

### What happened
The v0.1.16 submission was rejected: "Inaccurate Description - Non functional
- Dashboard" -- the reviewer couldn't reproduce the Dashboard feature named
in our own listing description.

### Root cause
`popup.js`'s `init()` unconditionally redirected to `login.html` whenever
`authState.isLoggedIn` was false (this exact behavior was locked in by a
tests/step9 regression guard after the *first* rejection, for a different
reason -- sign-up itself was broken then). Sign-up requires Supabase email
confirmation, which a reviewer cannot complete, so they got stuck on the
login screen and never saw the popup's "View Memories" button, let alone
the dashboard page it opens. The dashboard's own code was never the
problem -- the CSP/inline-script bug from Step 6 was already fixed. It was
simply unreachable behind a mandatory account wall.

### What was built
- **extension/popup/popup.js**: `init()` no longer returns early when
  signed out. Popup always renders in a "local mode" -- plan badge shows
  Free, user row shows "Local mode (not signed in)" with a Sign in link
  instead of Sign out. Dashboard button, capture/inject toggles all wired
  unconditionally. Sign out now re-renders the popup locally instead of
  bouncing to `login.html`.
- **extension/popup/popup.html**: added a `signin-link` control next to
  the existing `signout-btn` in the user row.
- **extension/popup/login.html + login.js**: added a "Continue without an
  account" link that returns to `popup.html` without signing in.
- **extension/manifest.json**: version bump to 0.1.17.
- No backend or service-worker changes needed -- `handleMemoryCaptured()`
  and `handleSearchMemories()` in `service_worker.js` already wrote to
  `chrome.storage.local` first and fell back to local search without a
  backend session; only the popup's UI gate was blocking access to them.

### Tests
- `tests/step9/test_auth_signup_regression.py`: rewrote the one assertion
  that had locked in the forced-redirect behavior
  (`test_popup_redirects_unauthenticated_to_login` ->
  `test_popup_does_not_force_redirect_when_unauthenticated`), added
  `test_signin_remains_available_via_explicit_link`.
- `tests/step10/test_anonymous_mode.py`: 9 new tests locking in that the
  popup never bails out early on auth state, the Dashboard/capture/search
  paths are reachable and backend-optional, and sign-in stays available
  as an opt-in link.
- Full suite: 329 extension tests + 48 backend E2E tests, all passing.

### Git tag: v0.1.17
