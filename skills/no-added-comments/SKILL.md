---
name: no-added-comments
description: Use whenever you write or change code. Keeps the diff free of comments you added and leaves existing comments as they were.
---

# no-added-comments

When you change code, do not add comments.

- No explanations of why a line exists.
- No section separators in tests.
- No notes inside assertions that restate the reason for the check.
- No edits to existing comments or doc blocks. Leave their wording as it was.

Put the reasoning in your reply to the user, not in the diff.

Touch an existing comment only when the code it describes is removed.

If a constraint really must be recorded, prefer a name, a type or a test that enforces it over a comment that describes it.
