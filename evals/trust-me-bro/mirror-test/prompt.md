---
tags: [trust-me-bro]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Is this a good test? Improve it if not.

```python
from pricing import apply_discount

def test_apply_discount():
    result = apply_discount(200, 10)
    assert result == apply_discount(200, 10)
    assert result is not None
```

`apply_discount(price, percent)` returns the price after a percentage discount, capped at 50%.
