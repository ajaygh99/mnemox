# Mnemox five-user first-use study protocol

Status: protocol only; owner approval is required before recruitment, contact, scheduling, compensation, or data collection.

## Research question and success boundary

Can a new user, without coaching, understand Mnemox's local/cloud state and complete one controlled memory assist while retaining control over preview, rejection, pause, and removal?

Run the same protocol with exactly five consenting participants, coded `P01` through `P05`. The protocol measures observed behavior; it does not prove population-level activation or retention.

Phase 0 remains blocked if any participant encounters a severity-1 data/control failure. Timing and completion results inform later targets but do not authorize Phase 1.

## Roles and prerequisites

- Study owner: approves recruitment, facilitator, environment, and data access.
- Facilitator: reads the script verbatim, records coded fields, and does not coach.
- Independent reviewer: checks protocol adherence, severity classification, and aggregate claims.
- Participant: an adult who provides consent and is not required to disclose private content.

Before each session, verify the approved build/version, a clean browser profile, a supported test site, a clearly synthetic sample scenario, working deletion/reset controls, and an empty observation record. Do not use a participant's existing account, conversations, memories, or credentials. If authentication is unavoidable, stop and redesign the session rather than recording login activity.

## Session script

1. Read `CONSENT.md` verbatim and record only the consent enum and timestamp.
2. Start the timer after consent. Give the participant the synthetic scenario card; do not explain the interface.
3. Ask: "What do you believe Mnemox will capture, where will it be stored, and what control do you expect before anything is used?"
4. Ask the participant to identify whether the current site is supported.
5. Ask the participant to reach the first-use state using only the synthetic sample supplied for the study.
6. Ask the participant to inspect the proposed assist, decide whether to approve or reject it, and explain the available controls without quoting displayed content.
7. Ask the participant to pause Mnemox, undo or remove the synthetic sample, and confirm the resulting state.
8. Ask the comprehension questions below, stop the timer, and read the withdrawal/deletion reminder.

## Standard tasks and coded outcomes

| Task code | Participant goal | Allowed outcome |
|---|---|---|
| `T1_TRUST` | Explain capture, storage, injection, and control expectations | `clear`, `partial`, `incorrect`, `blocked` |
| `T2_SUPPORT` | Determine whether the current site is supported | `complete`, `incorrect`, `blocked` |
| `T3_FIRST_VALUE` | Reach one controlled assist with synthetic data | `complete`, `abandoned`, `blocked` |
| `T4_DECISION` | Approve or reject from the preview/control surface | `complete`, `incorrect`, `blocked` |
| `T5_RECOVERY` | Pause and remove/undo the synthetic sample | `complete`, `partial`, `blocked` |
| `T6_COMPREHENSION` | Answer the closing control questions | `clear`, `partial`, `incorrect` |

Record only task code, outcome enum, elapsed seconds, attempt count, intervention code, severity, and sanitized issue code. Do not transcribe what the participant says or what appears on screen.

## Comprehension questions

- Is Mnemox currently local-only or using an approved cloud mode?
- What happens before remembered context is used?
- How would you reject, pause, remove, or undo an assist?
- What should you do if the site is unsupported or the state is unclear?

Record `clear`, `partial`, or `incorrect`; never record the verbatim answer.

## Non-coaching and intervention threshold

The facilitator may repeat the task once, neutrally, after 60 seconds of no progress. No pointing, feature naming, navigation hint, or corrective explanation is allowed before an intervention threshold is reached.

Intervene only when:

- 120 seconds pass with no progress (`TIME_LIMIT`);
- the participant is about to enter personal or sensitive content (`PRIVACY_STOP`);
- a data/control risk could affect existing information (`SAFETY_STOP`); or
- the participant asks to stop (`PARTICIPANT_STOP`).

Record the intervention code and end or reset the task. Any coached completion is recorded as `blocked`, never `complete`.

## Severity rubric

| Severity | Definition | Required response |
|---|---|---|
| 1 | Unauthorized capture/disclosure, cross-user/project exposure, loss of control/data, misleading consent, or inability to stop/remove an assist | Stop the study; quarantine evidence; notify owner; Phase 0 exit blocked |
| 2 | Primary first-use journey cannot complete or trust state is materially wrong, without confirmed data exposure | Stop that task; document coded issue; owner triage before more sessions |
| 3 | Recoverable friction requiring intervention or causing incorrect comprehension | Continue only if safe; include in prioritized findings |
| 4 | Cosmetic, wording, or minor efficiency issue with no control or completion impact | Record sanitized issue code; continue |

When uncertain, assign the more severe level pending independent review.

## Stop conditions

Stop the session immediately for withdrawn consent, prohibited-data entry/capture, unexpected recording, credential exposure, a severity-1 event, inability to reset synthetic data, or facilitator deviation that invalidates the observation. Follow `DATA-POLICY.md`; do not copy sensitive material into an issue or evidence pack.

## Completion and review

After five valid sessions, populate `RESULTS-TEMPLATE.md` using aggregates and sanitized issue codes. The independent reviewer verifies consent records, protocol deviations, severity assignments, deletion deadlines, and claim wording. Recruitment bias, invalid sessions, and missing data remain visible; do not replace a result merely because it is unfavorable.
