# Phase 0 exit assessment validation

Assessment candidate: `67e5ed5f3ad86eb739499a36f05de4c6693ad41f`  
Baseline: `af534de86444b4071c5c55d2bc3e306dfc2f199b`  
Authority: Issue #28

## Commands and results

- `python -m pytest tests/governance -q`: PASS — 39 passed.
- `python -m pytest -q`: PASS — 463 passed, 0 failed, 0 skipped, 5 warnings.
- `git diff --check`: PASS.
- Allowed-path review: PASS. Assessment changes are limited to the two authorized governance status files and `evidence/PHASE-0-EXIT/**`.

The five warnings are existing Python dependency/deprecation or test-key warnings: one `datetime.utcnow` deprecation, three Pydantic class-config deprecations, and one JWT HMAC key-length warning.

## Delivery provenance reviewed

- B-07 PR #22 merged as `4087e046`.
- B-09 PR #23 merged as `8413bdea`.
- B-10 PR #26 merged as `4d448ac390c01f4e84fb11dea7dce53ddfbbc739`.
- B-08 PR #27 merged as `4c31997e6c25078e1b007764a61160512e8a6d37`.
- Performance checkpoint PR #25 merged as `af534de86444b4071c5c55d2bc3e306dfc2f199b`; its independently reviewed branch head was `085e266199030abcfa536b6b23d8ad667d4755e0`.

Because PR #25 used rebase merge, its pre-merge evidence commit was rewritten on `main`. The assessment records both the reviewed head and final merge SHA. The checkpoint proves static budget guards, not measured production performance.

## Scope and safety

No product code, workflow, deployment, publication, telemetry, extension permission, privacy policy, billing, database, user data, Issue #21, or Phase 1 state was changed. No risk was accepted and no owner decision was signed.

## Validation conclusion

The assessment is reproducible for its exact candidate and supports a **DEFERRED** recommendation. Repository tests passing does not override the failed, blocked, and pending product exit gates.
