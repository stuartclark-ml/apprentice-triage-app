import httpx
import pytest
import respx

from apprenticeship_navigator.agents.nodes import requirements_for, fetch_requirements
from apprenticeship_navigator.models.transport import VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy

DETAIL_URL = "https://api.apprenticeships.education.gov.uk/vacancies/vacancy/2000062551"


@pytest.mark.asyncio
async def test_requirements_for_keeps_requirements_only():
    with respx.mock:
        respx.get(DETAIL_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "title": "IT Support Technician Apprentice",
                    "employerContactEmail": "someone@example.org",
                    "skills": ["IT skills"],
                    "thingsToConsider": "<ul><li>Right to work in the UK</li></ul>",
                },
            )
        )
        async with httpx.AsyncClient() as client:
            result = await requirements_for("2000062551", client)

    assert result is not None
    assert result.skills == ["IT skills"]
    assert result.things_to_consider == "- Right to work in the UK"
    assert "someone@example.org" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_requirements_for_withdrawn_advert_gives_none():
    with respx.mock:
        respx.get(DETAIL_URL).mock(return_value=httpx.Response(404))
        async with httpx.AsyncClient() as client:
            assert await requirements_for("2000062551", client) is None


GONE_URL = "https://api.apprenticeships.education.gov.uk/vacancies/vacancy/2000000000"


def journey_for(reference: str | None) -> VacancyJourney:
    return VacancyJourney(
        vacancy=Vacancy.model_validate({"vacancyReference": reference})
    )


@pytest.mark.asyncio
async def test_fetch_requirements_keeps_successes_only():
    with respx.mock:
        respx.get(DETAIL_URL).mock(
            return_value=httpx.Response(200, json={"skills": ["IT skills"]})
        )
        respx.get(GONE_URL).mock(return_value=httpx.Response(404))
        update = await fetch_requirements(
            {
                "vacancy_journeys": [
                    journey_for("2000000000"),
                    journey_for("2000062551"),
                    journey_for(None),
                ]
            }
        )

    assert list(update["requirements"]) == ["2000062551"]
