from datetime import datetime
from typing import Any

from apprenticeship_navigator.models.applicant_view import (
    RouteView,
    VacancyCard,
    RunView,
)
from apprenticeship_navigator.models.vacancy import (
    Vacancy,
    VacancyWage,
    WageType,
    WageUnit,
    QualificationWeighting,
)
from apprenticeship_navigator.agents.routing import (
    FEASIBLE_MAX_MINUTES,
    MARGINAL_MAX_MINUTES,
)
from apprenticeship_navigator.models.transport import (
    Feasibility,
    Journey,
    VacancyJourney,
)
from apprenticeship_navigator.models.requirements import VacancyRequirements


WAGE_TYPE_WORDS = {
    WageType.apprenticeship_minimum: "Apprenticeship minimum wage",
    WageType.national_minimum: "National minimum wage",
    WageType.competitive_salary: "Competitive salary",
}
UNIT_WORDS = {
    WageUnit.weekly: " a week",
    WageUnit.monthly: " a month",
    WageUnit.annually: " a year",
}


def wage_text(wage: VacancyWage | None) -> str | None:
    """One line of wage, never inventing a figure the advert did not give."""
    if wage is None:
        return None
    if wage.wage_type == WageType.custom and wage.wage_amount is not None:
        unit = UNIT_WORDS.get(wage.wage_unit, "") if wage.wage_unit else ""
        return f"£{wage.wage_amount:,.2f}{unit}"
    parts = []
    words = WAGE_TYPE_WORDS.get(wage.wage_type) if wage.wage_type else None
    if words:
        parts.append(words)
    if wage.wage_additional_information:
        parts.append(wage.wage_additional_information.strip())
    return ". ".join(parts) or None


def route_view(journey: Journey | None) -> RouteView | None:
    """The fastest journey as text: leaving time, legs and fare."""
    if journey is None:
        return None
    fare = None
    if journey.fare is not None and journey.fare.total_cost is not None:
        fare = f"£{journey.fare.total_cost / 100:.2f}"
    return RouteView(
        leave_at=f"{journey.start_date_time:%H:%M}",
        legs=[f"{leg.mode.name} {leg.duration} min" for leg in journey.legs],
        fare=fare,
    )


FEASIBILITY_WORDS = {
    "FEASIBLE": f"Feasible: up to {FEASIBLE_MAX_MINUTES} minutes",
    "MARGINAL": (
        f"Long journey: {FEASIBLE_MAX_MINUTES + 1} to {MARGINAL_MAX_MINUTES} minutes"
    ),
    "INFEASIBLE": f"Not feasible: over {MARGINAL_MAX_MINUTES} minutes or no route",
}


def feasibility_text(feasibility: Feasibility | None) -> str:
    """Feasibility in plain words, with the time limit stated."""
    if feasibility is None:
        return "Journey not checked: transport service unavailable"
    return FEASIBILITY_WORDS[feasibility]


def date_text(moment: datetime | None) -> str | None:
    """A date as '11 January 2027'."""
    if moment is None:
        return None
    return f"{moment.day} {moment:%B %Y}"


def hours_text(vacancy: Vacancy) -> str | None:
    """Hours per week and working pattern, as the advert gives them."""
    parts = []
    if vacancy.hours_per_week is not None:
        parts.append(f"{vacancy.hours_per_week:g} hours a week")
    if vacancy.wage is not None and vacancy.wage.working_week_description:
        parts.append(vacancy.wage.working_week_description.strip())
    return ". ".join(parts) or None


def vacancy_card(
    record: VacancyJourney, requirements: VacancyRequirements | None
) -> VacancyCard:
    """One vacancy as the applicant sees it. Contact details are never copied."""
    vacancy = record.vacancy
    card = VacancyCard(
        reference=vacancy.vacancy_reference or "",
        title=vacancy.title,
        employer=vacancy.employer_name,
        level=vacancy.apprenticeship_level,
        closing_date=date_text(vacancy.closing_date),
        start_date=date_text(vacancy.start_date),
        wage=wage_text(vacancy.wage),
        hours=hours_text(vacancy),
        advert_url=vacancy.vacancy_url,
        feasibility=feasibility_text(record.feasibility),
        journey_minutes=record.journey.duration if record.journey else None,
        route=route_view(record.journey),
        requirements_available=requirements is not None,
    )
    if requirements is not None:
        for q in requirements.qualifications:
            text = f"{q.qualification_type} {q.subject} ({q.grade})"
            if q.weighting == QualificationWeighting.essential:
                card.must_have.append(text)
            else:
                card.nice_to_have.append(text)
        card.skills = list(requirements.skills)
        card.things_to_consider = requirements.things_to_consider
    return card


def run_view(result: dict[str, Any], run_id: str) -> RunView:
    """The whole run as the page shows it: explanation, then a card per vacancy."""
    found = result.get("requirements", {})
    cards = [
        vacancy_card(record, found.get(record.vacancy.vacancy_reference or ""))
        for record in result.get("vacancy_journeys", [])
    ]
    awaiting = "__interrupt__" in result
    if awaiting:
        explanation = result["__interrupt__"][0].value["explanation"]
    else:
        explanation = result.get("explanation") or ""
    return RunView(
        run_id=run_id,
        awaiting_review=awaiting,
        transport_status=result.get("transport_status"),
        explanation=explanation,
        time_limits=". ".join(FEASIBILITY_WORDS.values()),
        cards=cards,
    )
