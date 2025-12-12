from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

from constants import BASE_URL
from creds import USERNAME, PASSWORD


# function to add basic authentication to the request
def get_basic_auth() -> HTTPBasicAuth:
    """
    Adds basic authentication to the request.

    Args:
        None

    Returns:
        HTTPBasicAuth: The basic authentication headers.
    """
    return HTTPBasicAuth(USERNAME, PASSWORD)


# function to combine the url using urllib.parse.urljoin
def get_url(endpoint: str) -> str:
    """
    Combines the base URL with the endpoint.

    Args:
        endpoint (str): The endpoint to be appended to the base URL.

    Returns:
        str: The combined URL.
    """
    return urljoin(BASE_URL, endpoint)


# function to add headers to the request
def get_headers():
    """
    Adds headers to the request.

    Args:
        None

    Returns:
        dict: A dictionary containing the headers.
    """

    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
