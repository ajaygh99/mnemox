# Mnemox v0.1.20 Console Warning Fix

## Cause

Claude and Gemini commonly render no Send button while the prompt is empty.
Mnemox checked for that button during initial prompt wiring and recorded the
normal absent state with `console.warn`. Chrome then displayed those warnings
on the extension's Errors page even though submission still had a fallback.

## Fix

- Replaced per-button startup wiring with one capture-phase delegated click
  listener on the document.
- Dynamic Send buttons are recognized when they are actually clicked.
- Removed the startup warning and candidate-button diagnostic dump.
- Retained the synthetic Enter fallback when no selector matches after an
  injection attempt.
- Downgraded that successful fallback notice to debug output so it does not
  appear as an extension failure.

## Verification

- 388 automated tests passed.
- JavaScript syntax validation passed.
- Prompt capture, injection, latency budget, and synthetic fallback remain enabled.
