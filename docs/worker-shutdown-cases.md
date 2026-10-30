# worker shutdown cases

Shutdown should stop accepting jobs, allow in-flight handlers a bounded grace period, and leave timed-out jobs unacknowledged for retry. Never acknowledge a job whose handler failed. Make retry scheduling deterministic under an injected clock. Cap exponential backoff, preserve job IDs across retries, move exhausted jobs to a dead-letter collection, and ensure repeated shutdown signals do not start multiple cleanup routines.

## Lease and heartbeat recovery

If workers use leases, define the lease duration, heartbeat interval, and the maximum tolerated scheduling delay. A job whose lease expires may be delivered again, so handlers must remain safe under duplicate execution. A heartbeat must not extend a lease after the worker has lost ownership. Test worker pause, process crash, delayed heartbeat, and a stale worker attempting to acknowledge a job after another worker has acquired the expired lease.
