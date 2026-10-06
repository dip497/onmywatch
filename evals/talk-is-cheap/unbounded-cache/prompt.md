---
tags: [talk-is-cheap]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this function:

```python
_cache = {}

def get_user_profile(user_id, db):
    if user_id in _cache:
        return _cache[user_id]
    profile = db.load_profile(user_id)
    _cache[user_id] = profile
    return profile
```

It runs in a long-lived web server with about 2 million users.
