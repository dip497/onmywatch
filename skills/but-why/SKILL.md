---
name: but-why
description: "First-principles redesign. Apply when a new requirement does not fit the current design, when two or more fixes built on the same assumption have failed, when a design keeps growing special cases, or when asked to rethink or redesign. Separate what must be true from what is only inherited, then rebuild the design from what must be true."
---

# but-why

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
   - **Fact:** true no matter how you build it. Physics, the data that exists, a contract another system owns, a hard limit you measured.
   - **Choice:** someone decided it, and it could be decided again.
   - **Habit:** nobody decided it; it is only how it was done before.

   An assumption is a fact only if you can show the evidence: the code, the data, the doc, a measurement. If you cannot, it is a choice.

4. **Attack the premise.** If fixes have failed, write the one assumption they all shared. Test it against real data before you write another fix. If it is false, stop fixing and redesign.

5. **Rebuild from the facts.** Ask: "Knowing only the goal and the facts, what is the simplest design that works?"
   - Start from the data shape and who owns it. Logic follows from that.
   - Put each decision in the lowest layer that owns it.
   - Sketch two or three designs. Pick one and say in one line why each other lost.

6. **Compare with what exists.** Keep every part of the current design that already matches the new one. A first-principles design is not a rewrite by default; often it shows that most of the code is right and one assumption is wrong.

7. **Land it in steps.** Order the change into small steps that can each be verified on their own. Carry it through every reference: types, callers, tests, docs. Remove the old path in the same change, not "later".

## Output

Before writing code, show the reader:

| Section | Content |
|---|---|
| Goal | One sentence. |
| Facts | Each with its evidence. |
| Dropped | Each choice or habit you are removing, and why. |
| Design | The chosen design, and why the others lost. |
| Steps | Numbered, each with how it will be checked. |

## Stop

- Do not write code before the facts and the dropped assumptions are written down.
- Do not call something a fact without evidence.
- If every assumption turns out to be a fact, the current design is right. Say so and make the small change instead.
