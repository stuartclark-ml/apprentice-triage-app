from apprenticeship_navigator.models.applicant_view import RouteView
from apprenticeship_navigator.models.vacancy import VacancyWage, WageType, WageUnit
from apprenticeship_navigator.agents.routing import (
    FEASIBLE_MAX_MINUTES,
    MARGINAL_MAX_MINUTES,
)
from apprenticeship_navigator.models.transport import Feasibility, Journey


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
