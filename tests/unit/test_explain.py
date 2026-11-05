import json
import pytest

from datetime import datetime
from langchain_google_genai.chat_models import GoogleRateLimitError
from langchain_core.messages import AIMessage

from apprenticeship_navigator.agents import nodes
from apprenticeship_navigator.config import settings
from apprenticeship_navigator.models.transport import Journey, VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy, VacancyAddress
from apprenticeship_navigator.sanitise import explanation_facts


class RateLimitedModel:
    """Stands in for Gemini: every call fails with a rate-limit error."""

    def __init__(self, **kwargs: object) -> None:
        pass

    async def ainvoke(self, messages: object) -> None:
        raise GoogleRateLimitError("rate limited")


class RecordingModel:
    """Stands in for Gemini: remembers what it was sent, replies with fixed text."""

    def __init__(self) -> None:
        self.messages: list = []

    async def ainvoke(self, messages: list) -> AIMessage:
        self.messages = messages
        return AIMessage(content="Fixed reply.")


@pytest.mark.asyncio
async def test_explain_falls_back_when_gemini_is_rate_limited(monkeypatch):
    monkeypatch.setattr(settings, "google_api_key", "fake-key")
    monkeypatch.setattr(nodes, "ChatGoogleGenerativeAI", RateLimitedModel)

    result = await nodes.explain({"vacancy_journeys": []})

    assert result == {
        "explanation": "Explanation unavailable right now. The journey results above still stand."
    }


@pytest.mark.asyncio
async def test_explain_sends_gemini_only_allowed_facts(monkeypatch):
    vacancy = Vacancy(
        title="Bar and Waiting Apprenticeship",
        employer_name="Example Hotel Ltd",
        apprenticeship_level="Intermediate",
        closing_date=datetime(2026, 11, 30, 23, 59),
        employer_contact_email="jane@example.com",
        addresses=[VacancyAddress(postcode="SW1A 2AA", latitude=51.5, longitude=-0.13)],
    )
    journey = Journey(
        duration=24,
        start_date_time=datetime(2026, 11, 5, 8, 36),
        arrival_date_time=datetime(2026, 11, 5, 9, 0),
    )
    reachable = VacancyJourney(vacancy=vacancy, journey=journey, feasibility="FEASIBLE")
    fake = RecordingModel()
    monkeypatch.setattr(settings, "google_api_key", "fake-key")
    monkeypatch.setattr(nodes, "ChatGoogleGenerativeAI", lambda **kwargs: fake)

    result = await nodes.explain({"vacancy_journeys": [reachable]})

    sent = fake.messages[1].content
    assert sent == json.dumps(explanation_facts([reachable]))
    assert "jane@example.com" not in sent
    assert "SW1A" not in sent
    assert "51.5" not in sent
    assert result == {"explanation": "Fixed reply."}
