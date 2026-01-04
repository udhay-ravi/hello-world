from typing import List, Dict
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class DigitalOceanIdeasScraper(BaseScraper):
    """Scraper for DigitalOcean Ideas portal"""

    def __init__(self):
        super().__init__("digitalocean_ideas")
        self.base_url = "https://ideas.digitalocean.com"

    async def scrape(self) -> List[Dict]:
        """Scrape DigitalOcean Ideas portal"""
        mentions = []

        try:
            async with aiohttp.ClientSession() as session:
                # Search for networking-related ideas
                search_terms = ["vpc", "load balancer", "nat", "firewall", "network"]

                for term in search_terms:
                    url = f"{self.base_url}/ideas?search={term}"

                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }

                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                # Find idea cards (structure may vary, this is a generic approach)
                                ideas = soup.find_all('div', class_=lambda x: x and 'idea' in x.lower())

                                for idea in ideas[:20]:  # Limit per search term
                                    try:
                                        title_elem = idea.find(['h2', 'h3', 'a'])
                                        if not title_elem:
                                            continue

                                        title = title_elem.get_text(strip=True)
                                        desc_elem = idea.find('p')
                                        description = desc_elem.get_text(strip=True) if desc_elem else ""

                                        text = f"{title}\n\n{description}"

                                        # Get URL
                                        link_elem = idea.find('a', href=True)
                                        idea_url = self.base_url + link_elem['href'] if link_elem else url

                                        mentions.append(self.create_mention_dict(
                                            raw_text=text,
                                            source_url=idea_url,
                                            author="DigitalOcean Community",
                                            created_at=datetime.utcnow()
                                        ))
                                    except Exception as e:
                                        print(f"Error parsing idea: {e}")
                                        continue
                    except Exception as e:
                        print(f"Error fetching ideas for '{term}': {e}")
                        continue

                    await asyncio.sleep(2)

        except Exception as e:
            print(f"DigitalOcean Ideas scraper error: {e}")

        return mentions
