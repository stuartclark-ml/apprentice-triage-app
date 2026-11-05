import pytest
from langchain_google_genai.chat_models import GoogleRateLimitError

from apprenticeship_navigator.agents import nodes
from apprenticeship_navigator.config import settings


class RateLimitedModel:
    """Stands in for Gemini: every call fails with a rate-limit error."""

    def __init__(self, **kwargs: object) -> None:
        pass

    async def ainvoke(self, messages: object) -> None:
        raise GoogleRateLimitError("rate limited")


@pytest.mark.asyncio
async def test_explain_falls_back_when_gemini_is_rate_limited(monkeypatch):
    monkeypatch.setattr(settings, "google_api_key", "fake-key")
    monkeypatch.setattr(nodes, "ChatGoogleGenerativeAI", RateLimitedModel)

    result = await nodes.explain({"vacancy_journeys": []})

    assert result == {
        "explanation": "Explanation unavailable right now. The journey results above still stand."
    }
