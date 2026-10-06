---
name: lets-build-pyramids
description: "Design and scalability check for a feature. Apply before building or approving a feature, an endpoint, a job, a cache or a data model, and when asked 'will this scale', 'is this designed well' or 'what breaks at 10x'. Forces a pass over design principles and growth limits before code."
---

# lets-build-pyramids

Build it like a pyramid: base first, sized for the weight it will carry, still standing when it grows.

**Why:** Most features work on day one with ten rows and one user. They break later at a size nobody checked, in a place that is now expensive to change.

## 1. Design

Answer each in one line. "Not sure" is an answer; go and find out.

| Principle | Question |
|---|---|
| One owner | Which single module or service owns this data and this decision? |
| Right layer | Is each decision in the lowest layer that owns it, not spread across callers? |
| Data first | Is the data shape right for the main read and write paths? |
| Boundaries | Are inputs checked once, at the edge? Do errors reach the caller with a next step? |
| Reuse | Does a helper, library or platform feature already do this? |
| Simple | Is there anything here with a single use: a class, a flag, a layer? Remove it. |
| Safe to repeat | If it runs twice, crashes halfway or is retried, does it end in the same state? |
| Concurrency | What happens if two actors change the same thing at once? |
| Lifecycle | Everything it opens, caches or spawns: who closes it, and when? |
| Reversible | Can it be turned off or rolled back without a data fix? |

## 2. Scale

Take the real numbers today, then ask what happens at 10x and 100x.

| Axis | Question |
|---|---|
| Data | Rows, documents, file size. Does any path read all of it? |
| Traffic | Requests per second, concurrent users, peak versus average. |
| Tenants | Does one large tenant slow down the others? |
| Hot path | Calls per request: queries, network, model calls. Any N+1? |
| Memory | Does anything grow without a bound: caches, queues, sessions, lists? |
| Limits | Timeouts, rate limits, pool sizes, payload caps. Which one is hit first? |
| Cost | Money per request or per run, at 100x. |
| Failure | When a dependency is slow or down, does this fail fast or pile up? |

For each axis, name the first thing that breaks and roughly at what size. If you cannot estimate, measure or say so.

## 3. Verdict

Show this before writing code:

| Section | Content |
|---|---|
| Fine as is | Points that hold at 100x. |
| Fix now | Problems that are cheap now and expensive later. Each with the fix. |
| Fix later | Problems with a known ceiling. Each with the size where it bites and the upgrade path. |
| Unknown | What you could not check, and how to check it. |

## Stop

- Do not over-build for scale nobody needs. A known ceiling written down beats a premature system.
- Do not mark a point fine without a reason or a number.
- If the design itself is wrong, switch to `/but-why`.
