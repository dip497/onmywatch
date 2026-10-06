---
name: pyramids-audit-log
tags: [lets-build-pyramids]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, WebSearch, WebFetch]
---

We run a multi-tenant B2B SaaS on Postgres: about 400 tenants, the largest has 2 million records, and records are edited about 3 million times a day in total. Customers now want an audit log: every change to every record, who made it and when, searchable per record and per user, kept for 2 years, exportable for compliance.

Before we build it, how should we design this, and will it scale? There is no code to read; work from this description.
