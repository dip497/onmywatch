# Checklist

Scan all areas. Report at most the 3 that matter for this change. Areas follow ISO/IEC 25010, plus the items developers most often forget.

## Areas

| Area | Look for | Usual fix |
|---|---|---|
| Data structures | A list searched by key; two copies of the same state; no clear owner; invariants nobody enforces | Map or set keyed by the lookup; one owner; make illegal states unrepresentable in the type |
| Performance | O(n²) on a growing input; N+1 queries; work inside a hot loop; sync I/O on a request path; needless copies | Index or batch; move work out of the loop; async or a queue; measure before and after |
| Memory | Unbounded cache, list, queue or map; whole file or result set held in memory; listeners never removed | A bound and an eviction rule; stream or paginate; remove on close |
| Resources | Connections, files, sessions, processes or timers opened without an owner that closes them | One owner; `with` / `try-finally` / `defer`; close on every path |
| Concurrency | Shared mutable state; check-then-act; lock order; a retry that runs the work twice | Isolate, or one writer; atomic operation; idempotency key |
| Errors | Swallowed exceptions; empty result standing in for failure; no timeout; retry with no backoff or limit | Fail loudly with a next step; timeout every call out; bounded retry with backoff |
| Readability | Vague names; functions doing two things; nesting over 3 levels; clever code off the hot path | Name by meaning; split; early return; plain code |
| Maintainability | Duplication of a rule; one-use abstraction; dead code; hidden side effects; coupling across layers | One home per rule; inline the abstraction; delete; pass dependencies in |
| Patterns | A pattern with nothing to solve: factory for one product, interface with one implementation, singleton holding state, strategy with one strategy | Plain function or direct call. Name a pattern only when it removes a real problem |
| Security | Injection (SQL, shell, path); secrets in code or logs; unchecked input at a trust boundary; missing access check | Parameterise; secrets from config, masked in logs; validate at the edge; check access in the owner |
| Reliability | No input size limit; partial failure leaves half-written state; data-loss path | Limits; transaction or write-then-rename; make the operation idempotent |
| Observability | A failure you could not explain at 3am: no log, no context, no metric | Log the decision with ids; error carries context; one metric on the hot path |
| Compatibility | API or schema change with old clients or data still around; migration with no way back | Additive change first; migrate callers, then delete; reversible migration |

## Often forgotten

- Time: time zones, daylight saving, clock skew, "now" read twice.
- Text: Unicode, encoding, case folding, trimming.
- Edges: empty input, one item, huge input, duplicates, off-by-one.
- Lists: pagination, ordering that is not stable.
- Money as float; rounding.
- Cache invalidation; stale reads after a write.
- Cost per request at 100x.
- A new dependency for what a few lines do.

## Data structure choice

| Need | Use | Cost |
|---|---|---|
| Find by key | Hash map | O(1) get, put, delete |
| Membership, dedupe | Hash set | O(1) |
| Ordered by key, range queries | Sorted tree / B-tree index | O(log n) |
| Smallest or largest next (scheduling, expiry) | Heap / priority queue | O(log n) push, pop |
| FIFO work | Queue / deque | O(1) both ends |
| Recent N, bounded cache | LRU (map + linked list) | O(1) |
| Counts | Map to int, or counter | O(1) |
| Relations, dependencies | Adjacency map; topological sort | O(V + E) |
| Prefix search | Trie, or a sorted list + binary search | O(k), O(log n) |

## Measure, do not guess

Before claiming slow or heavy: name the input size, then profile or benchmark (`time`, `cProfile`, `py-spy`, `perf`, a benchmark test, `EXPLAIN ANALYZE`). Mark a claim without a measurement as suspected.
