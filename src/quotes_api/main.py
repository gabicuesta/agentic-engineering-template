"""Application factory."""

from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .api import jobs


def create_app() -> FastAPI:
    app = FastAPI(title="Quotes API", version=__version__)
    app.include_router(jobs.router)

    @app.get("/health", tags=["ops"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
