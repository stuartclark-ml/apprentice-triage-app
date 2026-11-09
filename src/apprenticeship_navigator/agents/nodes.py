from datetime import datetime

import httpx
import json
from pydantic import ValidationError

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import GoogleAPIError, GoogleRateLimitError
from langgraph.types import interrupt

from apprenticeship_navigator.agents.routing import (
    MARGINAL_MAX_MINUTES,
    REACHABLE,
    feasibility,
)
from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.sanitise import SafeLocation, explanation_facts, sanitise
from apprenticeship_navigator.models.transport import VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy
from apprenticeship_navigator.services.postcode_api import (
    PostcodeNotFoundError,
    PostcodeServiceError,
    get_postcode_lookup,
)
from apprenticeship_navigator.services.transport_api import (
    TransportDisambiguationError,
    TransportServiceError,
    get_journeys,
)
from apprenticeship_navigator.services.vacancy_api import (
    VacancyServiceError,
    search_vacancies,
)

from apprenticeship_navigator.config import settings


async def locate(postcode: str) -> dict[str, SafeLocation | str | None]:
    """Look up the applicant's postcode; record a reason instead of raising."""
    async with httpx.AsyncClient() as client:
        try:
            location = await get_postcode_lookup(postcode, client)
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
    return {"location": sanitise(location), "location_error": None}


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


def vacancy_coordinates(vacancy: Vacancy) -> tuple[float, float] | None:
    """Return the first address's (latitude, longitude), or None if none has both."""
    for address in vacancy.addresses or []:
        if address.latitude is not None and address.longitude is not None:
            return (address.latitude, address.longitude)
    return None


async def check_vacancy(
    vacancy: Vacancy,
    origin: tuple[float, float],
    arrive_by: datetime,
    client: httpx.AsyncClient,
) -> VacancyJourney:
    """Check one vacancy's journey; failures give feasibility None instead of raising."""
    destination = vacancy_coordinates(vacancy)
    if destination is None:
        return VacancyJourney(vacancy=vacancy)
    try:
        response = await get_journeys(origin, destination, arrive_by, client)
    except (
        TransportServiceError,
        TransportDisambiguationError,
        httpx.HTTPError,
        ValidationError,
    ):
        return VacancyJourney(vacancy=vacancy)
    fastest = min(response.journeys, key=lambda journey: journey.duration, default=None)
    minutes = fastest.duration if fastest is not None else None
    return VacancyJourney(
        vacancy=vacancy, journey=fastest, feasibility=feasibility(minutes)
    )


MAX_TRANSPORT_CHECKS = 3


async def check_transport(state: AgentState) -> dict[str, list[VacancyJourney] | str]:
    """Check journeys for up to three vacancies; degraded only if every check fails."""
    location = state["location"]
    if location is None:
        return {"vacancy_journeys": [], "transport_status": "degraded"}
    origin = (location.latitude, location.longitude)
    async with httpx.AsyncClient() as client:
        journeys = [
            await check_vacancy(vacancy, origin, state["arrive_by"], client)
            for vacancy in state["vacancies"][:MAX_TRANSPORT_CHECKS]
        ]
    all_failed = bool(journeys) and all(j.feasibility is None for j in journeys)
    return {
        "vacancy_journeys": journeys,
        "transport_status": "degraded" if all_failed else "ok",
    }


def plain_ending(state: AgentState) -> dict[str, str]:
    """Fixed wording for every run that has nothing reachable to explain."""
    if state["location_error"]:
        text = state["location_error"]
    elif state["vacancy_error"]:
        text = state["vacancy_error"]
    elif state["transport_status"] == "degraded":
        text = "Journey times could not be checked; check travel yourself or try again later."
    elif not state["vacancies"]:
        text = "No vacancies found within your chosen distance."
    else:
        text = f"None of the nearest vacancies can be reached within {MARGINAL_MAX_MINUTES} minutes."
    return {"explanation": text}


EXPLANATION_PROMPT = (
    "You explain apprenticeship options to a young person in England. "
    "Use only the facts provided; never invent vacancies, pay, dates or advice. "
    "If a fact is missing, leave it out rather than guess. "
    "FEASIBLE means a comfortable journey; MARGINAL means reachable but long "
    f"(up to {MARGINAL_MAX_MINUTES} minutes). "
    "For each vacancy, give the title, employer, journey time and closing date. "
    "Plain English, plain text, no headings, under 120 words."
)


async def explain(state: AgentState) -> dict[str, str]:
    """Gemini explains reachable vacancies from allow-listed facts only."""
    reachable = [j for j in state["vacancy_journeys"] if j.feasibility in REACHABLE]
    if settings.google_api_key is None:
        return {
            "explanation": f"{len(reachable)} reachable vacancies. (No Gemini key set.)"
        }
    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model, google_api_key=settings.google_api_key
    )
    facts = json.dumps(explanation_facts(reachable))
    try:
        response = await model.ainvoke(
            [SystemMessage(content=EXPLANATION_PROMPT), HumanMessage(content=facts)]
        )
    except (GoogleRateLimitError, GoogleAPIError):
        return {
            "explanation": "Explanation unavailable right now. The journey results above still stand."
        }
    return {"explanation": response.text}


async def review(state: AgentState) -> dict[str, str]:
    """Pause so a careers adviser can approve Gemini's text against its source facts."""
    reachable = [j for j in state["vacancy_journeys"] if j.feasibility in REACHABLE]
    decision = interrupt(
        {
            "explanation": state["explanation"],
            "facts": explanation_facts(reachable),
        }
    )
    if decision == "approve":
        return {}
    return {
        "explanation": "Explanation withheld after review. The journey results above still stand."
    }
