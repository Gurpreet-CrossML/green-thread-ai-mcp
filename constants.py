"""Store registry for the multi-tenant tyre database service.

The calling store is resolved from an HTTP header (see `utils.resolve_store`),
never from a tool argument. Keeping it off the tool schema means the language
model can neither see the tenant nor choose it, so a hallucination or a prompt
injection in a customer message cannot make one store's catalogue serve another.
"""

# Header carrying the store code on every backend -> MCP call.
STORE_HEADER = "x-store-code"

# Header carrying the shared backend -> MCP secret.
AUTH_HEADER = "authorization"


# Anything a tool raises is fed straight back into the language model's context,
# so tool errors must not carry internals — the list of valid store codes, or the
# fact that a shared secret exists, would otherwise end up in the model's context
# and could be repeated to a customer.
#
# The store is resolved from a header, not a tool argument, so the model cannot
# correct this failure by calling the tool differently. The message therefore
# tells it not to retry: without that it will burn a retry (see the tool
# reliability rules in the agent prompt) before giving up anyway.
#
# The real reason is always logged server-side.
CATALOGUE_UNAVAILABLE_ERROR = (
    "The tyre catalogue is unavailable for this request. Do not retry this tool. "
    "Apologise to the customer, return no recommendations, and suggest they try "
    "again shortly."
)


# Every store runs the same catalogue API software and shares one credential
# pair (`API_USERNAME` / `API_PASSWORD`). What differs — and what therefore
# selects the store — is the host: each `base_url` serves that store's own
# products, prices, buy-links and language.
#
# Because the credentials are shared, they live in `creds.py` rather than here.
# If a store ever needs its own, add `username_env` / `password_env` to its
# record and resolve them in `creds.get_store_credentials`.
ACTIVE_STORES = {
    "renkaat247": {
        "base_url": "https://renkaat247.fi/chat-api/",
    },
    "rehvid": {
        "base_url": "https://rehvid.com/chat-api/",
    },
}
