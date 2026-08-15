# Accessibility remediation log

Authority: Issue #32  
Validated candidate: `4b52bbe5cef644a9e326d5551f84963d4759e0de`  
Baseline: `7636da2450727d6f162da0d3d458c23eec817fa8`

## Implemented

- Associated popup switch names and descriptions with their checkboxes while keeping the inputs keyboard focusable.
- Associated every login/signup label with its input and replaced clickable navigation spans with native buttons.
- Added visible high-contrast focus indicators.
- Added alert/status live-region semantics for errors, memory count, site state, dashboard state, and content-free toasts.
- Added dialog description, initial focus, Tab/Shift+Tab containment, Escape cancellation, and prompt focus restoration to injection review.
- Replaced dashboard `div` toggles with native buttons exposing `role="switch"` and `aria-checked`.
- Associated dashboard settings labels/hints and named search controls.
- Raised audited secondary text colors and added a narrow-width popup reflow rule.
- Kept dashboard capture/injection switches disabled until a valid consent receipt exists.

No extension permission, deployment, publication, telemetry, privacy-policy, Issue #21, or Phase 1 state changed.
