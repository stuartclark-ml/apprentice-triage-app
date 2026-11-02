from datetime import datetime
from typing import Literal

import pytest

from apprenticeship_navigator.agents.routing import (
    Route,
    feasibility,
    route_after_transport,
)
from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.models.transport import Feasibility, VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy


@pytest.mark.parametrize(
    ("minutes", "expected"),
    [
        (60, "FEASIBLE"),
        (61, "MARGINAL"),
        (90, "MARGINAL"),
        (91, "INFEASIBLE"),
        (None, "INFEASIBLE"),
    ],
)
def test_feasibility_bands(minutes: int | None, expected: Feasibility) -> None:
    assert feasibility(minutes) == expected


@pytest.mark.parametrize(
    ("labels", "status", "expected"),
    [
        ([None, "MARGINAL", "INFEASIBLE"], "ok", "explain"),
        (["INFEASIBLE", None, "INFEASIBLE"], "ok", "plain_ending"),
        ([None, None, None], "degraded", "plain_ending"),
    ],
)
def test_route_after_transport(
    labels: list[Feasibility | None], status: Literal["ok", "degraded"], expected: Route
) -> None:
    state: AgentState = {
        "messages": [],
        "postcode": "SW1A1AA",
        "location": None,
        "location_error": None,
        "distance_in_miles": 10,
        "vacancies": [],
        "vacancy_error": None,
        "arrive_by": datetime(2026, 11, 2, 9, 0),
        "vacancy_journeys": [
            VacancyJourney(vacancy=Vacancy(), feasibility=label) for label in labels
        ],
        "transport_status": status,
    }
    assert route_after_transport(state) == expected
