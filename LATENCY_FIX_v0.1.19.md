# Mnemox v0.1.19 Prompt Latency Fix

## Root cause

Earlier versions canceled the AI site's native submit event and waited for
memory retrieval before sending. A slow backend or an unresponsive service
worker could therefore delay the prompt indefinitely. Version 0.1.18 limited
the backend request to 2.5 seconds, but that was still perceptible.

## New latency contract

| Stage | v0.1.17 | v0.1.18 | v0.1.19 |
|---|---:|---:|---:|
| Remote search limit | Unlimited | 2,500 ms | 250 ms |
| Content-script watchdog | None | None | 350 ms |
| Post-lookup settle delay | 120 ms | 120 ms | 20 ms |
| Worst extension wait before submit | Unbounded | About 2,620 ms | About 370 ms |

If semantic retrieval finishes inside the budget, relevant memories are still
injected. If it does not, Mnemox immediately uses its local fallback or sends
the original prompt. A late callback is ignored so it cannot modify or resend
an already released prompt.

## Compatibility

- Capture remains enabled and asynchronous.
- Local keyword fallback remains available.
- Backend semantic injection is retained when it responds within budget.
- APIs, authentication, storage formats, and supported AI sites are unchanged.

## Verification

- 387 automated tests passed.
- 0 failures and 0 errors.
- JavaScript syntax validation passed for the content script and service worker.
