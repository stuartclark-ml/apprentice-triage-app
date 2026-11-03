from pydantic import BaseModel

from apprenticeship_navigator.models.postcode import PostcodeLookup

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
