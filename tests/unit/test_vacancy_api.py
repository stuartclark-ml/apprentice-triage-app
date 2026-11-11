import httpx
import pytest
import respx

from apprenticeship_navigator.models.vacancy import QualificationWeighting
from apprenticeship_navigator.services.vacancy_api import get_vacancy, search_vacancies

DETAIL_URL = "https://api.apprenticeships.education.gov.uk/vacancies/vacancy/2000062551"


@pytest.mark.asyncio
async def test_search_vacancies_success():
    with respx.mock:
        respx.get(
            "https://api.apprenticeships.education.gov.uk/vacancies/vacancy"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "total": 1,
                    "totalFiltered": 1,
                    "totalPages": 1,
                    "vacancies": [
                        {
                            "title": "Childcare Level 3 apprenticeship",
                            "employerName": "Example Nursery",
                        }
                    ],
                },
            )
        )

        async with httpx.AsyncClient() as client:
            result = await search_vacancies(client, PostedInLastNumberOfDays=30)

        assert result.total == 1
        assert result.vacancies[0].title == "Childcare Level 3 apprenticeship"


@pytest.mark.asyncio
async def test_get_vacancy_reads_requirements():
    with respx.mock:
        respx.get(DETAIL_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "title": "IT Support Technician Apprentice",
                    "skills": ["Communication skills", "IT skills"],
                    "qualifications": [
                        {
                            "weighting": "Essential",
                            "qualificationType": "GCSE",
                            "subject": "Maths",
                            "grade": "4/C",
                        }
                    ],
                    "thingsToConsider": "<p>Right to work in the UK</p>",
                },
            )
        )
        async with httpx.AsyncClient() as client:
            vacancy = await get_vacancy(client, "2000062551")

    assert vacancy.skills == ["Communication skills", "IT skills"]
    assert vacancy.qualifications is not None
    assert vacancy.qualifications[0].weighting == QualificationWeighting.essential
    assert vacancy.qualifications[0].subject == "Maths"
    assert vacancy.things_to_consider == "<p>Right to work in the UK</p>"


@pytest.mark.asyncio
async def test_get_vacancy_not_found_raises():
    with respx.mock:
        respx.get(DETAIL_URL).mock(return_value=httpx.Response(404))
        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await get_vacancy(client, "2000062551")
