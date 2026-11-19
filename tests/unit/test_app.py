from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apprenticeship_navigator.runs import NotAwaitingReview
from apprenticeship_navigator.web import app as app_module

client = TestClient(app_module.app)


def test_start_passes_inputs_and_never_echoes_postcode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = {}

    async def fake_start_run(postcode: str, distance_in_miles: int):
        seen["postcode"] = postcode
        seen["distance"] = distance_in_miles
        pause = SimpleNamespace(value={"explanation": "Draft"})
        return "run-1", {"__interrupt__": [pause]}

    monkeypatch.setattr(app_module, "start_run", fake_start_run)
    response = client.post(
        "/runs", json={"postcode": "SW1A1AA", "distance_in_miles": 5}
    )
    assert response.status_code == 200
    assert seen == {"postcode": "SW1A1AA", "distance": 5}
    assert "SW1A1AA" not in response.text


def test_unknown_decision_word_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    called = []

    async def fake_resume_run(run_id: str, decision: str):
        called.append(decision)
        return {}

    monkeypatch.setattr(app_module, "resume_run", fake_resume_run)
    response = client.post("/runs/run-1/decision", json={"decision": "yes"})
    assert response.status_code == 422
    assert called == []


def test_decision_on_run_not_paused_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_resume_run(run_id: str, decision: str):
        raise NotAwaitingReview(run_id)

    monkeypatch.setattr(app_module, "resume_run", fake_resume_run)
    response = client.post("/runs/run-1/decision", json={"decision": "reject"})
    assert response.status_code == 409
