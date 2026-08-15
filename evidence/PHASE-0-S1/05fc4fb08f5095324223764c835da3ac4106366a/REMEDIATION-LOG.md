# Phase 0 Severity-1 remediation log

Authority: Issue #30  
Validated candidate: `05fc4fb08f5095324223764c835da3ac4106366a`  
Baseline: `fec90b50c3d6adf39ec89c5e2cb304e5274fdc8f`

## Changes

1. Fresh installs now default capture and injection off and store no consent receipt.
2. The popup explains capture and reviewed injection, requires an explicit checkbox and enable action, and stores a versioned UTC consent receipt.
3. Withdrawing consent atomically clears the receipt and disables capture and injection.
4. The service worker rejects feature enablement without valid consent and accepts settings changes only from the extension popup.
5. Both keyboard and send-button injection paths show an accessible review dialog before prompt mutation or submission.
6. The review dialog permits editing proposed context, approving it, sending without memories, or returning without sending.
7. Capture and injection fail closed without consent in both content and service-worker boundaries.
8. Prompt excerpts, DOM dumps, memory content, and capture previews were removed from console and toast diagnostics.
9. Existing stored memories and settings remain preserved during install/update; missing safe defaults are added only when absent.

## Boundary

This change provides implementation and deterministic source-test evidence. It does not claim live-browser accessibility, Chrome Web Store publication, deployment, privacy-policy approval, or production validation. Those gates remain separate Phase 0 work.
