"""Request headers and errors for the tyre database service.

The server keeps no store configuration. The backend sends the calling store's
catalogue URL and Basic-auth login as HTTP headers on every call, read from the
store's credentials in Django (see `utils.resolve_store`). They are never tool
arguments, so the language model can neither see them nor choose them, and a
hallucination or a prompt injection in a customer message cannot make one
store's catalogue serve another.
"""

# Header carrying the store code; used only to label log lines.
STORE_HEADER = "x-store-code"

# Headers carrying the store's catalogue API base URL and its Basic-auth login.
CATALOGUE_URL_HEADER = "x-catalogue-url"
CATALOGUE_USERNAME_HEADER = "x-catalogue-username"
CATALOGUE_PASSWORD_HEADER = "x-catalogue-password"


# Anything a tool raises is fed straight back into the language model's context,
# so tool errors must not carry internals — catalogue URLs would otherwise end
# up in the model's context and could be repeated to a customer.
#
# The store is resolved from headers, not a tool argument, so the model cannot
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
