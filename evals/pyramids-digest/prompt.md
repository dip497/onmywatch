---
name: pyramids-digest
tags: [lets-build-pyramids]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, WebSearch, WebFetch]
---

Our app has 50,000 users across many time zones. We want to add a daily digest email: each user gets one email at 8am their local time summarising the notifications they missed, and each user can choose which notification types go into it.

Before we build it, what is the right architecture, and what breaks at 10x? There is no code to read; work from this description.
