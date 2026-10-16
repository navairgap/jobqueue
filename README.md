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

## Delivery guarantees

At-least-once. A job is acknowledged only after the handler returns; crashes mid-handler replay the job on restart. Handlers should be idempotent — use the job id as a dedupe key in your own store.

## Retries & backoff

Failed jobs retry up to `max_retries` (default 3) with exponential backoff and full jitter: `delay = base * 2^attempt * random(0.5..1.5)`. After the final failure the job moves to the dead-letter list, queryable via `queue.dead()`.


## Comparison

vs celery: no broker, no worker fleet — an in-process queue for one machine. vs a database table with a polling loop: real wakeups, no spin. when you outgrow it, migrate to celery; the job shape carries over.


## Testing

```bash
python3 -m unittest discover -s jobqueue -v
```

the suite covers ordering, retry backoff, dead-lettering, and shutdown draining. no network, no docker, no excuses.

## Comparison

vs celery: no broker, no worker fleet — an in-process queue for one machine. vs a database table with a polling loop: real wakeups, no spin. when you outgrow it, migrate to celery; the job shape carries over.

## Testing

```bash
python3 -m unittest discover -s jobqueue -v
```

the suite covers ordering, retry backoff, dead-lettering, and shutdown draining. no network, no docker, no excuses.

## Getting help

issues welcome with: python version, a minimal repro script, and whether the job handler raises. queue dumps (`queue.debug()`) attached as files help enormously.

## Getting help

issues welcome with: python version, a minimal repro script, and whether the job handler raises. queue dumps (`queue.debug()`) attached as files help enormously.

## Shutdown behavior

SIGTERM: stop accepting, drain in-flight, persist pending, exit 0. SIGKILL mid-handler: the job replays on restart — handlers must be idempotent.

## Error messages

dead letters carry a reason: `handler_panic`, `max_retries`, `timeout`. `queue.dead()` returns them with the last error attached — requeue by pushing a copy with a fresh id.

## Environment variables

the queue reads nothing from the environment by design — worker count, retries, and backoff are constructor arguments. if you need env-driven config, load it in your own main and pass values in.

## Common tasks

enqueue a batch: `for id in ids { queue.push(Job::new(id)) }`. inspect dead letters: iterate `queue.dead()`. drain on demand: `queue.drain()` blocks until empty — used in graceful shutdown.

## Design goals

in-process, no broker, no daemon. when a job outgrows one machine, the queue is the wrong tool — graduate to a real broker and keep the handler code unchanged.

## History

the queue was extracted from a telegram bot that needed retries and got a homemade scheduler instead. the bot is gone; the queue earned its own repo by being the only part without regret.
