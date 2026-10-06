## User

The incident write-up says the outage was a "cache stampede". What does that mean?

## Assistant

A cache stampede is a thundering-herd failure mode: when a hot key's TTL expires, N concurrent readers miss simultaneously and all fan out to the origin to recompute the value, so origin QPS spikes by roughly the concurrency factor and saturates the connection pool. Standard mitigations are request coalescing (singleflight), probabilistic early expiration (XFetch), jittered TTLs and stale-while-revalidate.
