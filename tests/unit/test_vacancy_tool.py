from typing import Any

import httpx
import pytest
import respx

from apprenticeship_navigator.models.vacancy import VacancySearchResponse, VacancyWage
from apprenticeship_navigator.tools.vacancy import (
    _summarise,
    _wage_text,
    search_apprenticeship_vacancies,
)


def test_summarise_shows_wage_text_and_rounded_distance(
    vacancy_search_payload: dict[str, Any],
) -> None:
    vacancy = VacancySearchResponse.model_validate(vacancy_search_payload).vacancies[0]
    line = _summarise(vacancy)
    assert "£14,976 a year" in line
    assert "6.7 miles" in line
    assert "wage not stated" not in line


def test_wage_text_prefers_numeric_amount_when_present() -> None:
    # Not a captured shape: exercises the branch a Custom wage would take.
    wage = VacancyWage.model_validate({"wageAmount": 17082, "wageUnit": "Annually"})
    assert _wage_text(wage) == "£17,082 annually"


def test_wage_text_falls_back_when_nothing_is_stated() -> None:
    assert _wage_text(None) == "wage not stated"
    assert _wage_text(VacancyWage()) == "wage not stated"


@pytest.mark.asyncio
async def test_tool_returns_summary_from_real_reply(
    vacancy_search_payload: dict[str, Any],
) -> None:
    with respx.mock:
        # Copied from test_get_postcode_lookup_success
        respx.get("https://api.postcodes.io/postcodes/SW1A1AA").mock(
            return_value=httpx.Response(
                200,
                json={
                    "result": {
                        "postcode": "SW1A 1AA",
                        "latitude": 51.501,
                        "longitude": -0.1415,
                        "lsoa": "Westminster 018C",
                    }
                },
            )
        )
        # Copied from test_search_vacancies_success, but replying with the fixture
        respx.get(
            "https://api.apprenticeships.education.gov.uk/vacancies/vacancy"
        ).mock(return_value=httpx.Response(200, json=vacancy_search_payload))

        summary = await search_apprenticeship_vacancies.ainvoke(
            {"postcode": "SW1A1AA", "distance_in_miles": 10}
        )

    assert "Childcare Level 3 apprenticeship" in summary
    assert "£14,976 a year" in summary
