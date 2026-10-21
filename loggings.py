import logging

# Configure logger
logger = logging.getLogger("tyre-mcp-service")
logger.setLevel(logging.INFO)

# Create a console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)
