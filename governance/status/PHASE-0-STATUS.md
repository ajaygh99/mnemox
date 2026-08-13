# Phase 0 consolidation status

Status date: 2026-08-12

Authority: issue #18 (B-07)

This record separates delivery completion from Phase 0 exit readiness. A merged
pull request proves that a scoped artifact entered `main`; it does not prove
that every product, privacy, accessibility, or independent-review gate passed.

## Delivery matrix

| Item | Issue | Pull request | Merge commit | Delivery | Exit implication |
|---|---:|---:|---|---|---|
| B-01 inventory | #2 | #3 | `0cd1376dea6f2a3bf2967a52b19e8d892a49e20d` | Complete | Claims and live-link evidence remained incomplete. |
| B-02 reproducible tests | #4 | #5 | `a4129b134b1f9c9ceb93012142daa5308bf369b6` | Complete | Full pinned suite became reproducible. |
| B-03 event contract | #8 | #9 | `5208e5cc4b6ac248a80361cbb33ec6463e090554` | Complete | Contract is non-collecting; telemetry was not activated. |
| B-04 CI bootstrap | #6 | #7 | `c21793513e234b92bfbd94c1aa3548b494616b6f` | Complete with evidence gap | CI exists, but no `evidence/B-04/**` artifact is tracked. |
| B-05 study protocol | #10 | #11 | `8eb34ca8bf97db576a0dc5447cb9c6c97b7dfae4` | Protocol complete | The five-user study was not executed; no participant outcome is claimed. |
| B-06 onboarding audit | #12 | #13 | `50c372db55617386d5a279f58984fc39cd2df452` | Audit complete | Three severity-1 product findings remain open. |
| B-07 consolidation | #18 | pending | pending | In progress | Does not authorize Phase 0 exit or Phase 1. |
| B-09 contract/workflow repair | #16 | pending | pending | Needs refinement | Must follow merged B-07. |
| B-10 phase-order negative tests | #20 | pending | pending | Needs refinement | Must follow merged B-09. |
| B-08 documentation-only dry run | #19 | pending | pending | Needs refinement | Must follow merged B-10. |

## Phase 0 exit gates

| Gate | Status | Basis |
|---|---|---|
| Links | Blocked | Repository links were audited, but live browser/store evidence is incomplete. |
| Claims | Fail | B-06 records contradicted or unverified public claims. |
| Functionality | Pending | Regression suites are green through B-06, but B-09, B-10, and B-08 remain. |
| Accessibility | Fail/blocked | B-06 records labeling defects and missing live keyboard, focus, contrast, and screen-reader evidence. |
| Security/privacy | Fail | Defaults-on capture/injection, absent pre-injection decision controls, and prompt excerpts in diagnostics are severity-1 findings. |
| Performance | Pass for current tested baseline | Performance guards pass; B-07 changes no runtime path. |
| Independent review | Fail | Several merged Phase 0 PRs have no GitHub `APPROVED` review recorded. Owner comments and manual merges are not independent approvals. |

Phase 0 exit is therefore **not approved**. Continuous autonomy and Phase 1
remain disabled until B-09, B-10, and B-08 complete and the owner reviews a
separate Phase 0 exit decision.

## Queue order

The only permitted order after B-07 is:

1. B-09 (#16)
2. B-10 (#20)
3. B-08 (#19)
4. reviewed Phase 0 exit decision
5. separately contracted and owner-authorized Phase 1 issue

No later item becomes eligible merely because an earlier pull request has green
tests. Its issue contract must be complete and it must be the sole issue labeled
`agent-ready` when claimed.
