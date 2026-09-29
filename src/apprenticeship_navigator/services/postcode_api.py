import asyncio
import httpx
from apprenticeship_navigator.models.postcode import PostcodeLookup

POSTCODES_IO_BASE_URL = "https://api.postcodes.io"
MAX_ATTEMPTS = 3


class PostcodeNotFoundError(Exception):
    pass


class PostcodeServiceError(Exception):
    pass


async def get_postcode_lookup(
    postcode: str, client: httpx.AsyncClient
) -> PostcodeLookup:
    url = f"{POSTCODES_IO_BASE_URL}/postcodes/{postcode}"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.get(url, timeout=10.0)
        except httpx.TimeoutException:
            if attempt == MAX_ATTEMPTS:
                raise PostcodeServiceError(f"Timed out after {MAX_ATTEMPTS} attempts")
            await asyncio.sleep(2**attempt)
            continue

        if response.status_code == 404:
            raise PostcodeNotFoundError(f"No result for postcode: {postcode}")

        if response.status_code >= 500:
            if attempt == MAX_ATTEMPTS:
                raise PostcodeServiceError(
                    f"Service error {response.status_code} after {MAX_ATTEMPTS} attempts"
                )
            await asyncio.sleep(2**attempt)
            continue

        response.raise_for_status()
        data = response.json()["result"]
        return PostcodeLookup(**data)

    raise PostcodeServiceError("Unreachable")
