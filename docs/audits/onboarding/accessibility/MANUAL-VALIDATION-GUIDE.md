# Accessibility manual validation guide

Use an unpacked Chrome build created from the exact candidate SHA. Use synthetic accounts, prompts, and memories only.

## Keyboard

1. Open the popup with capture and injection disabled.
2. Tab through consent, capture/injection switches, account actions, and memory actions. Record focus order and visible focus.
3. Open sign in. Operate sign-in/sign-up switching and continue-without-account using only Tab, Shift+Tab, Enter, and Space.
4. Trigger an injection preview with synthetic memories. Confirm focus starts in the context editor, Tab and Shift+Tab remain in the dialog, Escape returns to the prompt without sending, and each decision button works without a pointer.
5. At 200% browser zoom, repeat required actions and record clipping or two-dimensional scrolling.

## Screen reader

With NVDA on Windows, record the announced name, role, state, and description for:

- consent checkbox and action;
- capture and injection switches;
- login and signup fields and navigation buttons;
- errors and confirmation status;
- memory count and site status;
- injection dialog, editable context, approve, send-without, and return controls;
- generic content-free capture/injection toast.

## Contrast

Measure rendered foreground/background pairs and focus indicators using browser developer tools or an approved contrast analyzer. Record the measured colors and ratio. Normal text requires at least 4.5:1; large text and non-text focus indicators require at least 3:1.

Do not mark any check passed from source inspection alone. Record tool/browser/assistive-technology versions, exact candidate SHA, observed result, and any defect.
