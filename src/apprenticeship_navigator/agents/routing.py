from apprenticeship_navigator.models.transport import Feasibility
from typing import Literal

from apprenticeship_navigator.agents.state import AgentState

FEASIBLE_MAX_MINUTES = 60
MARGINAL_MAX_MINUTES = 90


def feasibility(minutes: int | None) -> Feasibility:
    if minutes is None:
        return "INFEASIBLE"
    if minutes <= FEASIBLE_MAX_MINUTES:
        return "FEASIBLE"
    if minutes <= MARGINAL_MAX_MINUTES:
        return "MARGINAL"
    return "INFEASIBLE"


Route = Literal["explain", "plain_ending"]
REACHABLE: set[Feasibility] = {"FEASIBLE", "MARGINAL"}


def route_after_transport(state: AgentState) -> Route:
    """Explain if any checked vacancy is reachable; otherwise end plainly."""
    if state["transport_status"] == "degraded":
        return "plain_ending"
    if any(j.feasibility in REACHABLE for j in state["vacancy_journeys"]):
        return "explain"
    return "plain_ending"
