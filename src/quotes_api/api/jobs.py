"""Routes for job requests and quotes. Thin: validate, call the domain, map errors."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..domain.models import DomainError, JobRequest, JobStatus, Quote
from ..storage.repository import JobRepository
from .deps import get_repository
from .schemas import JobCreate, JobOut, QuoteCreate, QuoteOut, SortOrder

router = APIRouter(prefix="/jobs", tags=["jobs"])
Repo = Annotated[JobRepository, Depends(get_repository)]


def _get_or_404(repo: JobRepository, job_id: UUID) -> JobRequest:
    job = repo.get(job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found.")
    return job


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(body: JobCreate, repo: Repo) -> JobRequest:
    job = JobRequest(**body.model_dump())
    repo.add(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(repo: Repo, status: JobStatus | None = None, province: str | None = None) -> list[JobRequest]:
    return repo.list(status=status, province=province)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: UUID, repo: Repo) -> JobRequest:
    return _get_or_404(repo, job_id)


@router.post("/{job_id}/quotes", response_model=QuoteOut, status_code=status.HTTP_201_CREATED)
def add_quote(job_id: UUID, body: QuoteCreate, repo: Repo) -> Quote:
    job = _get_or_404(repo, job_id)
    quote = Quote(**body.model_dump())
    try:
        job.add_quote(quote)
    except DomainError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    repo.save(job)
    return quote


@router.get("/{job_id}/quotes", response_model=list[QuoteOut])
def list_quotes(job_id: UUID, repo: Repo, order: SortOrder = SortOrder.ASC) -> list[Quote]:
    job = _get_or_404(repo, job_id)
    return job.quotes_by_price(descending=order is SortOrder.DESC)


@router.post("/{job_id}/quotes/{quote_id}/accept", response_model=JobOut)
def accept_quote(job_id: UUID, quote_id: UUID, repo: Repo) -> JobRequest:
    job = _get_or_404(repo, job_id)
    try:
        job.accept_quote(quote_id)
    except DomainError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    repo.save(job)
    return job


@router.post("/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: UUID, repo: Repo) -> JobRequest:
    job = _get_or_404(repo, job_id)
    try:
        job.cancel()
    except DomainError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    repo.save(job)
    return job
