"""Persistence port and an in-memory adapter. Swap the adapter, keep the domain."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from ..domain.models import JobRequest, JobStatus


class JobRepository(Protocol):
    def add(self, job: JobRequest) -> None: ...
    def get(self, job_id: UUID) -> JobRequest | None: ...
    def list(self, status: JobStatus | None = None, province: str | None = None) -> list[JobRequest]: ...
    def save(self, job: JobRequest) -> None: ...


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[UUID, JobRequest] = {}

    def add(self, job: JobRequest) -> None:
        self._jobs[job.id] = job

    def get(self, job_id: UUID) -> JobRequest | None:
        return self._jobs.get(job_id)

    def list(self, status: JobStatus | None = None, province: str | None = None) -> list[JobRequest]:
        jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        if status:
            jobs = [j for j in jobs if j.status is status]
        if province:
            jobs = [j for j in jobs if j.province.lower() == province.lower()]
        return jobs

    def save(self, job: JobRequest) -> None:
        self._jobs[job.id] = job
