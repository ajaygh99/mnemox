# B-09 exact-candidate validation

Issue: `ajaygh99/mnemox#16`

Validated candidate: `466f00d0d618c4c64afc7d8c44dfd96c74ec27bc`

Baseline: `origin/main` at `4087e046358eec22bc62e8bdf74fa11c575e6a9b`

## Scope

- Candidate changes only `.github/workflows/autonomous-review.yml`.
- Evidence commit changes only `evidence/B-09/**`.
- No product code, deployment, publication, telemetry, permissions requested by
  the extension, privacy policy, billing, user data, Phase 1, or MCP behavior
  changed.
- No bot account or repository secret was created.

## Verification

Environment: Python 3.12.10 with the repository's pinned dependencies.

- YAML parse and static workflow assertions: PASS.
- Prohibited strings absent: `gh pr review`, `REVIEWER_TOKEN`, and
  `actions/checkout`.
- Required controls present: `Test Suite`, `pull_request_target`, exact
  `head_sha` query, `gh pr merge`, and `--auto`.
- `git diff --check`: PASS.
- `python -m pytest tests/governance -q`: **16 passed**.
- `python -m pytest -q`: **440 passed, 0 failed, 0 skipped, 5 warnings**.

The five warnings are the established baseline: one `datetime.utcnow()`
deprecation, three Pydantic class-config deprecations, and one intentionally
short JWT rejection-test key warning.

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| Links | Pass | Only repository API routes and workflow identifiers are used. |
| Claims | Pass | Evidence does not claim a live merge before post-merge validation. |
| Functionality | Pass for candidate | YAML/static checks and 440 regression tests pass. |
| Accessibility | Not applicable | No user interface changes. |
| Security/privacy | Pass for workflow design | No PR checkout, self-approval, reviewer secret, content telemetry, or protection bypass. |
| Performance | Pass | No product runtime path changed; full performance guards pass. |

## Review and rollback

Independent review is required on the final draft-PR head. Rollback is reverting
the workflow/evidence commits; the prior workflow is broken but does not need to
be re-enabled to preserve data. No merge, deployment, or Phase 1 activation is
authorized by this evidence.
