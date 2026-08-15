# Onboarding claim and capability matrix

Status meanings:

- `verified-source`: directly supported by tracked source/tests, not necessarily live production.
- `conditional`: implemented only for a mode, account, backend, or fallback.
- `unverified-production`: source/configuration exists but live behavior is unobserved.
- `absent`: required behavior was not found in tracked source.
- `contradicted`: claim materially exceeds or conflicts with source-observed behavior.

| Claim or user expectation | Status | Source evidence | Required next evidence/action |
|---|---|---|---|
| Configured adapters exist for ChatGPT, Claude, Gemini, Copilot | `verified-source` / `unverified-production` | Manifest host/content-script declarations and site adapters | Public copy now states the configuration boundary; real-Chrome smoke is still required for current live compatibility |
| Account is optional | `verified-source` | Popup local-mode path and Continue without an account | Real fresh-install confirmation |
| Capture requires informed consent and remains off until enabled | `verified-source` | `service_worker.js`, `popup.js`, and privacy regression tests require a versioned consent receipt and false defaults | Public copy corrected; publication remains separately approval-gated |
| Injection is controllable per proposed context | `verified-source` / `unverified-production` | `content.js` preview offers edit, approve, send without memories, and return before prompt mutation; privacy/accessibility tests cover the gate | Manual browser validation exists for the reviewed build; revalidate each published build |
| “Mnemox silently captures context” | `contradicted` | Capture now requires informed consent and explicit enablement | Removed from active public copy |
| Relevant memories are proposed for reviewed injection | `verified-source` / `unverified-production` | Content script searches within a budget, then presents a preview before mutation | Public copy corrected; live supported-site behavior remains build-specific |
| Local mode works without sign-in | `verified-source` | Local storage and local search fallback paths | Browser/offline evidence |
| User knows local versus cloud state | `absent` | Popup says local mode only when signed out; memory-level state absent | Onboarding and per-memory disclosure design |
| Semantic search | `conditional` | Remote authenticated backend path; local fallback is keyword search | UI mode disclosure and degraded-state tests |
| Consent and reviewed-injection controls | `verified-source` / `unverified-production` | Phase 0 Severity-1 remediation added fail-closed consent, preview/edit/approve/reject, and redacted diagnostics | Public copy uses the specific controls rather than an absolute privacy promise; production review remains required |
| Prompt/response content is not logged diagnostically | `verified-source` | Privacy regression tests prohibit prompt content/excerpts; content script diagnostics report only non-content state/counts | Revalidate each published build |
| Delete anytime | `conditional` | Individual and clear-all deletion exist; clear all is irreversible; account deletion is email-based | Deletion receipt/recovery and production verification |
| Team Memory is available | `absent` | Backend-related source presence does not prove complete UX/isolation | Public copy marks it not currently available; Phase 7 evidence is required before an availability claim |
| Memory analytics is available | `absent` | No proven user analytics experience | Removed from active plan benefits |
| Free forever | `contradicted` | Tracked configuration defines a 50-memory free limit alongside paid-plan configuration, but cannot establish perpetual pricing | Replaced with current, non-perpetual access wording |
| Works in 60 seconds | `unverified-production` | Five-user study was not executed and no measured time-to-value evidence exists | Removed from public copy; do not restore without approved measured evidence |
| Website privacy text consistently identifies support contact | `contradicted` | General support uses `hello@mnemoxpro.com`; retention section uses personal Gmail | Approved copy/privacy-policy correction |
| Public privacy text fully matches actual data flow | `unverified-production` | Source describes Supabase/Qdrant/OpenAI but live configuration and retention unverified | Data-flow review and owner-approved publication |
| Safe sample-memory onboarding | `absent` | No sample workflow found | Phase 1 design after Phase 0 exit |
| Injection preview with source/reason/scope | `absent` | No preview surface found | Phase 1 design/implementation issue |
| Edit/reject/forget/pause/undo before injection | `absent` | Only global toggles and dashboard delete found | Phase 1 control issue |

This matrix is not publication approval. Any public claim must link to exact production evidence or be marked unavailable/Coming soon through an owner-approved change.
