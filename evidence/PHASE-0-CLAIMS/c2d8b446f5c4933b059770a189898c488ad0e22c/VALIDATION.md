# Validation

Candidate implementation: `c2d8b446f5c4933b059770a189898c488ad0e22c`

Baseline: `origin/main` at `dab8117575629a62e05477c0ea62b9feb1b4945d`

## Results

| Check | Command | Result |
|---|---|---|
| Public-claims contract and affected onboarding governance | `python -m pytest tests/governance/test_public_claims_contract.py tests/governance/test_onboarding_audit_contract.py -q` | PASS — 15 passed |
| Governance suite | `python -m pytest tests/governance -q` | PASS — 46 passed |
| Full supported suite | `python -m pytest -q` with `PYTHONUTF8=1` | PASS — 486 passed, 0 failed, 0 skipped, 5 known warnings |
| HTML static parse | `test_public_html_is_statically_parseable` in the public-claims contract | PASS |
| Prohibited active-copy scan | Contract assertions exclude the protected embedded policy and reject prohibited phrases | PASS |

## Allowed-path audit

Implementation commit paths:

- `website/index.html`
- `docs/audits/onboarding/CLAIM-CAPABILITY-MATRIX.md`
- `docs/audits/onboarding/FRICTION-REGISTER.md`
- `tests/governance/test_public_claims_contract.py`

Evidence commit adds only `evidence/PHASE-0-CLAIMS/c2d8b446f5c4933b059770a189898c488ad0e22c/**`.

All paths are allowed by Issue #34. No deployment, publication, product behavior, billing, telemetry, extension permission, user-data, Issue #21, or Phase 1 state change is included.

## Review boundary

This evidence validates repository copy at the candidate implementation SHA. It is not deployment or publication approval. The final PR head must pass GitHub checks and receive independent review from `shammyajju`; the PR must remain unmerged.

