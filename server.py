from typing import Optional

import requests

from mcp.server.fastmcp import FastMCP

from schemas import Tyres, Tyre
from utils import get_url, get_basic_auth, get_headers
from loggings import logger

mcp = FastMCP(
    name=str(
        "Tyre Database Service "
        "A service to manage and retrieve tyre data. "
        "1.0.0"
    ),
)


@mcp.tool()
def list_tyres(
    tyre_id: Optional[str] = None,
    brand: Optional[str] = None,
    tyre_size: Optional[str] = None,
    load_index: Optional[int] = None,
    speed_rating: Optional[str] = None,
    season: Optional[str] = None,
    wet_grip: Optional[str] = None,
    noise_db: Optional[int] = None,
    rolling_resistance: Optional[str] = None,
    price_from: Optional[float] = None,
    price_to: Optional[float] = None
) -> Tyres:
    """
    List all available tyres in the database.
    Supports filtering by various attributes.

    Args:
        tyre_id (Optional[str]): Filter by tyre ID.
        brand (Optional[str]): Filter by brand.
        tyre_size (Optional[str]): Filter by tyre size.
        load_index (Optional[int]): Filter by load index.
        speed_rating (Optional[str]): Filter by speed rating.
        season (Optional[str]): Filter by season.
        wet_grip (Optional[str]): Filter by wet grip class.
        noise_db (Optional[int]): Filter by noise level in dB.
        rolling_resistance (Optional[str]): Filter by rolling resistance class.
        price_from (Optional[float]): Filter by minimum price.
        price_to (Optional[float]): Filter by maximum price.

    Returns:
        Tyres: A paginated collection of Tyre items.
    """
    url = get_url("tyres")
    response = requests.get(
        url,
        auth=get_basic_auth(),
        headers=get_headers(),
        params={
            **({"tyre_id": tyre_id} if tyre_id is not None else {}),
            **({"brand": brand} if brand is not None else {}),
            **({"tyre_size": tyre_size} if tyre_size is not None else {}),
            **({"load_index": load_index} if load_index is not None else {}),
            **({"speed_rating": speed_rating} if speed_rating is not None else {}),
            **({"season": season} if season is not None else {}),
            **({"wet_grip": wet_grip} if wet_grip is not None else {}),
            **({"noise_db": noise_db} if noise_db is not None else {}),
            **({"rolling_resistance": rolling_resistance} if rolling_resistance is not None else {}),
            **({"price_from": price_from} if price_from is not None else {}),
            **({"price_to": price_to} if price_to is not None else {}),
        }
    )

    if response.status_code == 200:
        result = response.json()

        # Extract the tyres data and pagination information.
        data = result.get("data", [])
        current_page = result.get("current_page", None)
        total_pages = result.get("total_pages", None)
        
        # Form the Tyres object and return it.
        return Tyres(**{
            "tyres": [Tyre(**item) for item in data],
            "current_page": current_page,
            "total_pages": total_pages
        })
    else:
        logger.error(
            f"Failed to fetch tyres: {response.status_code} - {response.text}"
        )
        return Tyres(tyres=[], current_page=None, total_pages=None)


def get_tyre_by_id(tyre_id: str) -> Optional[Tyre]:
    """
    Retrieve a tyre by its unique identifier.

    Args:
        tyre_id (str): The unique identifier of the tyre.

    Returns:
        Optional[Tyre]: The Tyre object if found, otherwise None.
    """
    url = get_url(f"tyres/{tyre_id}")
    response = requests.get(
        url,
        auth=get_basic_auth(),
        headers=get_headers()
    )

    if response.status_code == 200:
        result = response.json()
        data = result.get("data", {})
        return Tyre(**data)
    else:
        logger.error(
            f"Failed to fetch tyre with ID {tyre_id}: "
            f"{response.status_code} - {response.text}"
        )
        return None


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
