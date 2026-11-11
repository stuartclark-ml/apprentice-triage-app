import asyncio
from typing import Any
import httpx

from apprenticeship_navigator.config import settings
from apprenticeship_navigator.models.vacancy import VacancySearchResponse

VACANCY_API_BASE_URL = "https://api.apprenticeships.education.gov.uk/vacancies"
MAX_ATTEMPTS = 3


class VacancyServiceError(Exception):
    pass


async def _get_json(
    client: httpx.AsyncClient,
    path: str,
    params: dict[str, str | int | float] | None = None,
) -> dict[str, Any]:
    """GET a vacancy API path, retrying timeouts and server errors; return the JSON."""
    url = f"{VACANCY_API_BASE_URL}{path}"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.apprenticeship_api_key,
        "X-Version": "2",
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.get(
                url, headers=headers, params=params, timeout=10.0
            )
        except httpx.TimeoutException:
            if attempt == MAX_ATTEMPTS:
                raise VacancyServiceError(f"Timed out after {MAX_ATTEMPTS} attempts")
            await asyncio.sleep(2**attempt)
            continue

        if response.status_code >= 500:
            if attempt == MAX_ATTEMPTS:
                raise VacancyServiceError(
                    f"Service error {response.status_code} after {MAX_ATTEMPTS} attempts"
                )
            await asyncio.sleep(2**attempt)
            continue

        response.raise_for_status()
        return response.json()

    raise VacancyServiceError("Unreachable")


async def search_vacancies(
    client: httpx.AsyncClient, **query_params: str | int | float
) -> VacancySearchResponse:
    data = await _get_json(client, "/vacancy", query_params)
    return VacancySearchResponse(**data)
