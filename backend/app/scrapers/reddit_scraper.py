import praw
from typing import List, Dict
from datetime import datetime, timedelta
import os
from .base_scraper import BaseScraper

class RedditScraper(BaseScraper):
    """Scraper for Reddit posts and comments"""

    def __init__(self):
        super().__init__("reddit")
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "DigitalOcean Insight Dashboard/1.0")

        self.subreddits = ["digitalocean", "webhosting", "sysadmin", "devops", "selfhosted"]
        self.keywords = [
            "digitalocean vpc", "digitalocean load balancer",
            "digitalocean nat", "digitalocean floating ip",
            "digitalocean firewall", "digitalocean network"
        ]

    async def scrape(self) -> List[Dict]:
        """Scrape Reddit for DigitalOcean networking mentions"""
        mentions = []

        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )

            # Search in specific subreddits
            for subreddit_name in self.subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)

                    # Search for DigitalOcean mentions
                    for keyword in ["digitalocean", "digital ocean"]:
                        for submission in subreddit.search(keyword, time_filter="month", limit=50):
                            # Check if it's about networking
                            text = f"{submission.title} {submission.selftext}"
                            if self._is_networking_related(text):
                                mentions.append(self.create_mention_dict(
                                    raw_text=text,
                                    source_url=f"https://reddit.com{submission.permalink}",
                                    author=str(submission.author),
                                    created_at=datetime.fromtimestamp(submission.created_utc)
                                ))

                            # Check comments
                            submission.comments.replace_more(limit=0)
                            for comment in submission.comments.list()[:20]:
                                if self._is_networking_related(comment.body):
                                    mentions.append(self.create_mention_dict(
                                        raw_text=comment.body,
                                        source_url=f"https://reddit.com{comment.permalink}",
                                        author=str(comment.author),
                                        created_at=datetime.fromtimestamp(comment.created_utc)
                                    ))
                except Exception as e:
                    print(f"Error scraping r/{subreddit_name}: {e}")
                    continue

        except Exception as e:
            print(f"Reddit scraper error: {e}")

        return mentions

    def _is_networking_related(self, text: str) -> bool:
        """Check if text mentions networking products"""
        text_lower = text.lower()
        networking_keywords = [
            'vpc', 'load balancer', 'nat', 'floating ip',
            'firewall', 'network', 'connectivity', 'bandwidth',
            'peering', 'routing', 'subnet'
        ]
        return any(keyword in text_lower for keyword in networking_keywords)
