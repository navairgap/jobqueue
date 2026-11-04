"""Small in-memory at-least-once queue with fenced worker leases.

All time values are supplied by the caller so tests and applications can use
an injected clock. This module is not persistent and is not a Redis backend.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import math
from threading import RLock
from typing import Any


class DuplicateJob(ValueError):
    """A job ID is already present in this queue."""


@dataclass
class Job:
    job_id: str
    payload: Any
    created_at: float
    available_at: float
    max_attempts: int
    attempts: int = 0
    state: str = "pending"
    lease_owner: str | None = None
    lease_token: int | None = None
    lease_until: float | None = None


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        converted = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be a finite number")
    return converted


class InMemoryQueue:
    """A deterministic queue for exercising at-least-once worker semantics."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._next_lease_token = 1
        self._lock = RLock()

    def enqueue(
        self,
        job_id: str,
        payload: Any,
        *,
        now: float,
        max_attempts: int = 3,
    ) -> Job:
        timestamp = _finite_number(now, "now")
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        with self._lock:
            if job_id in self._jobs:
                raise DuplicateJob(f"job ID already exists: {job_id}")
            job = Job(
                job_id=job_id,
                payload=deepcopy(payload),
                created_at=timestamp,
                available_at=timestamp,
                max_attempts=max_attempts,
            )
            self._jobs[job_id] = job
            return deepcopy(job)

    def claim(self, worker_id: str, *, now: float, lease_seconds: float) -> Job | None:
        timestamp = _finite_number(now, "now")
        duration = _finite_number(lease_seconds, "lease_seconds")
        if duration <= 0:
            raise ValueError("lease_seconds must be greater than zero")
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id must be a non-empty string")

        with self._lock:
            eligible: list[Job] = []
            for job in self._jobs.values():
                if job.state == "pending" and job.available_at <= timestamp:
                    eligible.append(job)
                elif (
                    job.state == "running"
                    and job.lease_until is not None
                    and job.lease_until <= timestamp
                ):
                    if job.attempts >= job.max_attempts:
                        self._mark_dead(job)
                    else:
                        eligible.append(job)

            if not eligible:
                return None

            job = min(eligible, key=lambda item: (item.available_at, item.created_at, item.job_id))
            job.state = "running"
            job.attempts += 1
            job.lease_owner = worker_id
            job.lease_token = self._next_lease_token
            self._next_lease_token += 1
            job.lease_until = timestamp + duration
            return deepcopy(job)

    def ack(self, job_id: str, lease_token: int, *, now: float) -> bool:
        timestamp = _finite_number(now, "now")
        with self._lock:
            job = self._jobs.get(job_id)
            if not self._owns_live_lease(job, lease_token, timestamp):
                return False
            assert job is not None
            job.state = "completed"
            self._clear_lease(job)
            return True

    def fail(
        self,
        job_id: str,
        lease_token: int,
        *,
        now: float,
        retry_delay: float = 0,
    ) -> str | None:
        timestamp = _finite_number(now, "now")
        delay = _finite_number(retry_delay, "retry_delay")
        if delay < 0:
            raise ValueError("retry_delay must not be negative")
        with self._lock:
            job = self._jobs.get(job_id)
            if not self._owns_live_lease(job, lease_token, timestamp):
                return None
            assert job is not None
            self._clear_lease(job)
            if job.attempts >= job.max_attempts:
                self._mark_dead(job)
                return "dead"
            job.state = "pending"
            job.available_at = timestamp + delay
            return "retry"

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return deepcopy(job) if job is not None else None

    def dead_letters(self) -> list[Job]:
        with self._lock:
            return [deepcopy(job) for job in self._jobs.values() if job.state == "dead"]

    @staticmethod
    def _owns_live_lease(job: Job | None, token: int, now: float) -> bool:
        return (
            job is not None
            and job.state == "running"
            and job.lease_token == token
            and job.lease_until is not None
            and now < job.lease_until
        )

    @staticmethod
    def _clear_lease(job: Job) -> None:
        job.lease_owner = None
        job.lease_token = None
        job.lease_until = None

    @classmethod
    def _mark_dead(cls, job: Job) -> None:
        job.state = "dead"
        cls._clear_lease(job)
