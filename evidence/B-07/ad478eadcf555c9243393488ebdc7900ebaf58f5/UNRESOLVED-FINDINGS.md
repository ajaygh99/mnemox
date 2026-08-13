# B-07 unresolved findings

Validated candidate: `ad478eadcf555c9243393488ebdc7900ebaf58f5`

## Severity 1 product findings from B-06

1. Capture and injection default on without an onboarding consent receipt.
2. No pre-injection preview, approve, reject, or edit decision surface.
3. Prompt excerpts can appear in console/toast diagnostics.

These findings block a positive privacy/onboarding exit. B-07 documents them;
it does not authorize or implement remediation.

## Other exit blockers and evidence gaps

- Live browser, store, keyboard, focus, contrast, and screen-reader evidence is
  incomplete.
- B-04 has no tracked `evidence/B-04/**` validation artifact.
- The five-user protocol exists, but the study has not been executed under a
  separately approved participant-contact action.
- Multiple merged Phase 0 PRs lack a GitHub `APPROVED` review.
- B-09, B-10, and B-08 remain incomplete and must run in that order.
- The autonomous-review workflow merged in PRs #14/#17 has not demonstrated a
  successful independent approval and protected auto-merge path.

## Prohibited conclusions

Green tests do not establish that Phase 0 passed, that continuous autonomy is
active, or that Phase 1 may start. Only a separately reviewed Phase 0 exit
decision can make that determination.
