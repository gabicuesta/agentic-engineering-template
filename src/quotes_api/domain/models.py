"""Domain model: a homeowner posts a job request, professionals send quotes, the owner accepts one.

Pure Python, no framework imports: business rules live here and are tested without HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    OPEN = "open"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"


class QuoteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DomainError(Exception):
    """A business rule was violated. The API maps it to HTTP 409."""


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Quote:
    professional: str
    amount_eur: Decimal
    message: str = ""
    id: UUID = field(default_factory=uuid4)
    status: QuoteStatus = QuoteStatus.PENDING
    created_at: datetime = field(default_factory=_now)


@dataclass
class JobRequest:
    title: str
    description: str
    province: str
    max_quotes: int = 3
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.OPEN
    quotes: list[Quote] = field(default_factory=list)
    created_at: datetime = field(default_factory=_now)

    def add_quote(self, quote: Quote) -> None:
        if self.status is not JobStatus.OPEN:
            raise DomainError(f"Job is {self.status.value}; it no longer accepts quotes.")
        if len(self.quotes) >= self.max_quotes:
            raise DomainError(f"Job already has the maximum of {self.max_quotes} quotes.")
        if any(q.professional == quote.professional for q in self.quotes):
            raise DomainError(f"'{quote.professional}' has already quoted this job.")
        if quote.amount_eur <= 0:
            raise DomainError("Quote amount must be positive.")
        self.quotes.append(quote)

    def quotes_by_price(self, *, descending: bool = False) -> list[Quote]:
        """The job's quotes ordered by amount, cheapest first unless `descending`. Does not mutate the job."""
        return sorted(self.quotes, key=lambda q: q.amount_eur, reverse=descending)

    def accept_quote(self, quote_id: UUID) -> Quote:
        if self.status is not JobStatus.OPEN:
            raise DomainError(f"Job is {self.status.value}; a quote can't be accepted.")
        chosen = next((q for q in self.quotes if q.id == quote_id), None)
        if chosen is None:
            raise DomainError("Quote not found on this job.")
        for q in self.quotes:
            q.status = QuoteStatus.ACCEPTED if q is chosen else QuoteStatus.REJECTED
        self.status = JobStatus.ACCEPTED
        return chosen

    def cancel(self) -> None:
        if self.status is JobStatus.ACCEPTED:
            raise DomainError("An accepted job can't be cancelled.")
        self.status = JobStatus.CANCELLED
