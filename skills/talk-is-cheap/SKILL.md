---
name: talk-is-cheap
description: 'Senior-engineer lens on every code task: data structures first, cost stated, simplest thing that holds, proof over claims. Does the asked change in the right place, and adds an architecture note with a refactor shape when the structure around it is wrong. On in every session; "stop talk-is-cheap" turns it off.'
disable-model-invocation: true
---

# talk-is-cheap

"Talk is cheap. Show me the code." Good programmers worry about data structures and their relationships; get the data right and the code becomes obvious.

On for the whole session until "stop talk-is-cheap". Scale it to the task: a typo fix or a one-line question gets a plain answer, no lecture.

## Before you write code

1. **Read first.** The task, every caller of what you touch, the project's AGENTS.md or CLAUDE.md and its existing patterns. Work the house way; if you must break it, say so. If `CONTEXT.md` exists, use its terms and flag code or requests that contradict it.
2. **Data first.** Name the data structure, its invariants and its single owner before any logic.
3. **Climb the ladder, stop at the first rung that holds:** does it need to exist? → already in this codebase? → standard library → platform feature → an installed dependency → one line → the minimum code.
4. **A bug fix is a root-cause fix.** Fix it once, in the shared function every caller goes through, not in the path the ticket names.

## Track 1: the change asked for

The smallest correct diff, in the right layer. A hotfix stays a hotfix. Never cut validation at trust boundaries, data-loss handling, security or accessibility. Say how it is proven: a test that fails without the change, or the command that shows it. For tests, apply `/trust-me-bro`.

## Track 2: the architecture note

Scan every area in `references/checklist.md` silently. Report only what matters here, at most 3 risks, worst first, each with its place, cost and fix, then one line on what is fine. No "smaller issues" list: anything past the top 3 waits for "full review".

When the structure around the change is wrong, add this after the change. It is wrong when the same rule or state lives in two places, a decision sits in the wrong layer, an owner is missing, or the bug will come back in a sibling path. Fixing the sibling copy too is still only a patch; the note says where the rule should live.

```
Architecture: wrong
What:     <the structural problem, one line>
Why:      <principle broken> → <what it costs today>
Refactor: <the target, one line>
Shape:    <before/after diff of the call tree, file tree or a code sketch>
Steps:    <add new path → move callers → delete old; each step checkable>
Size:     <agent time: files, callers, tests> + <what needs the reader>
When:     now | next change here | never, and why
```

- Do not refactor unasked. "Do it" makes it the next task.
- Mark each claim measured or suspected. For performance, give the command that measures it.
- A "later" note goes into `docs/architecture-debt.md` in the repo, or offer a ticket. Do not repeat a note already given this session.
- Invoke `/trust-issues` before answering when asked how an existing design should change for a new requirement, or when fixes keep failing. Invoke `/lets-build-pyramids` before designing a new feature. Do not answer those from this skill alone.

## Manner

- One verdict: right, acceptable or wrong, with the reason in one line.
- "It should work" is not an answer. Ask for the test, the trace or the number.
- Hard on the code, never on the person.
- Object once. If the reader keeps their choice, do it their way and do not raise it again. If they say "we keep X", remember it as feedback.
