import json


from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name = str("Tyre Database Service "
    "A service to manage and retrieve tyre data. "
    "1.0.0"),
)
TYRE_DATA_PATH = "tyre_database.json"


@mcp.tool()
def list_tyres() -> dict:
    """
    Load and return tyre data from the configured TYRE_DATA_PATH.

    This function opens the JSON file pointed to by the module-level TYRE_DATA_PATH
    constant, parses its contents, and returns the resulting Python dictionary.
    It is a thin wrapper around json.load and performs file I/O each time it is called.

    Returns:
        dict: The parsed JSON object representing tyre data. The exact structure
        depends on the stored JSON schema (callers should validate or adapt to the
        expected keys/format).

    Raises:
        FileNotFoundError: If the file at TYRE_DATA_PATH does not exist.
        json.JSONDecodeError: If the file contents are not valid JSON.
        OSError: For other I/O related errors (permissions, hardware issues, etc.).

    Notes:
        - This function performs blocking I/O; avoid calling it repeatedly in tight
        loops or performance-critical paths without caching the result.
        - Callers that require schema validation or transformation should perform
        those steps after receiving the returned dict.
        - The function returns the raw parsed JSON; modifications to the returned
        dict do not affect the underlying file unless explicitly written back.
    """
    data = {}

    if not TYRE_DATA_PATH:
        return data

    with open(TYRE_DATA_PATH, "r") as f:
        data = json.load(f)

    return data


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
