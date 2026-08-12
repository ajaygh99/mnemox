# B-02 exact-candidate validation

Issue: `ajaygh99/mnemox#4`

Candidate commit: `761857705d7e58774591fe8a34c0b655994fc3a2`

Baseline: `origin/main` at `2b80eed0b984ccf7febc3ce806d871395c2f9263`

## Scope

- Branch: `agent/b02-pinned-dependencies`
- Changed paths: `requirements.txt` and tracked `tests/**/*.py` only.
- No extension, backend, website, workflow, telemetry, MCP, deployment, permission, privacy, billing, credential, or user-data change.
- Requirements contain exact versions and no editable, local-path, or `file:` entries.
- All tracked Python-test `open()` calls now declare `encoding='utf-8'`.
- The release guard now matches the tracked manifest version `0.1.22`.

## Verification

Python: 3.12.10

Branch-local run without `PYTHONUTF8`:

```text
391 passed, 5 warnings in 2.29s
```

Required branch-local run with `PYTHONUTF8=1`:

```text
391 passed, 5 warnings in 2.17s
```

Fresh clone from candidate, fresh virtual environment, `pip install -r requirements.txt`, and full run with `PYTHONUTF8=1`:

```text
391 passed, 5 warnings in 4.28s
```

No tests failed or were skipped. The five warnings are pre-existing: one `datetime.utcnow()` deprecation, three Pydantic v2 class-config deprecations, and an intentionally short JWT key used by a rejection test. Warning removal is outside B-02 because it would require backend/product or broader test-fixture changes.

## Six gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Not applicable | No links changed |
| Claims | Not applicable | No product claims changed |
| Functionality | Pass | Branch-local and fresh-clone suites: 391 passed, 0 failed, 0 skipped |
| Accessibility | Not applicable | No user interface changed |
| Security/privacy | Pass | Isolated dependency capture; no secrets/local paths; no content handling changed |
| Performance | Pass | Full performance test directory included in the green suite |

## Rollback and review

Rollback: close the draft PR and delete the branch. Independent review remains required on the final draft-PR head before any merge decision.
