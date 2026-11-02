from datetime import datetime

import httpx
import pytest
import respx
from typing import Any

from apprenticeship_navigator.agents.nodes import (
    locate,
    find_vacancies,
    vacancy_coordinates,
    check_vacancy,
)
from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.models.postcode import PostcodeLookup
from apprenticeship_navigator.models.vacancy import (
    Vacancy,
    VacancyAddress,
    VacancySearchResponse,
)

from apprenticeship_navigator.models.transport import JourneyPlannerResponse

ORIGIN = (51.501, -0.1415)
ARRIVE_BY = datetime(2026, 10, 13, 9, 0)
VACANCY = Vacancy(addresses=[VacancyAddress(latitude=51.40564, longitude=-0.11516)])
TRANSPORT_URL = (
    "https://api.tfl.gov.uk/Journey/JourneyResults/51.501,-0.1415/to/51.40564,-0.11516"
)


@pytest.mark.asyncio
async def test_locate_records_not_found_instead_of_raising():
    state: AgentState = {
        "messages": [],
        "postcode": "ZZ999ZZ",
        "location": None,
        "location_error": None,
        "distance_in_miles": 10,
        "vacancies": [],
        "vacancy_error": None,
        "arrive_by": datetime(2026, 10, 27, 9, 0),
    }
    with respx.mock:
        respx.get("https://api.postcodes.io/postcodes/ZZ999ZZ").mock(
            return_value=httpx.Response(404)
        )
        update = await locate(state)

    assert update["location"] is None
    assert update["location_error"] == "Postcode not found. Please check it."


@pytest.mark.asyncio
async def test_locate_stores_location_on_success():
    state: AgentState = {
        "messages": [],
        "postcode": "SW1A1AA",
        "location": None,
        "location_error": "left over from an earlier run",
        "distance_in_miles": 10,
        "vacancies": [],
        "vacancy_error": None,
        "arrive_by": datetime(2026, 10, 27, 9, 0),
    }
    with respx.mock:
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
        update = await locate(state)

    assert update["location"] is not None
    assert update["location_error"] is None


@pytest.mark.asyncio
async def test_find_vacancies_stores_real_reply(
    vacancy_search_payload: dict[str, Any],
) -> None:
    location = PostcodeLookup.model_validate(
        {
            "postcode": "SW1A 1AA",
            "latitude": 51.501,
            "longitude": -0.1415,
            "lsoa": "Westminster 018C",
        }
    )
    state: AgentState = {
        "messages": [],
        "postcode": "SW1A1AA",
        "location": location,
        "location_error": None,
        "distance_in_miles": 10,
        "vacancies": [],
        "vacancy_error": "left over from an earlier run",
        "arrive_by": datetime(2026, 10, 27, 9, 0),
    }
    with respx.mock:
        respx.get(
            "https://api.apprenticeships.education.gov.uk/vacancies/vacancy"
        ).mock(return_value=httpx.Response(200, json=vacancy_search_payload))
        update = await find_vacancies(state)

    expected = VacancySearchResponse.model_validate(vacancy_search_payload).vacancies
    assert update["vacancies"] == expected
    assert update["vacancy_error"] is None


@pytest.mark.parametrize(
    ("addresses", "expected"),
    [
        (None, None),
        ([VacancyAddress(latitude=51.5)], None),
        (
            [
                VacancyAddress(latitude=51.5),
                VacancyAddress(latitude=51.6, longitude=-0.1),
            ],
            (51.6, -0.1),
        ),
    ],
)
def test_vacancy_coordinates(
    addresses: list[VacancyAddress] | None, expected: tuple[float, float] | None
) -> None:
    assert vacancy_coordinates(Vacancy(addresses=addresses)) == expected


@pytest.mark.asyncio
async def test_check_vacancy_keeps_fastest_journey(
    journey_success_payload: dict[str, Any],
) -> None:
    with respx.mock:
        respx.get(TRANSPORT_URL).mock(
            return_value=httpx.Response(200, json=journey_success_payload)
        )
        async with httpx.AsyncClient() as client:
            result = await check_vacancy(VACANCY, ORIGIN, ARRIVE_BY, client)

    reply = JourneyPlannerResponse.model_validate(journey_success_payload)
    assert result.journey is not None
    assert result.journey.duration == min(j.duration for j in reply.journeys)
    assert result.feasibility == "FEASIBLE"


@pytest.mark.asyncio
async def test_check_vacancy_no_journeys_is_infeasible() -> None:
    with respx.mock:
        respx.get(TRANSPORT_URL).mock(
            return_value=httpx.Response(200, json={"journeys": []})
        )
        async with httpx.AsyncClient() as client:
            result = await check_vacancy(VACANCY, ORIGIN, ARRIVE_BY, client)

    assert result.journey is None
    assert result.feasibility == "INFEASIBLE"


@pytest.mark.asyncio
async def test_check_vacancy_service_error_gives_no_label() -> None:
    with respx.mock:
        respx.get(TRANSPORT_URL).mock(return_value=httpx.Response(300))
        async with httpx.AsyncClient() as client:
            result = await check_vacancy(VACANCY, ORIGIN, ARRIVE_BY, client)

    assert result.journey is None
    assert result.feasibility is None


@pytest.mark.asyncio
async def test_check_vacancy_without_coordinates_skips_service() -> None:
    with respx.mock:
        async with httpx.AsyncClient() as client:
            result = await check_vacancy(Vacancy(), ORIGIN, ARRIVE_BY, client)

    assert result.journey is None
    assert result.feasibility is None
