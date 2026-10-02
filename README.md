# jobqueue

A Redis-backed job queue in Python with retries and dead letters

> 🚧 **Status: planning** — architecture and README first, code next.

## Why

Background jobs are where reliability goes to die. jobqueue is a small, well-tested queue library: at-least-once delivery, exponential backoff, dead-letter queues, and graceful worker shutdown.

## Planned features

- enqueue/dequeue with at-least-once semantics
- Retries with exponential backoff + jitter
- Dead-letter queue with manual replay tool
- Graceful shutdown: finish in-flight jobs, reject new ones
- Full pytest suite with fakeredis (no Redis needed for tests)

## Stack

`python` `redis` `pytest`

## Notes

Idempotency is the caller's job — document it loudly.

## License

MIT, see [LICENSE](LICENSE).

---
maintained · verified 2026-09-30
---
maintained · verified 2026-10-01
---
maintained · verified 2026-10-02
