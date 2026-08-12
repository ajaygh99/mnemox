# B-06 exact-candidate validation

Issue: `ajaygh99/mnemox#12`

Validated implementation: `bccfc707cf39e64d090e3aeb45b0fd6c1dc50e4b`

Baseline: `origin/main` at `8eb34ca8bf97db576a0dc5447cb9c6c97b7dfae4`

## Outcome and scope

- Inventoried first-use surfaces, permissions, supported sites, data states, controls, recovery, accessibility, screenshots, and listing evidence gaps.
- Added a claim/capability matrix with explicit source/production evidence states.
- Added 15 severity-ranked onboarding findings with impact, next-issue direction, and approval boundaries.
- Added eight automated audit-contract checks.
- Did not change extension, backend, website, store copy, permissions, privacy policy, telemetry, deployment, user data, Phase 1, or MCP behavior.

## Verification

- Targeted audit suite: `8 passed`.
- Full branch-local suite: `440 passed, 0 failed, 0 skipped, 5 warnings`.
- Fresh clone, fresh Python 3.12 environment, pinned install, full suite: `440 passed, 0 failed, 0 skipped, 5 warnings`.
- Whole-change diff check: PASS.
- Scoped secret-pattern scan: PASS.

The five warnings are the accepted baseline: one `datetime.utcnow()` deprecation, three Pydantic class-config deprecations, and one short JWT rejection-test key warning.

## Principal findings

- Severity 1: capture and injection default on without onboarding consent receipt.
- Severity 1: no pre-injection preview/approve/reject/edit surface.
- Severity 1: prompt excerpts appear in console/toast diagnostics.
- Severity 2: no guided onboarding or safe removable sample flow.
- Severity 2: local/cloud and semantic/keyword modes are not adequately disclosed.
- Severity 2: public claims overstate control and unverified team/analytics/commercial behavior.
- Severity 2: irreversible clear-all has no recovery.
- Severity 2: popup/login control labeling has accessibility defects.

These findings mean onboarding safety is not complete. Green tests prove the audit contract and repository regression suite, not live product readiness.

## Six gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Pass for source audit | Repository-relative references resolve; live routes/store remain blocked |
| Claims | Pass for audit | Matrix identifies contradicted/unverified claims without asserting fixes |
| Functionality | Pass | Audit checks and full suite pass locally and from fresh clone |
| Accessibility | Fail/blocked for product | Static defects found; live keyboard, screen-reader, focus, and contrast evidence absent |
| Security/privacy | Fail for product / pass for audit handling | Severity-1 default/preview/logging findings recorded without user data |
| Performance | Not applicable | Documentation/test-only audit; no runtime product path changed |

## Rollback and approvals

Rollback is closing the draft PR and deleting `agent/b06-onboarding-audit`. Any remediation, browser evidence, copy/privacy change, publication, deployment, telemetry, user contact, or Phase 1 work requires a separate approved issue.
