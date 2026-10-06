---
tags: [trust-issues]
max_turns: 6
allowed_tools: [Skill, Read, Glob, Grep]
---

Our payment webhook handler keeps creating duplicate orders. We tried three fixes and each one failed: (1) a Redis key set on each webhook id with a 60 s TTL, (2) a unique index on a hash of the request body, (3) a 2 second sleep before inserting. Duplicates still appear about 30 times a day. The provider retries webhooks for up to 3 days and re-signs each retry, which changes a timestamp field in the body. Rethink this properly before we try a fourth fix.
