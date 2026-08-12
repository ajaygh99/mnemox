# Onboarding claim and capability matrix

Status meanings:

- `verified-source`: directly supported by tracked source/tests, not necessarily live production.
- `conditional`: implemented only for a mode, account, backend, or fallback.
- `unverified-production`: source/configuration exists but live behavior is unobserved.
- `absent`: required behavior was not found in tracked source.
- `contradicted`: claim materially exceeds or conflicts with source-observed behavior.

| Claim or user expectation | Status | Source evidence | Required next evidence/action |
|---|---|---|---|
| Works on ChatGPT, Claude, Gemini, Copilot | `verified-source` / `unverified-production` | Manifest host/content-script declarations and site adapters | Real-Chrome synthetic smoke on every current site/build |
| Account is optional | `verified-source` | Popup local-mode path and Continue without an account | Real fresh-install confirmation |
| Capture is controllable | `conditional` | Capture toggle exists, but defaults on without onboarding consent | Design/validate informed first-run choice |
| Injection is controllable | `contradicted` | Global toggle exists; exact pre-injection approve/reject/edit control is absent | Phase 1 preview/control issue |
| Mnemox silently captures context | `verified-source` but trust-damaging | Capture defaults on; website uses the phrase | Approved copy/behavior fix; do not publish from this audit |
| Relevant memories are automatically injected | `verified-source` / `unverified-production` | Content script formats and prepends results within a budget | Browser proof plus preview/control design |
| Local mode works without sign-in | `verified-source` | Local storage and local search fallback paths | Browser/offline evidence |
| User knows local versus cloud state | `absent` | Popup says local mode only when signed out; memory-level state absent | Onboarding and per-memory disclosure design |
| Semantic search | `conditional` | Remote authenticated backend path; local fallback is keyword search | UI mode disclosure and degraded-state tests |
| Privacy first / data under user control | `contradicted` | Delete/toggles exist, but defaults-on capture/injection, no preview/undo, prompt excerpts logged | Trust-fix backlog and privacy review |
| Prompt/response content is not logged diagnostically | `contradicted` | Content script logs stored/prompt excerpts and capture previews | Redacted diagnostics issue |
| Delete anytime | `conditional` | Individual and clear-all deletion exist; clear all is irreversible; account deletion is email-based | Deletion receipt/recovery and production verification |
| Team Memory is available | `unverified-production` | Website claims it; backend-related source presence does not prove complete UX/isolation | Mark unavailable/Coming soon until Phase 7 evidence |
| Memory analytics is available | `unverified-production` | Website pricing claim; no proven user analytics experience | Remove/Coming soon pending evidence and approval |
| Free forever | `contradicted` | Website/config claim alongside paid plans and limits | Approved commercial-copy decision |
| Works in 60 seconds | `unverified-production` | Website claim; five-user study not executed | B-05 approved execution and measured evidence |
| Website privacy text consistently identifies support contact | `contradicted` | General support uses `hello@mnemoxpro.com`; retention section uses personal Gmail | Approved copy/privacy-policy correction |
| Public privacy text fully matches actual data flow | `unverified-production` | Source describes Supabase/Qdrant/OpenAI but live configuration and retention unverified | Data-flow review and owner-approved publication |
| Safe sample-memory onboarding | `absent` | No sample workflow found | Phase 1 design after Phase 0 exit |
| Injection preview with source/reason/scope | `absent` | No preview surface found | Phase 1 design/implementation issue |
| Edit/reject/forget/pause/undo before injection | `absent` | Only global toggles and dashboard delete found | Phase 1 control issue |

This matrix is not publication approval. Any public claim must link to exact production evidence or be marked unavailable/Coming soon through an owner-approved change.
