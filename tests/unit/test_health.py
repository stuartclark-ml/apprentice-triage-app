from fastapi.testclient import TestClient

from apprenticeship_navigator.api.main import create_app


def test_health_returns_200() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
