from typing import Annotated, TypedDict, Literal
from datetime import datetime

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from apprenticeship_navigator.models.postcode import PostcodeLookup
from apprenticeship_navigator.models.transport import VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy


class AgentState(TypedDict):
    """Shared state that every node in the graph reads and updates."""

    messages: Annotated[list[AnyMessage], add_messages]
    postcode: str
    location: PostcodeLookup | None
    location_error: str | None
    distance_in_miles: int
    vacancies: list[Vacancy]
    vacancy_error: str | None
    arrive_by: datetime
    vacancy_journeys: list[VacancyJourney]
    transport_status: Literal["ok", "degraded"]
