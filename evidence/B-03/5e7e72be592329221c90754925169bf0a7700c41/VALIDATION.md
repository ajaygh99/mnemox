# B-03 exact-candidate validation

Issue: `ajaygh99/mnemox#8`

Validated implementation: `5e7e72be592329221c90754925169bf0a7700c41`

Baseline: `origin/main` at `0cd1376dea6f2a3bf2967a52b19e8d892a49e20d`

## Outcome and scope

- Added a versioned JSON Schema for eight content-free event types.
- Added a standard-library, fail-closed validator driven by the schema.
- Added 33 privacy-contract tests, including prohibited-field and sensitive-pattern cases.
- Added developer privacy documentation.
- Did not add transport, storage, telemetry instrumentation, identifiers, vendor code, consent changes, permissions, product behavior, or production data collection.

## Verification

- Targeted privacy suite: `33 passed`.
- Full branch-local suite: `424 passed, 0 failed, 0 skipped, 5 warnings`.
- Fresh clone, fresh Python 3.12 virtual environment, pinned dependency install, full suite: `424 passed, 0 failed, 0 skipped, 5 warnings`.
- Draft 2020-12 schema metavalidation using `Draft202012Validator.check_schema`: PASS. The metavalidator was used as a local verification tool and was not added as a runtime dependency.
- Whole-change `git diff --check`: PASS.
- Scoped secret-pattern scan: PASS after test signatures were constructed at runtime instead of committed as literal credential/private-key markers.

The five warnings are the accepted repository baseline: one `datetime.utcnow()` deprecation, three Pydantic class-config deprecations, and one short JWT rejection-test key warning.

## Privacy-negative evidence

Tests reject prompt text, response text, memory IDs/content, email, API-key/token fields, source code, URLs, session identifiers, anonymous session hashes, stack traces, sensitive value patterns, unknown fields/events, malformed timestamps, and invalid integer types.

The initial negative run rejected `anonymous_session_hash` under the generic unknown-field gate. The bounded repair classified it explicitly as a prohibited key. A later security scan identified literal fake credential/private-key signatures in tests; fixtures were changed to runtime concatenation while preserving negative coverage.

## Six gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Pass | Repository-relative contract paths and GitHub documentation links are valid |
| Claims | Pass | Documentation states this is a non-collecting contract and does not claim telemetry is active |
| Functionality | Pass | 424 tests pass locally and from a fresh clone |
| Accessibility | Not applicable | No user interface changed |
| Security/privacy | Pass | Allowlists, unknown-field rejection, prohibited-key/value defenses, and negative tests pass |
| Performance | Pass | No runtime product path changed; full performance guards pass |

## Rollback and approvals

Rollback is closing the draft PR and deleting `agent/b03-privacy-event-contract`. Telemetry activation, identifier design, retention, vendor selection, consent/privacy changes, deployment, publication, and merge remain separately approval-gated.
