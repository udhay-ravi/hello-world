from typing import List, Dict
from datetime import datetime
from pytrends.request import TrendReq
from .base_scraper import BaseScraper

class GoogleTrendsScraper(BaseScraper):
    """Scraper for Google Trends data"""

    def __init__(self):
        super().__init__("google_trends")
        self.pytrends = TrendReq(hl='en-US', tz=360)

    async def scrape(self) -> List[Dict]:
        """Scrape Google Trends for search interest"""
        mentions = []

        try:
            keywords = [
                "digitalocean vpc issues",
                "digitalocean load balancer problems",
                "digitalocean nat gateway",
                "digitalocean floating ip not working",
                "digitalocean firewall"
            ]

            # Build payload
            self.pytrends.build_payload(
                keywords,
                cat=0,
                timeframe='today 3-m',
                geo='',
                gprop=''
            )

            # Get interest over time
            interest_df = self.pytrends.interest_over_time()

            if not interest_df.empty:
                # Analyze trends
                for keyword in keywords:
                    if keyword in interest_df.columns:
                        recent_interest = interest_df[keyword].tail(4).mean()

                        if recent_interest > 20:  # Threshold for significance
                            text = f"Google Trends shows {recent_interest:.0f}% search interest for '{keyword}' in the last month. This indicates users are actively searching for information about this topic."

                            mentions.append(self.create_mention_dict(
                                raw_text=text,
                                source_url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}",
                                author="Google Trends",
                                created_at=datetime.utcnow()
                            ))

            # Get related queries
            related_queries = self.pytrends.related_queries()
            for keyword, queries in related_queries.items():
                if queries['top'] is not None and not queries['top'].empty:
                    top_queries = queries['top']['query'].head(3).tolist()
                    if top_queries:
                        text = f"Top related searches for '{keyword}': {', '.join(top_queries)}"
                        mentions.append(self.create_mention_dict(
                            raw_text=text,
                            source_url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}",
                            author="Google Trends",
                            created_at=datetime.utcnow()
                        ))

        except Exception as e:
            print(f"Google Trends scraper error: {e}")

        return mentions
