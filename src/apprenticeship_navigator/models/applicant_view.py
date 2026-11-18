from pydantic import BaseModel


class RouteView(BaseModel):
    leave_at: str
    legs: list[str]
    fare: str | None = None


class LetterSection(BaseModel):
    text: str
    is_claim: (
        bool  # claims about the applicant start unticked; job facts start included
    )


class LetterDraft(BaseModel):
    greeting: str
    opening: str
    sections: list[LetterSection]
    closing: str
    sign_off: str


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


class RunView(BaseModel):
    run_id: str
    awaiting_review: bool
    transport_status: str | None = None
    explanation: str
    time_limits: str
    cards: list[VacancyCard] = []
