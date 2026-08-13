# Performance checkpoint validation

Issue: `ajaygh99/mnemox#24`

Validated candidate: `0e0ff35bfd94684f838ced3563aa5a418ccc781d`

Baseline: `origin/main` at `4087e046358eec22bc62e8bdf74fa11c575e6a9b`

Environment: Windows, Python 3.12.10, dependencies pinned by
`requirements.txt`.

## Commands and results

- `python -m pytest tests/performance -q`: **13 passed** in 0.13 s.
- `python -m pytest tests/governance -q`: **16 passed** in 0.07 s.
- `python -m pytest -q`: **440 passed** in 2.71 s, with 5 known warnings.
- `git diff --check`: **PASS**.

The warnings were one `datetime.utcnow()` deprecation, three Pydantic
class-configuration deprecations, and one intentionally short JWT test-key
warning. None was introduced by the documentation-only candidate.

## Gate results

| Gate | Result | Basis |
|---|---|---|
| Scope | Pass | Candidate changes one allowed governance status file; evidence commit changes only the allowed evidence tree. |
| Performance guards | Pass | 13 source-invariant tests pass. |
| Governance | Pass | 16 governance tests pass. |
| Regression | Pass | Full 440-test suite passes. |
| Measurement honesty | Pass | Checkpoint explicitly rejects unmeasured latency, capacity, and resource claims. |
| Phase ordering | Pass | B-09, B-10, B-08, reviewed Phase 0 exit, and separate Phase 1 authorization remain required. |
| Independent review | Pending | Draft PR review is required on the final evidence head. |

## Evidence boundary

Test execution times above describe the local pytest commands only. They are
not product latency measurements and must not be used as browser, API,
throughput, CPU, memory, or production-performance evidence.
