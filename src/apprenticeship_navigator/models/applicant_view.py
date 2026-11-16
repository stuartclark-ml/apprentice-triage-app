from pydantic import BaseModel


class RouteView(BaseModel):
    leave_at: str
    legs: list[str]
    fare: str | None = None


class VacancyCard(BaseModel):
    reference: str
    title: str | None = None
    employer: str | None = None
    level: str | None = None
    closing_date: str | None = None
    start_date: str | None = None
    wage: str | None = None
    hours: str | None = None
    advert_url: str | None = None
    feasibility: str
    journey_minutes: int | None = None
    route: RouteView | None = None
    must_have: list[str] = []
    nice_to_have: list[str] = []
    skills: list[str] = []
    things_to_consider: str | None = None
    requirements_available: bool
