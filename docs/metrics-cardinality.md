# Job queue metrics and cardinality (proposed)

Metrics should help operators understand queue health without creating unbounded time-series cardinality or leaking job data.

## Recommended metrics

- Queue depth, as a gauge per configured queue.
- Jobs accepted, completed, retried, and dead-lettered, as counters per configured queue and bounded outcome.
- Handler duration, as a histogram per registered handler class.
- Active workers and in-flight jobs, as gauges per configured queue.
- Lease expirations and acknowledgement failures, as counters with bounded reason categories.

## Label restrictions

Do not use job IDs, user IDs, arbitrary payload fields, raw exception messages, request URLs, or customer-supplied queue names as metric labels. These values can be unbounded and may contain secrets or personal data.

Use a bounded registry of queue names and handler identifiers configured by the application. Normalize error categories into a small documented enum. Put detailed diagnostics in access-controlled logs with redaction, not metric labels.

## Operational interpretation

A growing queue depth is a symptom, not a diagnosis. Compare queue depth with arrival rate, completion rate, active workers, and handler duration. A retry spike should remain distinguishable from newly submitted work. Dead-letter counts should not be hidden by a broad success total.

## Tests and review

Verify that arbitrary job IDs and error strings never appear in exported metric labels. Exercise unknown queue/handler values and ensure they map to a bounded fallback or are rejected according to the configured contract. Review metric names and labels before adding new dimensions.