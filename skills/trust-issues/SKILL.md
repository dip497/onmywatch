---
name: trust-issues
description: "First-principles redesign. Apply when a new requirement does not fit the current design, when two or more fixes built on the same assumption have failed, when a design keeps growing special cases, or when asked to rethink or redesign. Separate what must be true from what is only inherited, then rebuild the design from what must be true."
---

# trust-issues

Reason from what must be true, not from what already exists.

**Why:** An existing design carries the assumptions of the day it was built. Patching it keeps those assumptions, even after they stop being true. Each patch makes the next one harder, and the design ends up held together by special cases.

## When to apply

- A new requirement only fits through a flag, a special case or a second code path.
- Two or more fixes have failed and they share one assumption.
- The same kind of bug keeps coming back in different places.
- You are asked to rethink, redesign or "do it properly".

Do not apply it to a small, local change that the current design already handles cleanly.

## Pattern

1. **State the goal as an outcome.** One sentence about what the user or caller needs to be true, not the feature or the code. "A support agent sees every open ticket assigned to them" is a goal. "Add a filter to the list endpoint" is a solution.

2. **List the assumptions.** Write down everything the current design takes for granted: data shapes, who owns what, ordering, limits, "this is always called once", "there is one tenant". Read every file and doc the design touches, whole, so the list is complete.

3. **Sort each assumption.** Put each one in exactly one bucket:
   - **Fact:** true no matter how you build it. Physics, the data that exists, a hard limit you measured.
   - **Owned elsewhere:** a contract, API or rule another team or system owns. Treat it as fixed for this design, and name who could change it.
   - **Choice:** someone decided it, and it could be decided again.
   - **Habit:** nobody decided it; it is only how it was done before.

   An assumption is a fact only if you can show the evidence: the code, the data, the doc, a measurement. If you cannot, it is a choice.

   **Before you drop a choice or habit, find out why it exists** (Chesterton's fence): `git log -S`, `git blame`, the PR or ticket, a comment. Cite what you find. If the reason still holds, it is a fact. If you find no reason, say so. Dropping a choice is a decision: list the drops for the user to confirm, do not drop them silently.

4. **Attack the premise.** If fixes have failed, write the one assumption they all shared as one sentence. Test it with a check you can rerun (a query, a script, a log count) before you write another fix. If it is false, stop fixing and redesign. If it holds, the premise is not the cause: look elsewhere and keep the check as evidence. Remove the cause instead of compensating for it.

5. **Rebuild from the facts.** Ask: "Knowing only the goal and the facts, what is the simplest design that works?"
   - Start from the data shape and who owns it. Logic follows from that.
   - Put each decision in the lowest layer that owns it.
   - Sketch two or three designs that differ in data shape or ownership. A variant of the same shape is not an alternative. Pick one and say in one line why each other lost.
   - If the redesign needs scale numbers or research, hand that part to `/lets-build-pyramids`.

6. **Compare with what exists.** Keep every part of the current design that already matches the new one. A first-principles design is not a rewrite by default; often it shows that most of the code is right and one assumption is wrong.

7. **Land it like the Ship of Theseus: part by part, the system running the whole time.** No big-bang rewrite. Delete what the new design makes dead before you build on top. Then order the change into small steps that can each be verified on their own. Carry it through every reference: types, callers, tests, docs. Remove the old path in the same change, not "later".

## Output

Before writing code, show the reader:

| Section | Content |
|---|---|
| Goal | One sentence. |
| Done when | A check that could prove the redesign failed. |
| Facts | Each with its evidence. |
| Dropped | Each choice or habit you are removing, where it came from, and why it no longer holds. For the user to confirm. |
| Design | The chosen design, and why the others lost. |
| Steps | Numbered, each with how it will be checked. |

Once the user agrees, record the decision and each dropped choice as an ADR with `/domain-modeling` (Matt Pocock's skill), so the next person who asks "why is it like this?" finds the answer instead of digging through history.

## Stop

- Do not write code before the facts and the dropped assumptions are written down.
- Do not call something a fact without evidence.
- If every assumption turns out to be a fact, the current design is right. Say so and make the small change instead.
