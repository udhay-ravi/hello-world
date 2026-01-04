from typing import List, Dict
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class StackOverflowScraper(BaseScraper):
    """Scraper for Stack Overflow questions"""

    def __init__(self):
        super().__init__("stackoverflow")
        self.api_url = "https://api.stackexchange.com/2.3/search/advanced"
        self.base_url = "https://stackoverflow.com"

    async def scrape(self) -> List[Dict]:
        """Scrape Stack Overflow for DigitalOcean networking questions"""
        mentions = []

        tags = ["digitalocean"]
        keywords = ["vpc", "load balancer", "nat gateway", "floating ip", "firewall", "networking"]

        try:
            async with aiohttp.ClientSession() as session:
                for keyword in keywords:
                    params = {
                        "order": "desc",
                        "sort": "creation",
                        "tagged": "digitalocean",
                        "q": keyword,
                        "site": "stackoverflow",
                        "pagesize": 30,
                        "filter": "withbody"
                    }

                    try:
                        async with session.get(self.api_url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()

                                for item in data.get('items', []):
                                    # Combine title and body
                                    text = f"{item['title']}\n\n{self._clean_html(item.get('body', ''))}"

                                    mentions.append(self.create_mention_dict(
                                        raw_text=text,
                                        source_url=item['link'],
                                        author=item.get('owner', {}).get('display_name', 'Unknown'),
                                        created_at=datetime.fromtimestamp(item['creation_date'])
                                    ))
                    except Exception as e:
                        print(f"Error fetching Stack Overflow for '{keyword}': {e}")
                        continue

                    # Respect rate limits
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"Stack Overflow scraper error: {e}")

        return mentions

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
