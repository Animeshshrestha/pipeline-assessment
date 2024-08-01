from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Settings for the application."""
    API_KEY: str = os.getenv('API_KEY')
    QUALYS_API_URL: str = os.getenv('QUALYS_API_URL')
    CROWDSTRIKE_API_URL: str = os.getenv('CROWDSTRIKE_API_URL')
    IP_ADDRESS_API_URL: str = os.getenv('IP_ADDRESS_API_URL')
    LOGGING_DIR: str = os.getenv('LOGGING_DIR', 'logging')
    SKIP: int = int(os.getenv('SKIP'))
    LIMIT: int = int(os.getenv('LIMIT'))
    MONGO_DB_PORT: int = int(os.getenv('MONGO_DB_PORT'))
    MONGO_DB_HOST: str = str(os.getenv('MONGO_DB_HOST'))
    MONGO_DB_NAME: str = str(os.getenv('MONGO_DB_NAME'))
    MONGO_DB_COLLECTION_NAME: str = str(os.getenv('MONGO_DB_COLLECTION_NAME'))


settings = Settings()
