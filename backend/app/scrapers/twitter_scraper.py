import tweepy
from typing import List, Dict
from datetime import datetime, timedelta
import os
from .base_scraper import BaseScraper

class TwitterScraper(BaseScraper):
    """Scraper for Twitter/X mentions"""

    def __init__(self):
        super().__init__("twitter")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        self.search_queries = [
            "@digitalocean VPC",
            "@digitalocean load balancer",
            "@digitalocean NAT",
            "@digitalocean floating IP",
            "@digitalocean firewall",
            "@digitalocean network issue",
            "digitalocean networking problem"
        ]

    async def scrape(self) -> List[Dict]:
        """Scrape Twitter for DigitalOcean mentions"""
        mentions = []

        if not self.bearer_token or self.bearer_token == "your_twitter_bearer_token_here":
            print("Twitter API credentials not configured, skipping...")
            return mentions

        try:
            client = tweepy.Client(bearer_token=self.bearer_token)

            # Search tweets from last 7 days
            start_time = datetime.utcnow() - timedelta(days=7)

            for query in self.search_queries:
                try:
                    tweets = client.search_recent_tweets(
                        query=query,
                        max_results=100,
                        tweet_fields=['created_at', 'author_id', 'public_metrics'],
                        start_time=start_time
                    )

                    if tweets.data:
                        for tweet in tweets.data:
                            mentions.append(self.create_mention_dict(
                                raw_text=tweet.text,
                                source_url=f"https://twitter.com/i/web/status/{tweet.id}",
                                author=f"user_{tweet.author_id}",
                                created_at=tweet.created_at
                            ))

                except Exception as e:
                    print(f"Error searching Twitter for '{query}': {e}")
                    continue

        except Exception as e:
            print(f"Twitter scraper error: {e}")

        return mentions
