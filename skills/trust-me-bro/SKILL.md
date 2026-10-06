---
name: trust-me-bro
description: "Use whenever writing, changing, reviewing or cleaning up tests, and when a fix needs proof. A test must guard behaviour against a real bug, not mirror the code. Gates every new test, rejects tests that prove nothing, and audits existing ones."
---

# trust-me-bro

A test that cannot fail for a real bug is a "trust me bro" test: it costs CI time and review and proves nothing. Calling a method and checking it returns what it returns is not a test.

## Before you write a test

Answer all four. A missing answer means do not write it yet.

1. **What does it protect?** An observable behaviour, an invariant, or a contract someone relies on.
2. **What real bug makes it fail?** Name it.
3. **Why does no existing test catch that bug?** One contract has one main test, at the strongest boundary. Extend a table-driven case before adding a near-copy.
4. **Does it need a test-only hook in production code** (an export, flag or wrapper no real caller uses)? Then test at the real boundary instead.

Then two checks:

- **The refactor test.** Would it break if the code were restructured without changing behaviour? Then it tests implementation. Rewrite it at the boundary users call.
- **The undefined test.** Would it still pass if every function it imports returned `undefined`? Then it observes nothing.

## Write it like this

Call the subject the way its users do, with one concrete input, and assert the literal result or the observable effect:

```python
assert slugify("Hello, World!") == "hello-world"
```

- An absence: in the same test, assert the presence on the other input.
- A mock: assert the payload it received or the state after the call, not only that it was called.
- A constant: test the code that reads it, with one input. Do not restate the value.
- Edges that break real code: empty, one, many, duplicates, boundary values, bad input, time zones, Unicode.

## Regression tests

A bug's regression test must **fail on the old code for the bug's reason**, then pass after the fix. Show both runs, or say you could not. A regression test that never failed proves the mock, not the fix. One regression test, at the owner of the bug, covers it; do not repeat it at every layer.

## Tests that prove nothing

Reject a new one and flag an existing one that is:

- assertion-free, or asserts only `toBeDefined`, `toBeTruthy`, `not.toThrow`, `isinstance`, `> 0`;
- only "was called" or "was not called";
- self-referential: the expected value comes from the code under test;
- a fixture asserting the fixture: the subject never runs in the body;
- a constant pin restating a config value or prompt string;
- a mock that does the work being asserted;
- a source or string grep where a behaviour check is possible;
- a near-copy of a stronger test;
- named for more than it checks.

## Keep

Keep a test that guards a public API, protocol, config, migration, storage, security or platform contract; order when order is observable; a real regression. A test that looks implementation-shaped may still be the only guard of a contract: prove otherwise before you delete it. Slow or static is not a reason to delete.

## Audit existing tests

When asked to review or clean up tests: read the whole test, the code it covers and its other tests first. For each candidate, record what bug it can catch, what stronger test remains, and the command that checks the change. Prefer a few certain removals over many guesses. Delete test-only hooks and dead code freed by the removal.

## Report

For each test written or judged: what it protects, the bug it catches, and the run that shows it failing then passing. For an audit: removed, kept and why, and the commands run.
