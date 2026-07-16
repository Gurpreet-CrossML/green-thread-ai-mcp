import os
import re

from dotenv import load_dotenv

load_dotenv()

# Username from the enviroment variables
USERNAME = os.environ.get('API_USERNAME', '')

if not re.sub(r'\s', '', USERNAME):
    raise NotImplementedError(
        'Before running the server you need to export `API_USERNAME` in the enviroment, or add it in a `.env` file.'
    )


# Password from the enviroment variables
PASSWORD = os.environ.get('API_PASSWORD', '')

if not re.sub(r'\s', '', PASSWORD):
    raise NotImplementedError(
        'Before running the server you need to export `API_PASSWORD` in the enviroment, or add it in a `.env` file.'
    )


# Shared secret for the backend -> MCP hop. The MCP server is reachable over the
# network and serves every store's catalogue, so without this any caller can read
# any store's pricing and stock.
#
# It is optional so it can be rolled out without downtime: deploy the backend
# sending it first, then set it here to begin enforcing. While unset, every
# request is accepted and a warning is logged.
MCP_SHARED_SECRET = os.environ.get('MCP_SHARED_SECRET', '').strip()
