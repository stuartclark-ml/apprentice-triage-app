from datetime import datetime

from apprenticeship_navigator.models.transport import (
    Journey,
    JourneyFare,
    JourneyLeg,
    TransportMode,
)
from apprenticeship_navigator.models.vacancy import VacancyWage, WageType, WageUnit
from apprenticeship_navigator.web.views import wage_text, route_view


def test_custom_wage_without_amount_shows_advert_text() -> None:
    wage = VacancyWage(
        wage_type=WageType.custom,
        wage_unit=WageUnit.annually,
        wage_additional_information="£21,263 a year",
    )
    assert wage_text(wage) == "£21,263 a year"


def test_custom_wage_with_amount_is_formatted() -> None:
    wage = VacancyWage(
        wage_type=WageType.custom, wage_amount=15704, wage_unit=WageUnit.annually
    )
    assert wage_text(wage) == "£15,704.00 a year"


def test_minimum_wage_never_invents_a_figure() -> None:
    text = wage_text(VacancyWage(wage_type=WageType.apprenticeship_minimum))
    assert text == "Apprenticeship minimum wage"
    assert "£" not in text


def test_wage_words_and_advert_text_are_joined() -> None:
    wage = VacancyWage(
        wage_type=WageType.apprenticeship_minimum,
        wage_additional_information="  Plus travel costs ",
    )
    assert wage_text(wage) == "Apprenticeship minimum wage. Plus travel costs"


def test_no_wage_gives_none() -> None:
    assert wage_text(None) is None


def make_journey(legs: list[JourneyLeg], fare: JourneyFare | None) -> Journey:
    return Journey(
        duration=sum(leg.duration for leg in legs),
        start_date_time=datetime(2026, 11, 17, 8, 37),
        arrival_date_time=datetime(2026, 11, 17, 8, 58),
        legs=legs,
        fare=fare,
    )


def test_route_with_bus_fare() -> None:
    legs = [
        JourneyLeg(duration=13, mode=TransportMode(name="walking")),
        JourneyLeg(duration=4, mode=TransportMode(name="bus")),
        JourneyLeg(duration=4, mode=TransportMode(name="walking")),
    ]
    route = route_view(make_journey(legs, JourneyFare(total_cost=185)))
    assert route is not None
    assert route.leave_at == "08:37"
    assert route.legs == ["walking 13 min", "bus 4 min", "walking 4 min"]
    assert route.fare == "£1.85"


def test_walking_only_route_has_no_fare() -> None:
    legs = [JourneyLeg(duration=15, mode=TransportMode(name="walking"))]
    route = route_view(make_journey(legs, None))
    assert route is not None
    assert route.fare is None


def test_no_journey_gives_no_route() -> None:
    assert route_view(None) is None
