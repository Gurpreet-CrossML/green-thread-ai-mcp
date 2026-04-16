import json

from typing import Optional, List, Literal
from urllib.parse import quote

import requests

from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from constants import SYSTEM_PROMPT, USER_PROMPT,  GEMINI_MODEL, RESPONSE_SCHEMA
from creds import GEMINI_API_KEY
from schemas import Tyres, Tyre, VehicleOEMTyresResponse
from utils import get_url, get_basic_auth, get_headers
from loggings import logger

mcp = FastMCP(
    name=str(
        "Tyre Database Service "
        "A service to manage and retrieve tyre data. "
        "1.0.0"
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "127.0.0.1",
            "127.0.0.1:*",
            "localhost",
            "localhost:*",
            "ec2-44-197-115-243.compute-1.amazonaws.com",
            "ec2-44-197-115-243.compute-1.amazonaws.com:*",
            "ec2-13-49-41-40.eu-north-1.compute.amazonaws.com",
            "ec2-13-49-41-40.eu-north-1.compute.amazonaws.com:*"
        ],
        allowed_origins=[
            "http://ec2-44-197-115-243.compute-1.amazonaws.com",
            "https://ec2-44-197-115-243.compute-1.amazonaws.com",
            "http://ec2-13-49-41-40.eu-north-1.compute.amazonaws.com",
            "https://ec2-13-49-41-40.eu-north-1.compute.amazonaws.com",
            "http://localhost",
            "http://localhost:*",
        ],
    ),
)


@mcp.tool()
def list_tyres(
    tyre_id: Optional[str] = None,
    brand: Optional[str] = None,
    tyre_size: Optional[str] = None,
    load_index: Optional[int] = None,
    speed_rating: Optional[str] = None,
    season: Optional[List[Literal['summer', 'lamel', 'all_season']]] = None,
    wet_grip: Optional[str] = None,
    noise_db: Optional[int] = None,
    rolling_resistance: Optional[str] = None,
    price_from: Optional[float] = None,
    price_to: Optional[float] = None,
    is_premium: Optional[bool] = None,
    vehicle_type: Optional[List[Literal['car', 'suv',
                                        'van', 'moto', 'truck', 'otr']]] = None,
    limit: int = 5,
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
        season (Optional[List[Literal['summer', 'lamel', 'all_season']]]): Filter by season.
        wet_grip (Optional[str]): Filter by wet grip class.
        noise_db (Optional[int]): Filter by noise level in dB.
        rolling_resistance (Optional[str]): Filter by rolling resistance class.
        price_from (Optional[float]): Filter by minimum price.
        price_to (Optional[float]): Filter by maximum price.
        is_premium (Optional[bool]): Filter by premium status.
        vehicle_type (Optional[List[Literal['car', 'suv', 'van', 'moto', 'truck', 'otr']]]): Filter by type of vehicles.
        limit (int): Maximum number of tyres to return.

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
            **({"season": ','.join(season)} if season is not None and len(season) > 0 else {}),
            **({"wet_grip": wet_grip} if wet_grip is not None else {}),
            **({"noise_db": noise_db} if noise_db is not None else {}),
            **({"rolling_resistance": rolling_resistance} if rolling_resistance is not None else {}),
            **({"price_from": price_from} if price_from is not None else {}),
            **({"price_to": price_to} if price_to is not None else {}),
            **({"is_premium": is_premium} if is_premium is not None else {}),
            **({"vehicle_type": ','.join(vehicle_type)} if vehicle_type is not None and len(vehicle_type) > 0 else {})
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
            # Limit the number of tyres returned
            "tyres": [Tyre(**item) for item in data[:limit]],
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


@mcp.tool()
def get_oem_tyre_size(
    brand: str,
    model: str,
    year: int
) -> VehicleOEMTyresResponse:

    client = genai.Client(api_key=GEMINI_API_KEY)
    query = USER_PROMPT.format(brand=brand, model=model, year=year)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=query)
            ]
        )
    ]

    tools = [
        types.Tool(
            google_search=types.GoogleSearch()
        ),
    ]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.LOW,
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT)
        ],
        response_mime_type="application/json",
        response_schema=RESPONSE_SCHEMA
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config
        )

        data = {}
        if response and isinstance(response.text, str):
            data = json.loads(response.text)

        return VehicleOEMTyresResponse(**data)
    except Exception as e:
        logger.error(
            f"Failed to retrieve OEM tyre size for {brand} {model} {year}: "
            f"{str(e)}"
        )
        return VehicleOEMTyresResponse(**{})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
