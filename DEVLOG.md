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
