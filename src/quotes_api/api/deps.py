"""Dependency wiring. Tests override `get_repository` with a fresh repository."""

from __future__ import annotations

from functools import lru_cache

from ..storage.repository import InMemoryJobRepository, JobRepository


@lru_cache
def get_repository() -> JobRepository:
    return InMemoryJobRepository()
