import httpx

from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.models.postcode import PostcodeLookup
from apprenticeship_navigator.services.postcode_api import (
    PostcodeNotFoundError,
    PostcodeServiceError,
    get_postcode_lookup,
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
