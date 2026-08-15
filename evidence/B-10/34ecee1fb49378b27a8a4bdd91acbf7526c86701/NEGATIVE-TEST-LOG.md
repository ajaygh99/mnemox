# B-10 negative test log

Issue: `ajaygh99/mnemox#20`

Validated candidate: `34ecee1fb49378b27a8a4bdd91acbf7526c86701`

Baseline: B-09 merge `8413bdea087cd1550edddecca42873e1de5b6181`

## Refusal scenarios proved

- Draft PR: refused.
- Missing `agent-ready` label: refused.
- Base branch other than `main`: refused.
- Fork or different head repository: refused.
- Missing or unsuccessful Test Suite: refused.
- Successful Test Suite from a stale head SHA: refused.
- Self-approval or reviewer-secret dependency: prohibited by source assertion.
- Actor-specific exceptions: prohibited by source assertion.
- Direct merge, `--admin`, swallowed failure, or branch-protection bypass:
  prohibited by source assertion.
- PR-controlled checkout or code execution: prohibited by source assertion.
- B-08 and Phase 1 before the recorded Phase 0 sequence: refused by governance
  order assertion.

The positive control permits eligibility only when the PR is same-repository,
targets `main`, has `agent-ready`, is not a draft, and has a successful Test
Suite for the exact current head. Eligibility only enables native squash
auto-merge; it does not approve or bypass branch protection.

## Results

- `python -m pytest tests/governance/test_autonomous_review_negative_paths.py -q`:
  **17 passed**.
- `python -m pytest tests/governance -q`: **33 passed**.
- GitHub Test Suite run `31857582870` on the exact candidate: **457 passed,
  5 warnings**, conclusion success.

No live pull request was merged or used as a destructive test. The suite is a
deterministic executable model plus source-bound assertions against the trusted
workflow on the B-09 baseline.
