# jobqueue

A planned Python job queue focused on explicit delivery and retry semantics.

> **Status: design stage.** This repository currently contains documentation only; there is no queue implementation or Redis integration yet.

## Goal

Explore reliable background work with a small API and clearly documented failure behavior.

## Proposed contract

- Jobs have a stable identifier, payload, attempt count, and creation timestamp.
- A worker acknowledges a job only after its handler succeeds.
- A failed job is retried according to a configurable policy.
- Jobs that exceed the retry limit are moved to a dead-letter collection for inspection.
- Shutdown stops new work and gives in-flight handlers a bounded time to finish.

## Important semantics

- Delivery is intended to be **at least once**, so a handler may run more than once.
- Applications must make side effects idempotent or deduplicate by job ID.
- Retry delays should use bounded exponential backoff with jitter.
- The API must distinguish handler failures from queue/storage failures.
- Redis behavior, persistence guarantees, and concurrency limits must be specified before claiming production readiness.

## Planned milestones

- [ ] Implement a pure in-memory queue contract and tests.
- [ ] Add retry policy tests with an injectable clock/random source.
- [ ] Define shutdown and in-flight job behavior.
- [ ] Add a Redis backend with integration tests.
- [ ] Document observability and dead-letter replay safeguards.

## Testing

Core tests should run without a live Redis server. Backend integration tests can use an isolated test instance and should be clearly separated from unit tests.

## License

MIT. See [LICENSE](LICENSE).
