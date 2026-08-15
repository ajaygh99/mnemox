# Contrast and reflow validation

Validated candidate: `4b52bbe5cef644a9e326d5551f84963d4759e0de`

## Deterministic color calculations

WCAG relative-luminance calculations against popup/login background `#0d0d1a`:

| Foreground | Purpose | Ratio | Threshold | Result |
| --- | --- | ---: | ---: | --- |
| `#9ca3af` | secondary text | 7.59:1 | 4.5:1 | PASS |
| `#e5e7eb` | primary text | 15.57:1 | 4.5:1 | PASS |
| `#f87171` | error text | 6.97:1 | 4.5:1 | PASS |
| `#fbbf24` | focus indicator | 11.55:1 | 3:1 | PASS |

Status: **PASS for defined source color pairs; BLOCKED for rendered-state and 200% reflow observation.**

The popup includes a narrow-width reflow rule and all in-scope pages define visible focus indicators. Actual rendered colors, browser state variants, clipping, and two-dimensional scrolling must be observed in live Chrome using the manual validation guide before the full accessibility gate is marked passed.
