# job delivery semantics

Document the queue's delivery guarantee and acknowledge that at-least-once delivery can repeat handler side effects. Recommend idempotency keys for external operations. Define retryable versus permanent errors, maximum attempts, backoff caps, dead-letter inspection, and shutdown behavior. A job must not be acknowledged before successful handler completion. Include metrics for queue depth, retries, failures, and processing duration.

## Metrics cardinality

Expose aggregate queue depth, running jobs, attempts, retries, failures, dead-letter count, and processing latency. Do not use job IDs, user identifiers, arbitrary handler error text, or raw queue names as unbounded metric labels. Put high-cardinality diagnostic context in access-controlled structured logs instead, with secrets redacted. Document whether queue depth includes delayed and currently running jobs so dashboards remain comparable.
