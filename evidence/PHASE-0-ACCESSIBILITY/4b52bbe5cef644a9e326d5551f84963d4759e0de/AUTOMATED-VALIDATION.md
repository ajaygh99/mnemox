# Automated accessibility validation

Validated candidate: `4b52bbe5cef644a9e326d5551f84963d4759e0de`

- JavaScript syntax for content, popup, login, and dashboard scripts: PASS.
- Focused accessibility and directly affected extension tests: 186 passed.
- Governance suite: 39 passed.
- Full suite: 479 passed, 0 failed, 0 skipped, 5 known warnings.
- `git diff --check`: PASS.
- Allowed-path review: PASS.

The five warnings are pre-existing: one `datetime.utcnow` deprecation, three Pydantic class-config deprecations, and one test JWT HMAC key-length warning.

Static contracts verify names, labels, native navigation controls, live-region attributes, switch state, focus-visible styling, dialog focus logic, consent-aware dashboard controls, and defined contrast pairs. Static checks do not prove live browser or screen-reader behavior.

The separate live evidence files record the owner's 2026-08-15 manual keyboard, reflow, and NVDA attestation. Codex did not independently observe those checks.
