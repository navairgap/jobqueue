"""JobQueue's in-memory delivery-contract prototype."""
from .core import InMemoryQueue, Job, DuplicateJob

__all__ = ["InMemoryQueue", "Job", "DuplicateJob"]
