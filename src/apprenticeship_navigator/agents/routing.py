from apprenticeship_navigator.models.transport import Feasibility

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
