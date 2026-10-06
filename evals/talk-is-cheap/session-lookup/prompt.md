---
tags: [talk-is-cheap]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

We keep logged-in user sessions in a Python list and loop over it to find the session for each request by session id. Sessions expire after 30 minutes. We have about 50,000 active sessions at peak. Is this fine?
