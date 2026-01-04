from typing import List, Dict
from datetime import datetime, timedelta
import aiohttp
import asyncio
from .base_scraper import BaseScraper

class HackerNewsScraper(BaseScraper):
    """Scraper for Hacker News discussions"""

    def __init__(self):
        super().__init__("hackernews")
        self.api_url = "https://hn.algolia.com/api/v1/search"

    async def scrape(self) -> List[Dict]:
        """Scrape Hacker News for DigitalOcean mentions"""
        mentions = []

        try:
            async with aiohttp.ClientSession() as session:
                # Search for DigitalOcean with networking keywords
                queries = [
                    "digitalocean vpc",
                    "digitalocean load balancer",
                    "digitalocean network",
                    "digitalocean firewall"
                ]

                for query in queries:
                    params = {
                        "query": query,
                        "tags": "story,comment",
                        "numericFilters": f"created_at_i>{int((datetime.utcnow() - timedelta(days=90)).timestamp())}"
                    }

                    try:
                        async with session.get(self.api_url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()

                                for hit in data.get('hits', []):
                                    # Get comment or story text
                                    text = hit.get('comment_text') or hit.get('story_text') or hit.get('title', '')

                                    if text and len(text) > 50:  # Filter very short mentions
                                        item_type = 'item' if hit.get('comment_text') else 'story'
                                        url = f"https://news.ycombinator.com/{item_type}?id={hit['objectID']}"

                                        mentions.append(self.create_mention_dict(
                                            raw_text=text,
                                            source_url=url,
                                            author=hit.get('author', 'Unknown'),
                                            created_at=datetime.fromtimestamp(hit['created_at_i'])
                                        ))
                    except Exception as e:
                        print(f"Error searching HN for '{query}': {e}")
                        continue

                    await asyncio.sleep(1)

        except Exception as e:
            print(f"Hacker News scraper error: {e}")

        return mentions
