from apprenticeship_navigator.sanitise import SafeLocation, sanitise
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
