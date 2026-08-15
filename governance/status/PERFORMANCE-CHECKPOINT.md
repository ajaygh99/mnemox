# Phase 0 performance checkpoint

Status date: 2026-08-13

Authority: issue #24

Baseline: `origin/main` at `4087e046358eec22bc62e8bdf74fa11c575e6a9b`

## Decision

The performance tuning already present on `main` is accepted as a guarded
development baseline, not as production performance proof. Phase 1 remains
blocked by the existing governance queue and may not start from this checkpoint
alone.

The current suite proves that selected performance controls remain in source
and that the repository regression suite passes. It does not measure browser
startup, capture-to-submit latency, backend percentiles, throughput, memory or
CPU use, cache hit rate, extension resource consumption, or production behavior.

## Current controls

| Area | Implemented control | Guard | Checkpoint result |
|---|---|---|---|
| Backend I/O | Supabase calls are moved off the async event loop with `asyncio.to_thread`. | `tests/performance/test_performance_guards.py` | Present; static guard passed. |
| Health endpoint | Database and vector checks run concurrently with `asyncio.gather`. | Performance guard suite | Present; static guard passed. |
| Memory listing | List and count operations run concurrently. | Performance guard suite | Present; static guard passed. |
| Embeddings | In-memory embedding cache is bounded and evicts least-recently-used entries. | Performance guard suite | Present; static guard passed. |
| DOM observation | Mutation bursts are coalesced before submit-button discovery. | Performance guard suite | Present; static guard passed. |
| Semantic search | Remote search has a 250 ms abort budget and a local fallback path. | Performance guard suite | Present; static guard passed. |
| Prompt injection | Content processing has a 350 ms hard budget and 20 ms post-injection settle delay. | Performance guard suite | Present; static guard passed. |
| Dashboard filtering | Memory filtering is debounced by 100 ms. | Performance guard suite | Present; static guard passed. |
| Failure handling | Expected budget expiry is debug-level behavior rather than a false extension warning. | Performance guard suite | Present; static guard passed. |

## Validation snapshot

- Performance guards: **13 passed**.
- Governance suite: **16 passed**.
- Full repository suite: **440 passed**, 0 failed, 5 known warnings.
- No runtime or product file changed for this checkpoint.

These counts are reproducibility evidence for the exact candidate commit, not
latency or capacity measurements. Exact-SHA evidence is stored under
`evidence/PERFORMANCE-CHECKPOINT/<candidate-sha>/`.

## Gaps before Phase 1 performance claims

1. No repeatable benchmark harness or committed workload profile exists.
2. No percentile targets exist for capture, local search, remote search,
   injection, API endpoints, or dashboard rendering.
3. No cold/warm cache comparison or cache-hit instrumentation is recorded.
4. No browser CPU, memory, long-task, or extension startup baseline is recorded.
5. No backend concurrency, saturation, rate-limit, or failure-injection baseline
   is recorded.
6. No supported-device or network-condition matrix is recorded.
7. CI checks source invariants and regressions but does not detect performance
   regression statistically.

## Phase 1 entry checkpoint

This checkpoint adds no new permission to enter Phase 1. Before Phase 1 is
activated:

1. B-09, B-10, and B-08 must complete in the established order.
2. The owner must approve a separate Phase 0 exit decision.
3. The Phase 1 contract must name the performance-sensitive user journey,
   environment, workload, measurement method, percentile targets, resource
   ceilings, regression tolerance, and rollback trigger.
4. Any claim about real latency, throughput, memory, CPU, browser behavior, or
   production performance must be supported by measured evidence from that
   contract; these static guards are insufficient.

## Rollback

Revert the checkpoint documentation and evidence commits. There is no runtime
behavior to roll back.
