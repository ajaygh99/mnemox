# B-07 exact-candidate validation

Issue: `ajaygh99/mnemox#18`

Validated candidate: `ad478eadcf555c9243393488ebdc7900ebaf58f5`

Baseline: `origin/main` at `50c372db55617386d5a279f58984fc39cd2df452`

## Issue-to-commit mapping

| Item | Issue | PR | Validated implementation head | Merge commit | Repository evidence |
|---|---:|---:|---|---|---|
| B-01 | #2 | #3 | `a02c87367330b9c0dff9399edc8f17fce4fffd5d` | `0cd1376dea6f2a3bf2967a52b19e8d892a49e20d` | `evidence/B-01/3cf4abd7b4951c8ddc34654dbe18c5211cb33386/VALIDATION.md` |
| B-02 | #4 | #5 | `a6ea513bf0ae1d6b3f4153eeceec112317341cf0` | `a4129b134b1f9c9ceb93012142daa5308bf369b6` | `evidence/B-02/761857705d7e58774591fe8a34c0b655994fc3a2/VALIDATION.md` |
| B-03 | #8 | #9 | `f9eadd76429f136a5a456d77d8b0e49b3976946e` | `5208e5cc4b6ac248a80361cbb33ec6463e090554` | `evidence/B-03/5e7e72be592329221c90754925169bf0a7700c41/VALIDATION.md` |
| B-04 | #6 | #7 | `392dc678d836635aa25d511c5c081aa80449c9fc` | `c21793513e234b92bfbd94c1aa3548b494616b6f` | Missing from `evidence/B-04/**`; recorded as a gap |
| B-05 | #10 | #11 | `5d7275cc8286cd328fd8e0592265ac0083bf25dd` | `8eb34ca8bf97db576a0dc5447cb9c6c97b7dfae4` | `evidence/B-05/18152bc306851b6c2197bce06667cdf14f569b76/VALIDATION.md` |
| B-06 | #12 | #13 | `9057d9fef10bd8ac6119be3170626d86265267ff` | `50c372db55617386d5a279f58984fc39cd2df452` | `evidence/B-06/bccfc707cf39e64d090e3aeb45b0fd6c1dc50e4b/VALIDATION.md` |

All six issues are closed. Their stale `agent-claimed` and
`approval-required` labels were removed during B-07; each closed issue now has
`evidence-ready`. This label cleanup does not invent missing B-04 evidence.

## Verification

Environment: Python 3.12.10, isolated `.venv`, pinned `requirements.txt`.

- `python -m pytest tests/governance -q`: **16 passed**.
- `python -m pytest -q`: **440 passed, 0 failed, 0 skipped, 5 warnings**.
- `git diff --check`: PASS.
- Candidate changed only `governance/status/**`.
- Evidence commit changes only `evidence/B-07/**`.
- No product code, deployment, permissions, privacy policy, telemetry, billing,
  publication, user data, Phase 1 implementation, or MCP implementation changed.

The five warnings are the established baseline: one `datetime.utcnow()`
deprecation, three Pydantic class-config deprecations, and one deliberately
short JWT key warning in a rejection test.

## Review record

PRs #5, #7, and #13 contain no review records. PRs #3, #9, and #11 contain
owner comments with state `COMMENTED`, not `APPROVED`. These exceptions are not
reclassified as independent approvals. The B-07 final head requires an
independent review after exact-head GitHub Actions passes.

## Rollback

Revert the B-07 documentation/evidence commits and restore the issue-label
snapshot recorded here. No runtime or production rollback is required.
