from pydantic import BaseModel

from apprenticeship_navigator.models.postcode import PostcodeLookup
from apprenticeship_navigator.models.transport import VacancyJourney

COORDINATE_DECIMAL_PLACES = (
    2  # about .5 kilometre; enough to stop pinpointing an address
)


class SafeLocation(BaseModel):
    """Area-level location: never a postcode, coordinates rounded."""

    area: str
    latitude: float
    longitude: float


def sanitise(lookup: PostcodeLookup) -> SafeLocation:
    """Keep the area and rounded coordinates; the postcode is dropped here."""
    return SafeLocation(
        area=lookup.lower_super_output_area,
        latitude=round(lookup.latitude, COORDINATE_DECIMAL_PLACES),
        longitude=round(lookup.longitude, COORDINATE_DECIMAL_PLACES),
    )


def explanation_facts(
    journeys: list[VacancyJourney],
) -> list[dict[str, str | int | None]]:
    """Allow-list: the only vacancy and journey fields Gemini ever receives."""
    return [
        {
            "title": j.vacancy.title,
            "employer": j.vacancy.employer_name,
            "level": j.vacancy.apprenticeship_level,
            "closing_date": (
                j.vacancy.closing_date.date().isoformat()
                if j.vacancy.closing_date is not None
                else None
            ),
            "journey_minutes": j.journey.duration if j.journey is not None else None,
            "feasibility": j.feasibility,
        }
        for j in journeys
    ]
