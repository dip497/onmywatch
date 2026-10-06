#!/usr/bin/env bash
set -e
mkdir -p sync docs
cat > sync/job.py <<'P'
import time


def sync_contacts(client, store, contacts):
    for c in contacts:
        if c.get("email") is None:
            continue
        if c["source"] == "legacy":
            c["email"] = c["email"].lower()
        if c["source"] == "partner_b":
            time.sleep(1.1)
        if c.get("deleted"):
            store.delete(c["id"])
            continue
        store.upsert(c)
        client.push(c)
P
cat > docs/incidents.md <<'P'
# Incidents

## 2025-03-14 partner_b account suspended
Partner B allows at most 1 request per second per API key. Our sync burst 300 requests and Partner B suspended our key for 48 hours. Fix: wait 1.1 s between partner_b pushes. Do not remove until we have a per-key rate limiter.
P
