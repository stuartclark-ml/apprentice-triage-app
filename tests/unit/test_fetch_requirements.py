import httpx
import pytest
import respx

from apprenticeship_navigator.agents.nodes import requirements_for

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
