from decimal import Decimal

import pytest

from quotes_api.domain.models import DomainError, JobRequest, JobStatus, Quote, QuoteStatus


def make_job(**kw) -> JobRequest:
    return JobRequest(title="Pintar piso", description="Paredes y techos, 80 m2", province="Valencia", **kw)


def test_accepting_a_quote_rejects_the_others():
    job = make_job()
    a, b = Quote("Pinturas Sol", Decimal("2400")), Quote("Color Express", Decimal("2100"))
    job.add_quote(a)
    job.add_quote(b)

    job.accept_quote(b.id)

    assert job.status is JobStatus.ACCEPTED
    assert (a.status, b.status) == (QuoteStatus.REJECTED, QuoteStatus.ACCEPTED)


def test_job_rejects_quotes_beyond_the_limit():
    job = make_job(max_quotes=2)
    job.add_quote(Quote("Pro 1", Decimal("100")))
    job.add_quote(Quote("Pro 2", Decimal("100")))
    with pytest.raises(DomainError, match="maximum of 2"):
        job.add_quote(Quote("Pro 3", Decimal("100")))


def test_a_professional_quotes_only_once():
    job = make_job()
    job.add_quote(Quote("Pro", Decimal("100")))
    with pytest.raises(DomainError, match="already quoted"):
        job.add_quote(Quote("Pro", Decimal("90")))


def test_cancelled_job_takes_no_quotes():
    job = make_job()
    job.cancel()
    with pytest.raises(DomainError, match="cancelled"):
        job.add_quote(Quote("Pro", Decimal("100")))


def test_accepted_job_cannot_be_cancelled():
    job = make_job()
    q = Quote("Pro", Decimal("10"))
    job.add_quote(q)
    job.accept_quote(q.id)
    with pytest.raises(DomainError):
        job.cancel()
