import httpx
import pytest
import respx

from apprenticeship_navigator.services.vacancy_api import search_vacancies


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
