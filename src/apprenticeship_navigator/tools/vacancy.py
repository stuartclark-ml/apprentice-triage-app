import httpx
from langchain_core.tools import tool

from apprenticeship_navigator.models.vacancy import Vacancy
from apprenticeship_navigator.services.postcode_api import get_postcode_lookup
from apprenticeship_navigator.services.vacancy_api import search_vacancies


def _summarise(vacancy: Vacancy) -> str:
    """One line per vacancy: only the fields the model needs."""
    wage_text = "wage not stated"
    if vacancy.wage and vacancy.wage.wage_amount is not None:
        wage_text = f"£{vacancy.wage.wage_amount:,.0f}"
        if vacancy.wage.wage_unit:
            wage_text += f" {vacancy.wage.wage_unit.value.lower()}"

    closing = (
        vacancy.closing_date.date().isoformat() if vacancy.closing_date else "unknown"
    )

    return (
        f"- {vacancy.title} | {vacancy.employer_name} | "
        f"level {vacancy.apprenticeship_level} | {wage_text} | "
        f"{vacancy.distance} miles | closes {closing} | {vacancy.vacancy_url}"
    )


@tool(response_format="content_and_artifact", parse_docstring=True)
async def search_apprenticeship_vacancies(
    postcode: str, distance_in_miles: int = 10
) -> tuple[str, list[Vacancy]]:
    """Search live apprenticeship vacancies in England near a UK postcode.

    Args:
        postcode: A full UK postcode, for example "SW1A 1AA".
        distance_in_miles: Search radius in miles, from 1 to 50.
    """
    async with httpx.AsyncClient() as client:
        location = await get_postcode_lookup(postcode, client)
        result = await search_vacancies(
            client,
            Lat=location.latitude,
            Lon=location.longitude,
            DistanceInMiles=distance_in_miles,
            Sort="DistanceAsc",
            PageSize=10,
        )

    if not result.vacancies:
        return f"No vacancies found within {distance_in_miles} miles.", []

    summary = "\n".join(_summarise(vacancy) for vacancy in result.vacancies)
    return summary, result.vacancies
