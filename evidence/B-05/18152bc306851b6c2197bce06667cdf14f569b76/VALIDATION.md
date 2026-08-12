# B-05 exact-candidate validation

Issue: `ajaygh99/mnemox#10`

Validated implementation: `18152bc306851b6c2197bce06667cdf14f569b76`

Baseline: `origin/main` at `5208e5cc4b6ac248a80361cbb33ec6463e090554`

## Outcome and scope

- Defined an exactly-five-participant, uncoached first-use protocol.
- Added verbatim consent, privacy/data policy, structured observation template, aggregate results template, severity rubric, and stop conditions.
- Added eight automated governance checks.
- Did not recruit, contact, schedule, compensate, observe, or record participants.
- Did not change product code, telemetry, deployment, publication, permissions, privacy policy, billing, user data, Phase 1, or MCP behavior.

## Verification

- Targeted governance suite: `8 passed`.
- Full branch-local suite: `432 passed, 0 failed, 0 skipped, 5 warnings`.
- Fresh clone, fresh Python 3.12 virtual environment, pinned dependency install, full suite: `432 passed, 0 failed, 0 skipped, 5 warnings`.
- Whole-change `git diff --check`: PASS.
- Scoped credential/private-key signature scan: PASS.

The five warnings are the accepted repository baseline: one `datetime.utcnow()` deprecation, three Pydantic class-config deprecations, and one short JWT rejection-test key warning.

## Privacy and research safeguards

- Participant codes are limited to P01-P05 with no identity lookup table.
- The structured record has no name, email, prompt, response, memory, content, credential, URL, stable identifier, recording, screenshot, transcript, or free-form notes field.
- No audio, video, screen recording, or verbatim transcription is allowed.
- Valid coded records are deleted 30 days after the Phase 0 exit decision; declined/withdrawn records are deleted within two business days.
- Accidental prohibited-data capture stops the study, restricts access, triggers owner notification and deletion confirmation, and blocks resumption without approval.
- Severity-1 data/control failures block Phase 0 exit.

## Six gates

| Gate | Result | Evidence |
|---|---|---|
| Links | Pass | Repository-relative protocol links resolve and the GitHub issue link is valid |
| Claims | Pass | Templates label results as five-user observations, not representative proof or release authorization |
| Functionality | Pass | Governance and full suites pass locally and from a fresh clone |
| Accessibility | Pass for protocol | Verbatim script, neutral task language, and coded outcomes avoid relying on visual screenshots; actual participant accessibility remains future execution evidence |
| Security/privacy | Pass | Content-free structure, access/retention/deletion rules, incident stops, and automated prohibited-field checks pass |
| Performance | Not applicable | Documentation and test-contract change only; no product runtime path changed |

## Rollback and approvals

Rollback is closing the draft PR and deleting `agent/b05-first-use-study-protocol`. Recruitment, contact, compensation, scheduling, study execution, data collection, retention changes, and publication require separate owner approval.
