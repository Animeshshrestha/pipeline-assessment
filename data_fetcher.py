import aiohttp
import asyncio
from logger import Logger

from typing import Tuple, Optional, Dict, Any
from config  import settings

logger = Logger().get_logger()

class DataFetcher:
    """
    Class to fetch data from different sources.
    """
    def __init__(self):
        """
        Initializing the DataFetcher class with API credentials and parameters.
        """
        self.api_key = settings.API_KEY
        self.qualys_url = settings.QUALYS_API_URL
        self.crowdstrike_url = settings.CROWDSTRIKE_API_URL
        self.skip = settings.SKIP
        self.limit = settings.LIMIT

    async def fetch_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Fetches data from the given URL using the provided session and parameters.
        Returns JSON response if status code is 200 else None value is written
        """
        async with session.post(url, headers={"token": self.api_key}, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.content.read()
                error_reason = {"url": str(response.url), "status_code": response.status, "error": error_message.decode("utf-8")}
                logger.error(error_reason)
                return None

    async def fetch_all_data(self) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Fetches data from both Qualys and CrowdStrike APIs concurrently with respective url and query params
        Recieves the qualys data and crowdstrike data to the respective variables.
        """
        query_params = {
            "skip": self.skip,
            "limit": self.limit
        }
        async with aiohttp.ClientSession() as session:
            qualys_task = asyncio.create_task(self.fetch_data(session, self.qualys_url, params=query_params))
            crowdstrike_task = asyncio.create_task(self.fetch_data(session, self.crowdstrike_url, params=query_params))
            qualys_data = await qualys_task
            crowdstrike_data = await crowdstrike_task
            return qualys_data, crowdstrike_data
        
data_fetcher = DataFetcher()