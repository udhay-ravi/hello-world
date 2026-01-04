from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
import asyncio
import aiohttp

class BaseScraper(ABC):
    """Base class for all data scrapers"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = None
        self.rate_limit_delay = 1.0  # seconds between requests

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Scrape data from the source
        Returns: List of dicts with keys: raw_text, source_url, author, created_at
        """
        pass

    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
        """Fetch URL with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(self.rate_limit_delay)
                async with self.session.get(url, timeout=30) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1} for {url} after {wait_time}s: {e}")
                await asyncio.sleep(wait_time)

    def create_mention_dict(self, raw_text: str, source_url: str,
                           author: str = None, created_at: datetime = None) -> Dict:
        """Create standardized mention dictionary"""
        return {
            'raw_text': raw_text,
            'source_url': source_url,
            'author': author,
            'created_at': created_at or datetime.utcnow(),
            'source': self.source_name
        }
