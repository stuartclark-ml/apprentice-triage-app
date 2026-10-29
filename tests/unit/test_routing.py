from apprenticeship_navigator.agents.routing import feasibility
from apprenticeship_navigator.models.transport import Feasibility
import pytest


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
