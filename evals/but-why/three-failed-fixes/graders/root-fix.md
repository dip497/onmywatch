---
type: llm
weight: 1
---
The proposed design dedupes on the provider's stable event id (or an idempotency key) with a durable unique constraint, instead of another time-window or body-hash patch.
