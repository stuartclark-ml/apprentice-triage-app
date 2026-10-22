from datetime import datetime
from typing import Any

import httpx
import pytest
import respx

from apprenticeship_navigator.services.transport_api import (
    TransportDisambiguationError,
    get_journeys,
)

ORIGIN = (51.501, -0.1415)
DESTINATION = (51.40564, -0.11516)
ARRIVE_BY = datetime(2026, 10, 13, 9, 0)
URL = (
    "https://api.tfl.gov.uk/Journey/JourneyResults/51.501,-0.1415/to/51.40564,-0.11516"
)


@pytest.mark.asyncio
async def test_get_journeys_reads_real_reply(
    journey_success_payload: dict[str, Any],
) -> None:
    with respx.mock:
        route = respx.get(URL).mock(
            return_value=httpx.Response(200, json=journey_success_payload)
        )
        async with httpx.AsyncClient() as client:
            result = await get_journeys(ORIGIN, DESTINATION, ARRIVE_BY, client)

    assert len(result.journeys) == 3
    assert result.journeys[0].duration == 37
    sent = route.calls.last.request.url.params
    assert sent["date"] == "20261013"
    assert sent["time"] == "0900"
    assert sent["timeIs"] == "Arriving"


@pytest.mark.asyncio
async def test_get_journeys_raises_on_disambiguation(
    journey_disambiguation_payload: dict[str, Any],
) -> None:
    with respx.mock:
        respx.get(URL).mock(
            return_value=httpx.Response(300, json=journey_disambiguation_payload)
        )
        async with httpx.AsyncClient() as client:
            with pytest.raises(TransportDisambiguationError):
                await get_journeys(ORIGIN, DESTINATION, ARRIVE_BY, client)
