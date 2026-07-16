import hmac

from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

from constants import (
    ACTIVE_STORES,
    AUTH_HEADER,
    CATALOGUE_UNAVAILABLE_ERROR,
    STORE_HEADER,
)
from creds import MCP_SHARED_SECRET, USERNAME, PASSWORD
from loggings import logger

_BEARER_PREFIX = "bearer "


def _reject(reason: str) -> None:
    """Log the real reason, raise a generic one.

    Whatever a tool raises is fed back into the language model's context, so the
    message it sees must not disclose valid store codes or the existence of a
    shared secret. Operators get the detail from the logs.
    """
    logger.error(f"Rejected MCP call: {reason}")
    raise ValueError(CATALOGUE_UNAVAILABLE_ERROR)


def _verify_caller(headers) -> None:
    """
    Reject callers that do not present the shared backend -> MCP secret.

    Skipped (with a warning) when `MCP_SHARED_SECRET` is unset, so the secret can
    be rolled out without downtime: deploy the backend sending it first, then set
    it here to begin enforcing.

    Raises:
        ValueError: if a secret is configured and the caller does not match it.
    """
    if not MCP_SHARED_SECRET:
        logger.warning(
            "MCP_SHARED_SECRET is not set — the MCP server is accepting "
            "unauthenticated calls, so any caller can read any store's catalogue."
        )
        return

    presented = (headers.get(AUTH_HEADER) or "").strip()
    if presented.lower().startswith(_BEARER_PREFIX):
        presented = presented[len(_BEARER_PREFIX):].strip()

    # Constant-time compare so the secret cannot be recovered by timing.
    if not hmac.compare_digest(presented, MCP_SHARED_SECRET):
        _reject("caller presented an invalid or missing shared secret")


def resolve_store(ctx) -> dict:
    """
    Resolve the calling store from the transport headers.

    The store code travels as an HTTP header rather than a tool argument, so it
    is chosen by the backend and is invisible to the language model — a
    hallucination or a prompt injection cannot redirect one store's request to
    another store's catalogue.

    An unknown or missing code fails closed. There is deliberately no default
    store: defaulting would silently serve one store's catalogue to another.

    In normal operation this never fails — the backend validates `store_code` and
    rejects the request with a 400 long before the agent runs. A failure here
    means either a caller bypassing the backend, or that `ACTIVE_STORES` has
    drifted out of sync with the backend's `SUPPORTED_STORE_CODES`.

    Args:
        ctx (Context): The FastMCP request context, injected into the tool.

    Returns:
        dict: The store record from `ACTIVE_STORES`, plus its `code`.

    Raises:
        ValueError: If the caller is unauthorized, or the store code is unknown.
            The raised message is deliberately generic — see `_reject`.
    """
    request = getattr(ctx.request_context, "request", None) if ctx else None
    if request is None:
        _reject("no HTTP request context available; cannot resolve the store")

    _verify_caller(request.headers)

    code = (request.headers.get(STORE_HEADER) or "").strip().lower()
    store = ACTIVE_STORES.get(code)
    if not store:
        _reject(
            f"unknown or missing store code {code!r} "
            f"(configured stores: {sorted(ACTIVE_STORES)}). "
            f"If this store is live in the backend, ACTIVE_STORES has drifted."
        )

    return {"code": code, **store}


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
def get_basic_auth() -> HTTPBasicAuth:
    """
    Adds basic authentication to the request.

    Every store's catalogue API shares one credential pair — only the host
    differs — so this takes no store argument.

    Args:
        None

    Returns:
        HTTPBasicAuth: The basic authentication headers.
    """
    return HTTPBasicAuth(USERNAME, PASSWORD)


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
