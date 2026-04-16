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


# API key from the enviroment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if not re.sub(r'\s', '', GEMINI_API_KEY):
    raise NotImplementedError(
        'Before running the server you need to export `GEMINI_API_KEY` in the enviroment, or add it in a `.env` file.'
    )
