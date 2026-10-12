import httpx
import pytest
import respx

from apprenticeship_navigator.agents.nodes import locate
from apprenticeship_navigator.agents.state import AgentState


@pytest.mark.asyncio
async def test_locate_records_not_found_instead_of_raising():
    state: AgentState = {
        "messages": [],
        "postcode": "ZZ999ZZ",
        "location": None,
        "location_error": None,
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
