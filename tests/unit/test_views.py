from datetime import datetime

from apprenticeship_navigator.models.transport import (
    Journey,
    JourneyFare,
    JourneyLeg,
    TransportMode,
    VacancyJourney,
)
from apprenticeship_navigator.models.requirements import VacancyRequirements

from apprenticeship_navigator.models.vacancy import (
    VacancyWage,
    WageType,
    WageUnit,
    QualificationWeighting,
    Vacancy,
    VacancyAddress,
    VacancyQualification,
)
from apprenticeship_navigator.web.views import (
    feasibility_text,
    route_view,
    wage_text,
    vacancy_card,
)


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


def test_feasible_states_the_limit() -> None:
    assert feasibility_text("FEASIBLE") == "Feasible: up to 60 minutes"


def test_marginal_range_starts_above_feasible_limit() -> None:
    assert feasibility_text("MARGINAL") == "Long journey: 61 to 90 minutes"


def test_unchecked_journey_is_explained() -> None:
    assert (
        feasibility_text(None) == "Journey not checked: transport service unavailable"
    )


def make_vacancy() -> Vacancy:
    return Vacancy(
        title="IT Support Technician Apprentice",
        employer_name="The Halo Trust",
        vacancy_reference="2000062551",
        employer_contact_name="Jo Bloggs",
        employer_contact_email="jo@example.com",
        employer_contact_phone="020 7946 0000",
        addresses=[VacancyAddress(postcode="SW1A 2AA")],
    )


def test_card_never_contains_contact_details() -> None:
    record = VacancyJourney(vacancy=make_vacancy(), feasibility="FEASIBLE")
    sent = vacancy_card(record, None).model_dump_json()
    for private in ("Jo Bloggs", "jo@example.com", "020 7946 0000", "SW1A 2AA"):
        assert private not in sent


def test_requirements_split_into_must_and_nice() -> None:
    requirements = VacancyRequirements(
        reference="2000062551",
        qualifications=[
            VacancyQualification(
                weighting=QualificationWeighting.essential,
                qualification_type="GCSE",
                subject="English",
                grade="4/C",
            ),
            VacancyQualification(
                weighting=QualificationWeighting.desired,
                qualification_type="Level 3",
                subject="IT",
                grade="Pass or above",
            ),
        ],
        skills=["Patience"],
    )
    record = VacancyJourney(vacancy=make_vacancy(), feasibility="FEASIBLE")
    card = vacancy_card(record, requirements)
    assert card.must_have == ["GCSE English (4/C)"]
    assert card.nice_to_have == ["Level 3 IT (Pass or above)"]
    assert card.skills == ["Patience"]
    assert card.requirements_available is True


def test_missing_requirements_and_unchecked_journey() -> None:
    record = VacancyJourney(vacancy=make_vacancy(), feasibility=None)
    card = vacancy_card(record, None)
    assert card.requirements_available is False
    assert card.must_have == []
    assert card.feasibility == "Journey not checked: transport service unavailable"
