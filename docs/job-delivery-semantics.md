# job delivery semantics

Document the queue's delivery guarantee and acknowledge that at-least-once delivery can repeat handler side effects. Recommend idempotency keys for external operations. Define retryable versus permanent errors, maximum attempts, backoff caps, dead-letter inspection, and shutdown behavior. A job must not be acknowledged before successful handler completion. Include metrics for queue depth, retries, failures, and processing duration.
