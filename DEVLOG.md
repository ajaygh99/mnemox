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
