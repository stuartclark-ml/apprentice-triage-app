from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from apprenticeship_navigator.models.vacancy import CamelModel, Vacancy


class TransportMode(CamelModel):
    name: str


class JourneyLeg(CamelModel):
    duration: int
    mode: TransportMode


class JourneyFare(CamelModel):
    total_cost: int | None = None


class Journey(CamelModel):
    duration: int
    start_date_time: datetime
    arrival_date_time: datetime
    legs: list[JourneyLeg] = []
    fare: JourneyFare | None = None


class JourneyPlannerResponse(CamelModel):
    journeys: list[Journey] = []


Feasibility = Literal["FEASIBLE", "MARGINAL", "INFEASIBLE"]


class VacancyJourney(BaseModel):
    vacancy: Vacancy
    journey: Journey | None = None
    feasibility: Feasibility | None = None
