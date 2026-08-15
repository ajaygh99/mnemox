# B-10 validation

Issue: `ajaygh99/mnemox#20`

Validated candidate: `34ecee1fb49378b27a8a4bdd91acbf7526c86701`

Baseline: B-09 merge `8413bdea087cd1550edddecca42873e1de5b6181`

## Scope

- Candidate changes only
  `tests/governance/test_autonomous_review_negative_paths.py`.
- Evidence commit changes only `evidence/B-10/**`.
- No workflow, product code, deployment, telemetry, extension permission,
  privacy policy, billing, user data, bot identity, B-08, or Phase 1 state
  changed.

## Verification

- B-10 tests: **17 passed** locally.
- Complete governance suite: **33 passed** locally.
- Exact-candidate GitHub Test Suite run `31857582870`: **457 passed**, 0 failed,
  5 known warnings, conclusion success.
- `git diff --check`: **PASS**.

The local full-suite attempt reached 456 passed tests before Windows Application
Control blocked loading gRPC's installed native `cygrpc` DLL. This was an
environment-policy import error, not a failed assertion. The repository's
Windows GitHub runner installed the pinned dependencies and completed all 457
tests successfully on the exact candidate SHA.

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| Prohibited states | Pass | Six scenario families refuse eligibility. |
| Exact-head tests | Pass | Only a successful run matching current `head_sha` satisfies the model and workflow assertions. |
| Review protection | Pass | No approval, actor exception, `--admin`, direct merge, or bypass exists; native `--auto` leaves protection authoritative. |
| Phase order | Pass | B-09, B-10, B-08, reviewed exit, then separately authorized Phase 1 are asserted in order. |
| Governance | Pass | 33 governance tests pass. |
| Full regression | Pass | GitHub exact-candidate run reports 457 passed. |
| Independent review | Pending | `shammyajju` must review the final evidence head with write access. |

## Boundary

These tests prove deterministic refusal logic and trusted workflow invariants.
They do not claim a production merge or activate B-08 or Phase 1. The draft PR
must remain unmerged until independent approval is recorded on the final head.
