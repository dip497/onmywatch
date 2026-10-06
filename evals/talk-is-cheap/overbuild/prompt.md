---
tags: [talk-is-cheap]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Internal leave-request tool for our 200-person company. My plan: 6 microservices (users, requests, approvals, notifications, audit, reporting), Kafka between them, each with its own Postgres, on Kubernetes. Review the architecture.
