# Mnemox v0.1.21 Extension Context Fix

## Root cause

Reloading or updating an unpacked Chrome extension invalidates content scripts
already running in open AI tabs. The popup can show the new version while an
open Claude, Gemini, ChatGPT, or Copilot tab still runs the previous script.
That stale script cannot contact the new service worker, causing both missing
captures and `Extension context invalidated` errors.

The screenshot confirmed this mixed state: the popup showed v0.1.20 while the
page console still emitted the candidate-button diagnostic removed in v0.1.20.

## Fix

- Centralized content-script communication in `safeSendMessage`.
- Catches both synchronous throws and callback runtime errors.
- Converts extension reload invalidation into an informational refresh notice.
- Shows an in-page toast asking the user to refresh the AI tab.
- Clears the capture deduplication state when delivery fails.
- Downgrades expected injection-budget expiration to debug output.

## Important Chrome lifecycle behavior

The first refresh after installing or reloading an unpacked extension remains
required by Chrome. No content script can reconnect after its extension context
has already been destroyed. Version 0.1.21 makes this state safe and explicit.

## Verification

- 390 automated tests passed.
- JavaScript syntax validation passed.
- Capture, injection, dashboard storage, and latency limits remain unchanged.
