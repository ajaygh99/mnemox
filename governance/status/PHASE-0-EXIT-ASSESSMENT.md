# Phase 0 exit assessment

Authority: Issue #28  
Assessment baseline: `af534de86444b4071c5c55d2bc3e306dfc2f199b`  
Assessment type: documentation-only; no Phase 1 activation

## Recommendation

**DEFER Phase 0 exit.** The repository regression and Phase 0 workflow-hardening work pass, but product exit cannot be approved while severity-1 privacy/control findings, accessibility verification, public-claim corrections, live links, and first-use validation remain unresolved.

Issue #21 must remain blocked. This assessment does not authorize Phase 1, deployment, publication, risk acceptance, or production changes.

## Completed Phase 0 delivery

| Work | Pull request | Merge commit | Assessment |
| --- | --- | --- | --- |
| B-07 completion evidence | #22 | `4087e046` | Merged |
| B-09 autonomous workflow repair | #23 | `8413bdea` | Merged and independently approved |
| B-10 refusal-path tests | #26 | `4d448ac390c01f4e84fb11dea7dce53ddfbbc739` | Merged and independently approved |
| B-08 governance-only dry run | #27 | `4c31997e6c25078e1b007764a61160512e8a6d37` | Merged and independently approved |
| Performance checkpoint | #25 | `af534de86444b4071c5c55d2bc3e306dfc2f199b` | Merged and independently approved |

The performance checkpoint's reviewed branch head was `085e266199030abcfa536b6b23d8ad667d4755e0`. Rebase merge rewrote the branch commits; therefore its original exact-SHA evidence directory does not equal the final `main` merge SHA. This provenance caveat does not turn static guards into production performance measurements.

## Exit gate matrix

| Gate | Status | Evidence and boundary |
| --- | --- | --- |
| Repository functionality | PASS | Governance: 39 passed. Full suite: 463 passed, 5 known warnings. |
| Phase ordering and autonomous workflow safety | PASS | B-09, B-10, and B-08 are merged; the dry run is a deterministic repository-state simulation. |
| Performance baseline | PASS WITH BOUNDARY | Static budget guards pass. No measured browser/API latency percentiles, throughput, CPU, memory, or cache-hit evidence exists. |
| Security and privacy | FAIL | Three severity-1 findings remain: defaults-on capture/injection without onboarding consent receipt; no per-injection preview/approve/reject/edit control; prompt excerpts in diagnostics. |
| Accessibility | FAIL/BLOCKED | Static labeling and keyboard defects remain; live keyboard, focus, contrast, and screen-reader evidence is absent. |
| Public claims | FAIL | Control/privacy, diagnostic logging, Team Memory, analytics, free-forever, and 60-second claims are contradicted or unverified. |
| Live links and store state | BLOCKED | Repository-relative links were audited, but live routes and Chrome Web Store state were not validated. |
| Manual browser and production validation | PENDING | The source audit and B-08 dry run explicitly do not validate live browser, database, billing, deployment, user-data, privacy, or production behavior. |
| Five-user first-use study | PENDING | The B-05 protocol exists, but the study was not executed and no participant outcome is claimed. |
| Independent review | PARTIAL | Recent hardening and checkpoint PRs have independent approval. Historical decision-log gaps on earlier Phase 0 PRs remain documented. |

## Required remediation before approval

1. Resolve or explicitly accept each severity-1 privacy/control risk through an owner-approved contract and independent review. Codex does not accept these risks.
2. Correct or remove contradicted and unverified public claims, then validate the published surfaces.
3. Remediate accessibility defects and collect live keyboard, focus, contrast, and screen-reader evidence.
4. Validate live routes, store state, supported-browser behavior, and the relevant production boundary without exposing user data.
5. Execute the approved five-user protocol or record an owner-approved, independently reviewed change to the exit criterion.
6. Reassess every gate, obtain an independent review, and record a signed owner decision before refining or activating Phase 1.

Each remediation outcome must have its own bounded issue contract and exact-SHA evidence. Passing repository tests alone is insufficient to change the exit recommendation.

## Evidence

Exact-candidate evidence is recorded under `evidence/PHASE-0-EXIT/<candidate-sha>/`. The owner decision template is `governance/status/PHASE-0-EXIT-DECISION.md` and remains unsigned.
