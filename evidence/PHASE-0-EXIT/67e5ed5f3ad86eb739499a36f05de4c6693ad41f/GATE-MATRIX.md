# Phase 0 exit gate matrix

Assessment candidate: `67e5ed5f3ad86eb739499a36f05de4c6693ad41f`  
Baseline: `af534de86444b4071c5c55d2bc3e306dfc2f199b`  
Authority: Issue #28

| Gate | Result | Exit effect |
| --- | --- | --- |
| Governance suite | PASS — 39 passed | Satisfied |
| Full regression suite | PASS — 463 passed, 5 warnings | Satisfied |
| Workflow safety and phase order | PASS | Satisfied |
| Static performance guards | PASS WITH BOUNDARY | Satisfied only for repository budgets; no production performance claim |
| Security/privacy | FAIL | Blocks exit |
| Accessibility | FAIL/BLOCKED | Blocks exit |
| Public claims | FAIL | Blocks exit |
| Live routes/store | BLOCKED | Blocks exit |
| Manual browser/production validation | PENDING | Blocks exit |
| Five-user first-use study | PENDING | Blocks exit |
| Independent review coverage | PARTIAL | Requires owner/reviewer disposition |

Result: **DEFER Phase 0 exit and keep Phase 1 blocked.**

The detailed rationale and remediation list are in `governance/status/PHASE-0-EXIT-ASSESSMENT.md`. The owner decision is intentionally unsigned.
