# Corrected claim matrix

Candidate implementation: `c2d8b446f5c4933b059770a189898c488ad0e22c`

| Old claim category | Corrected factual wording | Tracked source evidence | Production limitation |
|---|---|---|---|
| “Free forever” | Local unsigned use is currently available at no charge with a tracked 50-memory limit; pricing and availability may change | `product.config.json`; `extension/popup/popup.js`; `backend/billing.py` | Configuration does not prove perpetual commercial terms |
| “Works in 60 seconds/under a minute” | Install and review the controls; no duration is promised | Five-user study remains unexecuted in the onboarding audit | No measured production time-to-value evidence |
| Team Memory available | Team Memory is not currently available | Backend-related source is not a complete verified team UX/isolation path | Availability requires later approved evidence |
| Memory analytics available | Removed from active benefits | No proven analytics user experience in the claim matrix | Must not be restored without approved production evidence |
| Silent capture | Capture remains off until informed consent is recorded and capture is enabled | `extension/background/service_worker.js`; `extension/popup/popup.js`; `tests/privacy/test_severity1_remediation.py` | Repository/source evidence is not publication approval |
| Automatic injection / user controls every shared item | Injection remains off until consent and enablement; each proposal can be edited, approved, rejected, or returned from before mutation | `extension/content/content.js`; privacy and accessibility regression tests | Supported-site behavior must be revalidated for the published build |
| Nothing leaves the browser / account-only storage | Unsigned use stores locally; optional account, cloud-sync, and backend semantic-search paths can send memory content beyond the browser | `extension/background/service_worker.js`; `extension/popup/popup.js`; anonymous-mode tests | Live backend configuration and retention remain unverified |
| Semantic search for all users | Signed-in backend search can use vector embeddings; local unsigned use falls back to keyword matching | `extension/background/service_worker.js`; `tests/step5/test_injection.py`; anonymous-mode tests | Backend semantic search requires a connected/authenticated path |
| Guaranteed support across named sites | Configured adapters exist for the named sites; live compatibility must be verified against the current build | Extension manifest and content-script site adapters | Third-party sites can change independently |
| Absolute training, isolation, sharing, retention, and deletion promises | Active copy describes only the specific consent, review, local-storage, connected-path, and memory-deletion controls | Severity-1 remediation source/tests and existing Privacy Policy | Legal/policy consistency requires separate owner/legal review |

