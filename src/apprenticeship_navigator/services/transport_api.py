import asyncio
from datetime import datetime
import httpx

from apprenticeship_navigator.models.transport import JourneyPlannerResponse

JOURNEY_PLANNER_BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults"
MAX_ATTEMPTS = 3


class TransportDisambiguationError(Exception):
    pass


class TransportServiceError(Exception):
    pass


async def get_journeys(
    origin: tuple[float, float],
    destination: tuple[float, float],
    arrive_by: datetime,
    client: httpx.AsyncClient,
) -> JourneyPlannerResponse:
    url = (
        f"{JOURNEY_PLANNER_BASE_URL}/{origin[0]},{origin[1]}"
        f"/to/{destination[0]},{destination[1]}"
    )
    params = {
        "date": arrive_by.strftime("%Y%m%d"),
        "time": arrive_by.strftime("%H%M"),
        "timeIs": "Arriving",
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.get(url, params=params, timeout=10.0)
        except httpx.TimeoutException:
            if attempt == MAX_ATTEMPTS:
                raise TransportServiceError(f"Timed out after {MAX_ATTEMPTS} attempts")
            await asyncio.sleep(2**attempt)
            continue

        if response.status_code == 300:
            raise TransportDisambiguationError(
                "Journey planner could not identify a location"
            )

        if response.status_code >= 500:
            if attempt == MAX_ATTEMPTS:
                raise TransportServiceError(
                    f"Service error {response.status_code} after {MAX_ATTEMPTS} attempts"
                )
            await asyncio.sleep(2**attempt)
            continue

        response.raise_for_status()
        return JourneyPlannerResponse.model_validate(response.json())

    raise TransportServiceError("Unreachable")
