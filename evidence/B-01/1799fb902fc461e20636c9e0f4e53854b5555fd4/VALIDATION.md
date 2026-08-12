# B-01 exact-candidate validation

Issue: `ajaygh99/mnemox#2`  
Candidate commit evaluated: `1799fb902fc461e20636c9e0f4e53854b5555fd4`  
Baseline: `origin/main` at `2b80eed0b984ccf7febc3ce806d871395c2f9263`  
Change scope: `sprint/PRODUCT-INVENTORY.md`

## Scope and repository checks

- Canonical remote: PASS - `https://github.com/ajaygh99/mnemox.git`.
- Isolated branch: PASS - `agent/b01-canonical-inventory`.
- Allowed paths: PASS - candidate changes only `sprint/PRODUCT-INVENTORY.md`.
- Product code changed: NO.
- Production, store, privacy, permission, billing, data, or MCP action: NO.

## Python baseline

- Python 3.12.10 installed from the official `Python.Python.3.12` winget package.
- Branch-local virtual environment used; it is excluded by `.gitignore`.
- Repository dependency manifest: BLOCKED - none is tracked.
- Initial `python -m pytest -q`: 345 passed, 46 failed. Most failures were Windows CP1252 decoding errors caused by tests opening UTF-8 assets without an explicit encoding.
- Single bounded diagnostic rerun with `PYTHONUTF8=1`: 390 passed, 1 failed, 5 warnings.
- Remaining failure: `tests/performance/test_performance_guards.py::test_release_version_is_0_1_21` expects `0.1.21`, while `extension/manifest.json` is `0.1.22` on the baseline commit.

The remaining failure is pre-existing and outside B-01's allowed paths. It was not hidden, skipped, or repaired by modifying production behavior.

## Six validation gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Blocked | Repository URLs inventoried; live browser/store routes not tested by B-01 |
| Claims | Fail | Source contains production/marketing claims without production evidence |
| Functionality | Fail | Supported suite is not yet reproducible; UTF-8 mode leaves one stale version assertion |
| Accessibility | Not applicable | Documentation-only change |
| Security/privacy | Pass | No sensitive content, secrets, telemetry, permissions, or data behavior changed |
| Performance | Fail | The only residual failing test is in the performance guard suite, though it asserts version rather than runtime performance |

## Review and rollback

Independent review is required on the final draft-PR head. One bounded diagnostic rerun has been used; no further repair is authorized in B-01. Rollback is branch/PR deletion only.
