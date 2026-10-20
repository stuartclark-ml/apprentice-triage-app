import httpx

from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.models.postcode import PostcodeLookup
from apprenticeship_navigator.services.postcode_api import (
    PostcodeNotFoundError,
    PostcodeServiceError,
    get_postcode_lookup,
)
from apprenticeship_navigator.models.vacancy import Vacancy
from apprenticeship_navigator.services.vacancy_api import (
    VacancyServiceError,
    search_vacancies,
)


async def locate(state: AgentState) -> dict[str, PostcodeLookup | str | None]:
    """Look up the applicant's postcode; record a reason instead of raising."""
    async with httpx.AsyncClient() as client:
        try:
            location = await get_postcode_lookup(state["postcode"], client)
        except PostcodeNotFoundError:
            return {
                "location": None,
                "location_error": "Postcode not found. Please check it.",
            }
        except (PostcodeServiceError, httpx.HTTPError):
            return {
                "location": None,
                "location_error": "Postcode service unavailable. Try again later.",
            }
    return {"location": location, "location_error": None}


async def find_vacancies(state: AgentState) -> dict[str, list[Vacancy] | str | None]:
    """Search vacancies near the stored location; record a reason instead of raising."""
    location = state["location"]
    if location is None:
        return {"vacancies": [], "vacancy_error": "No location to search from."}
    async with httpx.AsyncClient() as client:
        try:
            result = await search_vacancies(
                client,
                Lat=location.latitude,
                Lon=location.longitude,
                DistanceInMiles=state["distance_in_miles"],
                Sort="DistanceAsc",
                PageSize=10,
            )
        except (VacancyServiceError, httpx.HTTPError):
            return {
                "vacancies": [],
                "vacancy_error": "Vacancy service unavailable. Try again later.",
            }
    return {"vacancies": result.vacancies, "vacancy_error": None}
