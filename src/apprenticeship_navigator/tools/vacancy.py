import httpx
from langchain_core.tools import tool

from apprenticeship_navigator.models.vacancy import Vacancy, VacancyWage
from apprenticeship_navigator.services.postcode_api import get_postcode_lookup
from apprenticeship_navigator.services.vacancy_api import search_vacancies


def _wage_text(wage: VacancyWage | None) -> str:
    """Prefer the numeric amount; fall back to the service's own wording."""
    if wage is None:
        return "wage not stated"
    if wage.wage_amount is not None:
        text = f"£{wage.wage_amount:,.0f}"
        if wage.wage_unit:
            text += f" {wage.wage_unit.value.lower()}"
        return text
    if wage.wage_additional_information:
        return wage.wage_additional_information
    return "wage not stated"


def _summarise(vacancy: Vacancy) -> str:
    """One line per vacancy: only the fields the model needs."""
    closing = (
        vacancy.closing_date.date().isoformat() if vacancy.closing_date else "unknown"
    )
    distance = (
        f"{vacancy.distance:.1f} miles"
        if vacancy.distance is not None
        else "distance unknown"
    )

    return (
        f"- {vacancy.title} | {vacancy.employer_name} | "
        f"level {vacancy.apprenticeship_level} | {_wage_text(vacancy.wage)} | "
        f"{distance} | closes {closing} | {vacancy.vacancy_url}"
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
