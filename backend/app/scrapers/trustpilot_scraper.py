from typing import List, Dict
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TrustpilotScraper(BaseScraper):
    """Scraper for Trustpilot reviews"""

    def __init__(self):
        super().__init__("trustpilot")
        self.base_url = "https://www.trustpilot.com/review/www.digitalocean.com"

    async def scrape(self) -> List[Dict]:
        """Scrape Trustpilot for DigitalOcean reviews"""
        mentions = []

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                # Scrape first 3 pages
                for page in range(1, 4):
                    url = f"{self.base_url}?page={page}"

                    try:
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                # Find review cards
                                reviews = soup.find_all('div', {'class': 'styles_reviewCardInner__EwDq2'})

                                for review in reviews:
                                    try:
                                        # Extract review text
                                        text_elem = review.find('p', {'class': 'typography_body-l__KUYFJ'})
                                        if not text_elem:
                                            continue

                                        text = text_elem.get_text(strip=True)

                                        # Only include if mentions networking
                                        if self._is_networking_related(text):
                                            # Extract author
                                            author_elem = review.find('span', {'class': 'typography_heading-xxs__QKBS8'})
                                            author = author_elem.get_text(strip=True) if author_elem else 'Unknown'

                                            # Extract date
                                            date_elem = review.find('time')
                                            review_date = datetime.fromisoformat(date_elem['datetime']) if date_elem and 'datetime' in date_elem.attrs else datetime.utcnow()

                                            mentions.append(self.create_mention_dict(
                                                raw_text=text,
                                                source_url=self.base_url,
                                                author=author,
                                                created_at=review_date
                                            ))
                                    except Exception as e:
                                        print(f"Error parsing review: {e}")
                                        continue
                    except Exception as e:
                        print(f"Error fetching Trustpilot page {page}: {e}")
                        continue

                    await asyncio.sleep(2)  # Be polite

        except Exception as e:
            print(f"Trustpilot scraper error: {e}")

        return mentions

    def _is_networking_related(self, text: str) -> bool:
        """Check if review mentions networking"""
        text_lower = text.lower()
        keywords = [
            'network', 'vpc', 'load balancer', 'nat', 'floating ip',
            'firewall', 'connectivity', 'bandwidth', 'routing', 'peering'
        ]
        return any(keyword in text_lower for keyword in keywords)
