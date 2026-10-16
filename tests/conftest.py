import pytest
from fastapi.testclient import TestClient

from quotes_api.api.deps import get_repository
from quotes_api.main import create_app
from quotes_api.storage.repository import InMemoryJobRepository


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    repo = InMemoryJobRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app)


@pytest.fixture
def job(client) -> dict:
    body = {"title": "Reforma de baño", "description": "Cambiar bañera por plato de ducha", "province": "Madrid"}
    return client.post("/jobs", json=body).json()
