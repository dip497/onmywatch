---
type: llm
weight: 2
---
The reply says the list is the wrong structure, recommends a hash map (dict) keyed by session id, and handles expiry in a way that works (a check on read plus a periodic sweep, a heap or other time-ordered structure, or a TTL store such as Redis expiry).
