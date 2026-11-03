# jobqueue

A Python job queue prototype focused on explicit delivery and retry semantics.

> **Current state: in-memory queue prototype.** A standard-library in-memory implementation now exercises stable job IDs, at-least-once delivery, bounded leases, retries, and dead-letter transitions. Redis integration, persistence, and worker processes are not implemented.

## First delivery contract

- Jobs retain the same ID across retries; duplicate IDs are rejected while retained in the queue.
- A worker receives a lease token when it claims a job.
- Acknowledgements and failures are accepted only from the current, unexpired lease holder.
- Expired leases can be claimed by another worker; stale workers cannot acknowledge afterward.
- A failed final attempt moves to the dead-letter state.
- Time is supplied by the caller, allowing deterministic tests without sleeps.

Run the focused tests with:

    python -m unittest discover -s tests -v

## Important limitation

Delivery is at least once. A handler can complete an external side effect and crash before acknowledgement, so the queue cannot guarantee exactly-once effects. Use the stable job ID as a downstream idempotency key where supported. This prototype is in-memory only and loses all state on process exit.

## Remaining work

- [ ] Add bounded exponential retry backoff with jitter.
- [ ] Define worker shutdown and in-flight handler behavior.
- [ ] Add a Redis backend with integration tests.
- [ ] Add metrics with bounded label cardinality.
- [ ] Document safe dead-letter inspection and replay.

## License

MIT. See [LICENSE](LICENSE).
