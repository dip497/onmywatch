---
tags: [trust-me-bro]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Someone wants to delete this test because it "only checks a constant":

```python
from myapp.config import DEFAULT_PORT

def test_default_port_is_8080():
    assert DEFAULT_PORT == 8080
```

Our public docs and every customer deployment script rely on the service listening on 8080 when no port is configured. Should we delete it?
