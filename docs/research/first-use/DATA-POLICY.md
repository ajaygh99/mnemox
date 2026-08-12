# First-use study data policy

## Data minimization

Use `participant-observation.template.json` for each valid session. Participant codes are limited to `P01`-`P05` and are assigned without a lookup table. Do not collect identity, contact information, stable identifiers, raw content, recordings, screenshots, transcripts, free-form notes, device details, URLs, or credentials.

The structured record contains only consent state/time, approved build version, task enums, elapsed seconds, counts, intervention codes, severity, protocol-deviation codes, deletion deadline, and sanitized issue codes. Issue codes identify a product behavior category, not a person or content item.

## Storage and access

Before any study, the owner must approve a private evidence location and name the study owner and independent reviewer. Access is limited to those two roles. Do not store records in public issues, PR comments, analytics systems, chat transcripts, shared drives with broad access, or this repository.

Encrypt the approved storage at rest and in transit using the provider's standard controls. Do not create a participant-code lookup table. Do not place secrets or access links in study evidence.

## Retention, withdrawal, and deletion

- Set each valid record's deletion deadline to 30 calendar days after the recorded Phase 0 exit decision.
- Delete declined-consent and withdrawn-participant records within two business days.
- On deletion, remove primary and ordinary recoverable copies under the approved storage procedure and record only aggregate deletion counts and completion date.
- Do not extend retention without a new owner-approved issue stating purpose, scope, and privacy review.

## Incident handling

If prohibited data is entered, displayed in a recording, or copied into notes:

1. stop the session and do not reproduce the data;
2. restrict access to the study owner;
3. record only incident code `PROHIBITED_DATA_CAPTURED`, participant code, UTC time, and affected storage location category;
4. notify the owner through the approved private channel;
5. delete the prohibited material and confirm deletion;
6. classify the product/control impact using the severity rubric; and
7. do not resume studies until the owner approves the corrective protocol.

Never paste prohibited data into GitHub, telemetry, terminal output, or an evidence pack.

## Aggregate reporting

Report counts, medians, ranges, completion rates, severity totals, intervention totals, and sanitized issue codes. With only five participants, describe results as observations, not statistically representative claims. Separate observed results, facilitator hypotheses, and owner decisions.
