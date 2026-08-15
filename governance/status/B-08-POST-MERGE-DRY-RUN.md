# B-08 post-merge dry run

Status date: 2026-08-15

Authority: issue #19

Baseline: merged B-10 commit `4d448ac390c01f4e84fb11dea7dce53ddfbbc739`

## Simulation decision

This is a deterministic repository-state simulation of a documentation-only
governance merge. It verifies that protected product and operational surfaces
remain byte-for-byte identical to the merged B-10 baseline.

No production system was contacted. No extension was loaded, backend deployed,
database queried or migrated, Stripe operation performed, user data read or
written, telemetry emitted, package published, or live pull request merged by
the simulation.

## Simulated post-merge state

| Surface | Expected result | Verification |
|---|---|---|
| Extension | Version remains `0.1.22`; permissions and runtime package unchanged. | Manifest SHA-256 pinned to B-10 baseline. |
| Backend | API entry point and database adapter unchanged. | `backend/main.py` and `backend/database.py` fingerprints pinned. |
| Dependencies | Backend dependency set unchanged. | `backend/requirements.txt` fingerprint pinned. |
| Database | Supabase schemas unchanged; no migration command runs. | Both tracked schema fingerprints pinned. |
| Billing | Stripe/billing implementation and product pricing configuration unchanged. | `backend/billing.py` and `product.config.json` fingerprints pinned. |
| Deployment | Railway configuration unchanged; no deployment command runs. | `railway.toml` fingerprint pinned and side-effect commands prohibited. |
| Automation | B-09 trusted workflow unchanged and does not check out or execute product code. | Workflow fingerprint and source assertions pinned. |
| User data | Unaffected by this repository-only simulation. | No service connection, credential, API call, or data operation occurs. |
| Phase 1 | Remains disabled pending a reviewed exit decision and separate owner authorization. | Existing Phase 0 status boundary asserted. |

## Evidence boundary

This dry run proves repository invariance for the listed protected files and
the absence of side-effect commands in the simulation. It is not production,
browser, database, billing, accessibility, privacy, deployment, or user-data
validation and makes no such claim.

## Outcome

If the simulation and full regression suite pass on the exact candidate, B-08
is eligible for independent review. This record does not authorize Phase 1 and
does not replace the separate Phase 0 exit decision.

## Rollback

Revert the governance simulation, this status record, and its evidence commit.
There is no product or production state to restore.
