"""HTTP contracts. Kept separate from domain models so the API can evolve without touching rules."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..domain.models import JobStatus, QuoteStatus


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=4000)
    province: str = Field(min_length=2, max_length=60)
    max_quotes: int = Field(3, ge=1, le=10)


class QuoteCreate(BaseModel):
    professional: str = Field(min_length=2, max_length=120)
    amount_eur: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    message: str = Field("", max_length=2000)


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    professional: str
    amount_eur: Decimal
    message: str
    status: QuoteStatus
    created_at: datetime


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    province: str
    max_quotes: int
    status: JobStatus
    quotes: list[QuoteOut]
    created_at: datetime
