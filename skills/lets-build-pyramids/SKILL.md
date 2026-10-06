---
name: lets-build-pyramids
description: "Architecture review for a feature before it is built. Apply when planning or approving a feature, service, endpoint, job, cache or data model, and when asked 'will this scale', 'how should we design this', 'is this the right architecture' or 'what breaks at 10x'. Researches how others solved it, compares real alternatives with numbers, and stress-tests the choice."
---

# lets-build-pyramids

A pyramid is designed from the base, sized for the weight it will carry, and still standing 4,500 years later. Design features the same way.

A checklist filled in from memory is not a design review. This skill is research and thinking first; the answer comes last.

## 1. Ground it

Find out what is really there before you reason about it.

- Read the code, schema and docs the feature touches, whole. Note the patterns this codebase already uses for the same kind of problem.
- Get the real numbers: rows, users, tenants, requests per second, payload sizes, growth per month. Query or measure them. If you cannot, ask for them once, and state the assumption you use meanwhile.
- Write the goal in one sentence as an outcome, and the hard constraints.

## 2. Research how others solved it

Most features are a known problem in disguise: a queue, a fan-out, a counter, an audit trail, a sync, a search, a rate limit.

- Name the known problem this is.
- Look up how mature systems and well-known engineering write-ups solve it, and what the libraries or platforms in this stack already offer. Search the web and the official docs; do not rely on memory.
- Cite each source in one line: what it does and what it teaches here.

## 3. Look at it from every side

Walk the feature through each view and write what that person would worry about:

| View | Asks |
|---|---|
| User | What do they feel when it is slow, wrong or down? |
| Data | Who owns it, how it grows, what must stay consistent, what can be stale. |
| Operator at 3am | How it fails, how you notice, how you recover, what a retry does. |
| Security and tenants | Who can see what; can one tenant hurt another? |
| Cost | Money per request or per run, today and at 100x. |
| Next year | The three requirements most likely to come next. Does this design bend or break for them? |

## 4. Design real alternatives

Sketch at least three designs that differ in architecture, not in detail. Include the most boring one that could work and one bolder one.

For each: a small diagram (ASCII or Mermaid), how data flows, and where it first breaks.

Then compare them in a scale table: one row per design, columns for today, 10x and 100x. In each cell put the number that limits that design (storage, writes per second, latency, memory or cost) and whether it still holds. Under the table, show the arithmetic for each number. A table that stops at today's size is not a comparison.

## 5. Pre-mortem the winner

Pick the design. Then assume it is a year later and it failed badly. Write the three most likely reasons. Change the design for each one, or write it down as a known ceiling with the size where it bites and the upgrade path.

## 6. Report

This report is a walkthrough the reader asked for. Give every section below in full, even when a brevity style is active; lead with the verdict, then the sections.

| Section | Content |
|---|---|
| Problem | Goal, constraints, real numbers, and which known problem this is. |
| What others do | Sources and what each teaches. |
| Options | The designs, diagrams and the scale table at today, 10x and 100x. |
| Choice | The winner, why each other lost, and what was surprising. |
| Pre-mortem | The failure reasons and what you changed. |
| Build order | Numbered steps, foundation first, each with how it is checked. |
| Unknown | What you could not check, and how to check it. |

## Quality bar

- At least one insight the reader would not have reached alone. If the review only confirms the first idea, dig further.
- Every number has its source or its arithmetic.
- Do not build for scale nobody needs; a written ceiling beats a premature system.
- If the requirement itself looks wrong, switch to `/trust-issues`.
