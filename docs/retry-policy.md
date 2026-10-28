# Retry and dead-letter policy (proposed)

This document defines predictable retry behavior for a future jobqueue implementation. The queue remains design-stage.

## Attempt contract

- A job handler is acknowledged only after it returns success.
- Handler failure increments the attempt count; storage/queue failures are reported separately and must not be misclassified as handler failures.
- Delivery is at least once. A handler may run more than once, so side effects should be idempotent or deduplicated by job ID.
- After the configured maximum number of attempts, move the job to a dead-letter collection with its last error and timestamps. Do not retry indefinitely.

## Attempt numbering

Attempt 1 is the first handler invocation; `max_attempts` includes that initial attempt rather than counting retries only. A value of 1 therefore means no retry after the first failure. Persist the attempt count alongside the job so a worker restart cannot reset the retry budget. Tests should cover `max_attempts = 1`, the final allowed retry, and dead-letter transfer immediately after the final failed attempt.

## Backoff

For attempt number (n), use capped exponential backoff:

`delay = min(max_delay, base_delay * 2^(n - 1))`

Apply bounded jitter to avoid synchronized retry waves. Inject the clock and random source so tests do not sleep or depend on nondeterministic timing.

## Idempotency boundary

The queue can prevent some duplicate scheduling, but it cannot promise exactly-once side effects across an arbitrary external API and a process crash. Use a stable job ID as an idempotency key with downstream services where supported. Document retention for deduplication records and test the crash window where a handler succeeds but acknowledgement fails; the expected recovery is a repeat delivery that the handler can safely recognize.

## Shutdown

Stop accepting new work first. Give in-flight handlers a bounded grace period, then leave unacknowledged jobs recoverable according to the backend's documented lease or visibility timeout.

## Required tests

Test success acknowledgment, retry count boundaries, capped delay, jitter bounds, dead-letter transfer, handler exceptions, backend exceptions, and shutdown with an in-flight task. Core tests should not require a live Redis server.
