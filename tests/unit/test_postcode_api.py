import httpx
import pytest
import respx

from apprenticeship_navigator.services.postcode_api import (
    PostcodeNotFoundError,
    get_postcode_lookup,
)


@pytest.mark.asyncio
async def test_get_postcode_lookup_success():
    with respx.mock:
        respx.get("https://api.postcodes.io/postcodes/SW1A1AA").mock(
            return_value=httpx.Response(
                200,
                json={
                    "result": {
                        "postcode": "SW1A 1AA",
                        "latitude": 51.501,
                        "longitude": -0.1415,
                        "lsoa": "Westminster 018C",
                    }
                },
            )
        )

        async with httpx.AsyncClient() as client:
            result = await get_postcode_lookup("SW1A1AA", client)

        assert result.postcode == "SW1A 1AA"
        assert result.lower_super_output_area == "Westminster 018C"


@pytest.mark.asyncio
async def test_get_postcode_lookup_not_found():
    with respx.mock:
        respx.get("https://api.postcodes.io/postcodes/ZZ999ZZ").mock(
            return_value=httpx.Response(404)
        )

        async with httpx.AsyncClient() as client:
            with pytest.raises(PostcodeNotFoundError):
                await get_postcode_lookup("ZZ999ZZ", client)
