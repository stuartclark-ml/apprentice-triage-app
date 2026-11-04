from datetime import datetime

from apprenticeship_navigator.models.transport import Journey, VacancyJourney
from apprenticeship_navigator.models.vacancy import Vacancy, VacancyAddress

from apprenticeship_navigator.sanitise import SafeLocation, sanitise, explanation_facts
from apprenticeship_navigator.models.postcode import PostcodeLookup


def test_sanitise_drops_postcode_and_rounds_coordinates():
    lookup = PostcodeLookup(
        postcode="SW1A 1AA",
        latitude=51.50101,
        longitude=-0.141563,
        lower_super_output_area="Westminster 018C",
    )
    result = sanitise(lookup)
    assert result == SafeLocation(
        area="Westminster 018C", latitude=51.5, longitude=-0.14
    )
    assert "SW1A" not in result.model_dump_json()


def test_explanation_facts_sends_only_allowed_fields():
    vacancy = Vacancy(
        title="Bar and Waiting Apprenticeship",
        employer_name="Example Hotel Ltd",
        apprenticeship_level="Intermediate",
        closing_date=datetime(2026, 11, 30, 23, 59),
        employer_contact_email="jane@example.com",
        addresses=[VacancyAddress(postcode="SW1A 2AA", latitude=51.5, longitude=-0.13)],
    )
    journey = Journey(
        duration=24,
        start_date_time=datetime(2026, 11, 5, 8, 36),
        arrival_date_time=datetime(2026, 11, 5, 9, 0),
    )
    facts = explanation_facts(
        [VacancyJourney(vacancy=vacancy, journey=journey, feasibility="FEASIBLE")]
    )
    assert facts == [
        {
            "title": "Bar and Waiting Apprenticeship",
            "employer": "Example Hotel Ltd",
            "level": "Intermediate",
            "closing_date": "2026-11-30",
            "journey_minutes": 24,
            "feasibility": "FEASIBLE",
        }
    ]
