# Mnemox onboarding and first-use trust audit

Date: 2026-08-12

Status: source audit only. Live Chrome, Chrome Web Store, production services, screenshots, keyboard operation, screen readers, and visual contrast were not observed in this task.

## Scope and method

This audit covers the tracked Universal Memory extension, website source, configuration, and automated tests at baseline `8eb34ca8bf97db576a0dc5447cb9c6c97b7dfae4`. It does not inspect the separate Prompt Coach checkout or stale Mnemox checkout.

Reproduce the automated audit-contract check with:

```powershell
$env:PYTHONUTF8 = "1"
python -m pytest tests/governance/test_onboarding_audit_contract.py -q
```

Run the supported full regression suite with `python -m pytest -q` in the same configured environment. Static source evidence proves configuration and implemented branches, not live store contents or end-to-end browser behavior.

## First-use surfaces

| Surface | Entry point | Source evidence | Source-observed state | Live evidence |
|---|---|---|---|---|
| Installation/startup | Chrome install/update event | `extension/background/service_worker.js:35-70` | Missing defaults are written; capture/injection default on; local memories are preserved | Blocked |
| Browser popup | Toolbar action | `extension/manifest.json`; `extension/popup/popup.html`; `popup.js` | Site badge, memory count, local/sign-in state, capture/inject toggles, dashboard link | Blocked |
| Optional authentication | Explicit Sign in action | `extension/popup/login.html`; `login.js`; `popup.js:85-188` | Sign-in/up plus continue-without-account; account not required for local mode | Blocked |
| Supported AI page | Manifest content scripts | `extension/manifest.json`; `extension/content/content.js` | ChatGPT, Claude, Gemini, Copilot adapters; capture/injection intercept submit behavior | Blocked |
| Capture feedback | Supported AI page after capture | `extension/content/content.js:270-317` | Toast includes a prompt preview; console diagnostics include prompt excerpts | Blocked |
| Injection | Supported AI page before submit | `extension/content/content.js:167-235` | Memories are formatted and prepended automatically when enabled; no decision preview | Blocked |
| Memory dashboard | Popup View Memories | `extension/dashboard/index.html`; `dashboard.js` | View, search, expand, delete, clear all, settings, backend connection | Blocked |
| Marketing/privacy | Website routes | `website/index.html`; `website/vercel.json` | Claims, pricing, support/privacy disclosures, store links | Blocked |

There is no dedicated onboarding document/page, persisted onboarding state, removable sample-memory flow, or step checklist in tracked extension source.

## Permission and supported-site audit

Manifest version 3 requests:

- `storage`: source uses it for settings, local memories, counts, authentication state, backend URL, and API-key field.
- `activeTab`: source states it is used for active-site detection.
- host access for `chat.openai.com`, `chatgpt.com`, `claude.ai`, `gemini.google.com`, and `copilot.microsoft.com`.

The website privacy source explains these permissions at `website/index.html:519-523`, but the extension has no first-run permission explanation before capture/injection defaults become active. Live Chrome permission prompts and store disclosure alignment remain blocked.

## Data-state and consent audit

- Local mode is implemented and the popup labels a signed-out state as local mode.
- The default backend URL points to a Railway endpoint even in stored defaults.
- Local capture is attempted first; authenticated remote sync/search paths are conditional on account/backend state.
- The popup does not explain whether a particular memory is local, remote, or both.
- Capture and injection are enabled by default on install, without a recorded onboarding consent state.
- The privacy source says prompt text is captured and can be sent to Supabase, Qdrant, and OpenAI embeddings in applicable modes; no in-extension first-use summary explains that data flow.
- Authentication tokens and user details are stored locally when signed in; the dashboard exposes an API Secret Key input. This audit does not inspect values.

## Control and recovery audit

| Control | Source result | Evidence gap |
|---|---|---|
| Toggle capture | Present in popup/dashboard | Defaults on; no first-run consent receipt |
| Toggle injection | Present in popup/dashboard | Defaults on; no per-injection decision |
| View memories | Present | Proven only statically |
| Delete one memory | Present in dashboard | Uses memory ID internally; no undo or deletion receipt |
| Clear all memories | Confirmation exists | Explicitly permanent; no recovery/backup |
| Preview before injection | Absent | Injected content is written before send without a user decision surface |
| Approve/reject/edit selected memory | Absent | No source implementation found |
| Forget/supersede semantics | Absent | Delete is not an explained lifecycle model |
| Pause with clear scope | Partial | Capture and injection toggles are separate; no unified pause/status |
| Undo injection/removal | Absent | No recovery path found |
| Unsupported-site guidance | Partial | Site badge detects state; no evidence-backed guided next step |
| Redacted diagnostics | Absent | Console logging includes prompt excerpts and internal status |

## Accessibility audit

Static evidence only:

| Check | Result | Evidence |
|---|---|---|
| Document language | Pass | Popup/login/dashboard use `lang="en"` |
| Native buttons/inputs | Partial | Many controls are native, but some navigation uses clickable spans |
| Form label association | Fail | Login labels lack `for`; toggle text is not programmatically tied to hidden checkboxes |
| Toggle accessible names | Fail | Checkbox inputs have no `aria-label`, `aria-labelledby`, or associated textual label |
| Keyboard reachability | Fail/partial | Hidden checkbox dimensions are zero; clickable spans lack native keyboard semantics |
| Focus indication | Partial | Text inputs define focus borders; comprehensive visible focus not defined for all controls |
| Dynamic status announcement | Blocked | No live-region evidence for errors, counts, toasts, or connection status |
| Screen reader operation | Blocked | No executed assistive-technology evidence |
| Color contrast | Blocked | No measured contrast evidence |
| Focus order/return | Blocked | No live keyboard/browser evidence |

## Screenshot and listing evidence gaps

Repository image assets do not prove the current Chrome Web Store screenshots or live listing. The Phase 0 evidence pack still needs owner-approved, content-free captures for:

1. first popup open showing local/cloud state and defaults;
2. supported-site versus unsupported-site state;
3. capture disclosure and confirmation using synthetic content;
4. injection behavior, including the current absence of preview/control;
5. dashboard view/search/delete and clear-all confirmation;
6. optional sign-in and continue-without-account;
7. permission explanations mapped to manifest permissions; and
8. keyboard focus and zoom/reflow evidence.

Screenshots must use synthetic data and be bound to the exact build SHA. Store publication is not authorized.

## Exit assessment

The static audit does not satisfy the Phase 0 exit. Severity-1/2 findings require refinement and approved implementation evidence; live-browser, accessibility, route, store, and five-user evidence remain blocked. See `FRICTION-REGISTER.md` and `CLAIM-CAPABILITY-MATRIX.md`.
