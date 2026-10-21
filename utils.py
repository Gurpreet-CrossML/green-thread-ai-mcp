import ipaddress
import socket
from typing import NoReturn
from urllib.parse import urljoin, urlparse

from requests.auth import HTTPBasicAuth

from constants import (
    CATALOGUE_PASSWORD_HEADER,
    CATALOGUE_UNAVAILABLE_ERROR,
    CATALOGUE_URL_HEADER,
    CATALOGUE_USERNAME_HEADER,
    STORE_HEADER,
)
from loggings import logger


def reject_call(reason: str) -> NoReturn:
    """Log the real reason, raise a generic one.

    Whatever a tool raises is fed back into the language model's context, so the
    message it sees must not disclose catalogue URLs. Operators get the detail from the logs.
    """
    logger.error(f"Rejected MCP call: {reason}")
    raise ValueError(CATALOGUE_UNAVAILABLE_ERROR)


def is_public_host(hostname: str) -> bool:
    """
    Check that a catalogue host resolves only to public internet addresses.

    Stops the server being pointed at services on its own machine or private
    network (localhost, 10.x, 192.168.x, cloud metadata and so on).

    Args:
        hostname (str): The catalogue URL's host.

    Returns:
        bool: True when every address the host resolves to is public; False
            when any is private, loopback, link-local or reserved, or the host
            does not resolve.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    return all(ipaddress.ip_address(info[4][0]).is_global for info in infos)


def resolve_store(ctx) -> dict:
    """
    Resolve the calling store's catalogue from the transport headers.

    The backend sends the store's catalogue URL and Basic-auth login (from the
    store's credentials in Django) as HTTP headers rather than tool arguments,
    so they are chosen by the backend and invisible to the language model — a
    hallucination or a prompt injection cannot redirect one store's request to
    another store's catalogue.

    Missing or invalid values fail closed. There is deliberately no default
    store: defaulting would silently serve one store's catalogue to another.
    Only `https` catalogue URLs on public hosts are accepted.

    Args:
        ctx (Context): The FastMCP request context, injected into the tool.

    Returns:
        dict: ``code``, ``base_url``, ``username`` and ``password``.

    Raises:
        ValueError: If the catalogue headers are missing or invalid. The raised message is deliberately generic —
            see `reject_call`.
    """
    request = getattr(ctx.request_context, "request", None) if ctx else None
    if request is None:
        reject_call("no HTTP request context available; cannot resolve the store")

    code = (request.headers.get(STORE_HEADER) or "").strip().lower()
    base_url = (request.headers.get(CATALOGUE_URL_HEADER) or "").strip()
    username = request.headers.get(CATALOGUE_USERNAME_HEADER) or ""
    password = request.headers.get(CATALOGUE_PASSWORD_HEADER) or ""

    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        reject_call(
            f"store {code!r} has a missing or non-https catalogue URL "
            f"{base_url!r}; set its API URL in the backend's store credentials"
        )
    if not is_public_host(parsed.hostname):
        reject_call(
            f"store {code!r} catalogue URL {base_url!r} does not resolve to a "
            "public address"
        )
    if not username or not password:
        reject_call(
            f"store {code!r} has no catalogue login; set its API username and "
            "password in the backend's store credentials"
        )

    # urljoin drops the last path segment unless the base ends with "/".
    if not base_url.endswith("/"):
        base_url += "/"

    return {
        "code": code,
        "base_url": base_url,
        "username": username,
        "password": password,
    }


# function to combine the url using urllib.parse.urljoin
def get_url(store: dict, endpoint: str) -> str:
    """
    Combines a resolved store's catalogue base URL with the endpoint.

    Args:
        store (dict): A store record returned by `resolve_store`.
        endpoint (str): The endpoint to be appended to the base URL.

    Returns:
        str: The combined URL.
    """
    return urljoin(store["base_url"], endpoint)


# function to add basic authentication to the request
def get_basic_auth(store: dict) -> HTTPBasicAuth:
    """
    Builds the Basic authentication for a store's catalogue API.

    Args:
        store (dict): A store record returned by `resolve_store`.

    Returns:
        HTTPBasicAuth: The store's catalogue login.
    """
    return HTTPBasicAuth(store["username"], store["password"])


# function to add headers to the request
def get_headers():
    """
    Adds headers to the request.

    Args:
        None

    Returns:
        dict: A dictionary containing the headers.
    """

    return {"Content-Type": "application/json", "Accept": "application/json"}
