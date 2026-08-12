# Onboarding blocker and friction register

Severity follows the B-05 rubric. These are source-audit findings; final severity may increase after approved browser/user evidence.

| ID | Severity | Finding and source evidence | User impact | Recommended next issue | Approval boundary |
|---|---:|---|---|---|---|
| ONB-001 | 1 | Capture and injection default true without an onboarding consent receipt (`service_worker.js:49-56`, popup defaults) | Content may be captured/inserted before the user understands scope or control | Informed first-run choices and migration-safe defaults | Privacy behavior, store release, deployment |
| ONB-002 | 1 | No pre-injection preview/approve/reject/edit surface (`content.js:167-235`) | User cannot inspect or stop a specific memory before sharing it with an AI tool | Injection preview/control design and implementation | Product behavior, privacy, release |
| ONB-003 | 1 | Prompt excerpts are emitted to console/toasts (`content.js:292-315`) | Sensitive text may appear in diagnostics or shoulder-visible UI | Redacted diagnostic and capture-confirmation policy | Privacy behavior and release |
| ONB-004 | 2 | No guided onboarding, safe sample, or persisted checklist found | New user cannot learn the value/control model predictably | Supported-site three-step onboarding design | Phase 1 activation issue |
| ONB-005 | 2 | Local/cloud state is not explained per memory; backend URL is preconfigured | Users cannot predict where content travels or which search mode applies | Local/cloud and search-mode disclosure | Privacy/data-flow review |
| ONB-006 | 2 | Website says user decides what is shared, but only a global injection toggle exists | Public trust claim overstates available control | Claim correction plus preview roadmap | Website/store publication approval |
| ONB-007 | 2 | Team, analytics, 60-second value, and free-forever claims lack production evidence | Users may make installation/payment decisions from unsupported claims | Claim/copy issue using capability matrix | Pricing/publication approval |
| ONB-008 | 2 | Clear-all is permanent and has no undo/backup (`dashboard.js:238-241`) | Accidental deletion is unrecoverable | Reversible deletion/receipt design | Data lifecycle approval |
| ONB-009 | 2 | Popup checkboxes lack accessible names and login labels are not associated | Keyboard/screen-reader users may not understand controls | Accessibility remediation with real-browser AT tests | Product UI issue |
| ONB-010 | 3 | Clickable sign-in/up navigation spans lack native keyboard semantics | Some authentication navigation may be inaccessible | Convert to semantic buttons/links | Product UI issue |
| ONB-011 | 3 | Unsupported-site badge has no clear next action | User may interpret inactivity as failure | Supported-site guidance design | Phase 1 onboarding issue |
| ONB-012 | 3 | Search can be semantic remotely or keyword locally without clear mode labeling | User may misunderstand result quality and network use | Search-mode indicator and degraded-state tests | Product/privacy behavior |
| ONB-013 | 3 | Privacy/support contact is inconsistent in website source | User may not know the correct deletion/support channel | Approved support-contact/privacy text update | Privacy-policy publication approval |
| ONB-014 | 3 | Dynamic status/toast/error regions lack proven screen-reader announcement | Success/failure may be invisible to assistive technology | Live-region/focus design and AT verification | Product UI issue |
| ONB-015 | 4 | Repository screenshots/store state are not bound to current exact SHA | Reviewers cannot reproduce public presentation | Content-free screenshot evidence pack | Store/publication approval |

## Prioritization rule

Resolve or explicitly accept all severity-1 findings before Phase 0 exit. Severity-2 findings require owner triage and issue-ready disposition. Do not convert these findings directly into product code without one complete `agent-ready` issue per outcome.
