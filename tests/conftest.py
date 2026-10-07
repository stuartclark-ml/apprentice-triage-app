import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def vacancy_search_payload() -> dict[str, Any]:
    """A real vacancy search reply, captured 6 October 2026, trimmed to one vacancy."""
    text = (FIXTURES_DIR / "vacancy_search_response.json").read_text(encoding="utf-8")
    payload: dict[str, Any] = json.loads(text)
    return payload
