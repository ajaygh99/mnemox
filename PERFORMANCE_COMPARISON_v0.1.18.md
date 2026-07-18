# Mnemox v0.1.18 Performance Comparison

## Baseline

- Source version: 0.1.17
- Source commit: `0e47f864a1185535ed39851f3720d05ed03141d0`
- Existing suite: 377 passing tests
- Original repository: `C:\Users\ajjuk\Documents\Cowork\mnemox\mnemox`
- Optimized copy: `C:\Users\ajjuk\Documents\Cowork\mnemox\Codex_Mnemox`

## Changes

| Area | v0.1.17 | v0.1.18 |
|---|---|---|
| Page observation | Full prompt lookup after every DOM mutation | Mutation bursts coalesced into one lookup every 50 ms and ignored when no nodes were added |
| Backend search | Could wait indefinitely on a slow backend | Aborted after 2.5 seconds and falls back to local search |
| Dashboard filtering | Full list filtering/rendering on every keystroke | Keystrokes debounced by 100 ms |
| Supabase access | Synchronous SDK calls executed on FastAPI's event loop | Blocking calls run in worker threads |
| Health endpoint | Supabase and Qdrant checked sequentially | Both checks run concurrently |
| Memory listing | Page query and total count run sequentially | Both database operations run concurrently |
| Embedding cache | Unbounded process memory growth | LRU eviction capped at 512 vectors |

## Compatibility

- Public API routes and response models are unchanged.
- Chrome storage keys and memory data formats are unchanged.
- Capture, semantic injection, anonymous mode, authentication, billing, teams, and dashboard behavior are unchanged.
- Slow or unavailable backend searches continue through the existing local fallback.

## Verification

- Baseline: 377/377 tests passed.
- Optimized release: 385/385 tests passed in 2.40 seconds.
- Added checks: 8 performance regression guards.
- Failures: 0.
- Packaged manifest: version 0.1.18 at the ZIP root.
- Package entries: 13.
