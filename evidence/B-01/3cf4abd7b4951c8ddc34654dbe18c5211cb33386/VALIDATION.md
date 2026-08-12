# B-01 refreshed exact-candidate validation

Issue: `ajaygh99/mnemox#2`

Candidate commit: `3cf4abd7b4951c8ddc34654dbe18c5211cb33386`

Current-main merge base incorporated: `c21793513e234b92bfbd94c1aa3548b494616b6f`

## Scope

- The existing B-01 branch was updated by merging current `origin/main`; it was not force-pushed or recreated.
- B-01 changes remain limited to `sprint/PRODUCT-INVENTORY.md` and `evidence/B-01/**`.
- B-02 and B-04 files visible in branch history came from their already-merged `main` commits, not from new B-01 modifications.
- No product code, deployment, publication, telemetry, permission, privacy, billing, MCP, credential, or user-data behavior changed.

## Verification

Supported command on Python 3.12.10:

```powershell
$env:PYTHONUTF8 = "1"
python -m pytest -q
```

Result:

```text
391 passed, 5 warnings in 2.63s
```

There were zero failures and zero skips. The warnings are the accepted B-02 baseline: one `datetime.utcnow()` deprecation, three Pydantic class-config deprecations, and one short JWT rejection-test key warning.

## Six gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Blocked | Repository URLs are inventoried; live browser/store-route evidence remains separate Phase 0 work |
| Claims | Fail | Inventory deliberately identifies configured or public-facing claims that lack production evidence |
| Functionality | Pass | Complete pinned suite: 391 passed, zero failed, zero skipped |
| Accessibility | Not applicable | Documentation-only B-01 change |
| Security/privacy | Pass | No secrets, content data, telemetry, permissions, or data behavior changed |
| Performance | Pass | Complete suite includes the performance guards; no runtime behavior changed |

## Rollback and review

Rollback is closing PR #3 and deleting `agent/b01-canonical-inventory`. Independent review and the required exact-head GitHub Actions check remain mandatory before merge.
