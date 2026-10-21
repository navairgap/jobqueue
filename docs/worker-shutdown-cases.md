# worker shutdown cases

Shutdown should stop accepting jobs, allow in-flight handlers a bounded grace period, and leave timed-out jobs unacknowledged for retry. Never acknowledge a job whose handler failed. Make retry scheduling deterministic under an injected clock. Cap exponential backoff, preserve job IDs across retries, move exhausted jobs to a dead-letter collection, and ensure repeated shutdown signals do not start multiple cleanup routines.
