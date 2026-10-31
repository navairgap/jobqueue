# Job idempotency contract (proposed)

JobQueue is designed for at-least-once delivery. A worker may execute the same job more than once after a process crash, lease expiry, or acknowledgement failure. The API must make this behavior explicit.

## Stable job identity

Assign each accepted job a stable identifier that remains unchanged across retries and worker handoffs. A retry must not be represented as a newly submitted job. Persist the identifier with the attempt count, creation timestamp, and payload metadata required by the selected backend.

## Handler expectations

Handlers should be idempotent where possible. For an external side effect, pass the stable job identifier as an idempotency key when the downstream service supports it. If a handler cannot be made idempotent, document the duplicate-effect risk and require an application-specific reconciliation strategy.

Do not claim exactly-once side effects. A worker may complete an external operation and crash before acknowledging the job; the queue cannot know whether the operation happened unless the downstream system participates in an idempotency protocol.

## Deduplication scope

If duplicate submission is supported, define the scope and retention period of its deduplication key. Distinguish a repeated enqueue request from a legitimate new job with similar payload. Never use a payload hash alone as a universal job identity.

## Failure windows to test

- Handler succeeds, process crashes before acknowledgement.
- Acknowledgement succeeds but the client loses the response.
- Worker lease expires while the original worker is paused.
- A stale worker attempts to acknowledge after another worker has acquired the job.
- Duplicate enqueue arrives while the original job is pending, running, completed, or dead-lettered.
- Deduplication state expires and the same external request is submitted again.

Use an injected clock and a fake backend for core tests. Do not require a live Redis server to validate the delivery contract.