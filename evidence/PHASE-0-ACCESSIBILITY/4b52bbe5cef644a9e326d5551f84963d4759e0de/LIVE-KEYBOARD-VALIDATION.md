# Live keyboard validation

Validated candidate: `4b52bbe5cef644a9e326d5551f84963d4759e0de`

Status: **PASS — owner-reported manual observation**

Codex attempted to initialize the available browser-control skill, but its required `scripts/browser-client.mjs` runtime file was unavailable. No substitute browser automation was used.

On 2026-08-15, the owner reported completing manual validation against PR #33 and attested:

- visible yellow focus outline: PASS;
- Tab and Shift+Tab containment inside the injection dialog: PASS;
- Escape closes without sending and returns focus: PASS;
- required UI remains usable at 200% zoom: PASS.

These results are recorded as owner attestation; Codex did not independently observe them. Chrome version and observer name were not supplied.

Checks covered by the attestation:

- popup Tab order and visible focus;
- login/sign-up/continue actions by keyboard;
- injection dialog initial focus, Tab/Shift+Tab containment, all decisions, Escape cancellation, and prompt focus return;
- 200% zoom/reflow on popup and login;
- supported-site behavior with synthetic prompt and memory data.

Any future change to the validated implementation requires this manual check to be repeated on the new final build.
