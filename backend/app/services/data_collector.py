import asyncio
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.database import Problem, Mention, ScrapingLog
from ..utils.text_processing import compute_content_hash, get_sentiment_score, extract_excerpt
from ..utils.claude_analyzer import ClaudeAnalyzer
from ..scrapers.reddit_scraper import RedditScraper
from ..scrapers.twitter_scraper import TwitterScraper
from ..scrapers.stackoverflow_scraper import StackOverflowScraper
from ..scrapers.hackernews_scraper import HackerNewsScraper
from ..scrapers.google_trends_scraper import GoogleTrendsScraper
from ..scrapers.trustpilot_scraper import TrustpilotScraper
from ..scrapers.digitalocean_ideas_scraper import DigitalOceanIdeasScraper

class DataCollector:
    """Orchestrates data collection from all sources"""

    def __init__(self, db: Session):
        self.db = db
        self.claude_analyzer = ClaudeAnalyzer()

        # Source weights for ranking
        self.source_weights = {
            'digitalocean_ideas': 2.0,
            'twitter': 1.5,
            'reddit': 1.0,
            'stackoverflow': 1.2,
            'hackernews': 1.3,
            'trustpilot': 1.4,
            'google_trends': 1.1
        }

    async def collect_all_data(self) -> Dict[str, int]:
        """Run all scrapers and process data"""
        results = {
            'total_mentions': 0,
            'new_problems': 0,
            'updated_problems': 0,
            'sources': {}
        }

        scrapers = [
            ('reddit', RedditScraper()),
            ('twitter', TwitterScraper()),
            ('stackoverflow', StackOverflowScraper()),
            ('hackernews', HackerNewsScraper()),
            ('google_trends', GoogleTrendsScraper()),
            ('trustpilot', TrustpilotScraper()),
            ('digitalocean_ideas', DigitalOceanIdeasScraper())
        ]

        for source_name, scraper in scrapers:
            log = ScrapingLog(source=source_name, status='running', started_at=datetime.utcnow())
            self.db.add(log)
            self.db.commit()

            try:
                print(f"Scraping {source_name}...")
                mentions = await scraper.scrape()

                processed = await self._process_mentions(mentions, source_name)

                log.status = 'success'
                log.items_collected = len(mentions)
                log.completed_at = datetime.utcnow()

                results['sources'][source_name] = len(mentions)
                results['total_mentions'] += len(mentions)
                results['new_problems'] += processed['new_problems']
                results['updated_problems'] += processed['updated_problems']

            except Exception as e:
                log.status = 'failed'
                log.error_message = str(e)
                log.completed_at = datetime.utcnow()
                print(f"Error in {source_name}: {e}")

            self.db.commit()

        return results

    async def _process_mentions(self, mentions: List[Dict], source: str) -> Dict[str, int]:
        """Process raw mentions and create/update problems"""
        stats = {'new_problems': 0, 'updated_problems': 0}

        for mention_data in mentions:
            try:
                # Check for duplicates
                content_hash = compute_content_hash(mention_data['raw_text'])

                existing_mention = self.db.query(Mention).filter(
                    Mention.content_hash == content_hash
                ).first()

                if existing_mention:
                    continue  # Skip duplicates

                # Use Claude to analyze the text
                analysis = self.claude_analyzer.analyze_customer_feedback(
                    mention_data['raw_text'],
                    source
                )

                # Skip if not a valid issue
                if not analysis.get('is_valid_issue', True):
                    continue

                # Calculate sentiment
                sentiment = get_sentiment_score(mention_data['raw_text'])

                # Find or create problem
                problem = self._find_or_create_problem(
                    summary=analysis['problem_summary'],
                    description=analysis['problem_description'],
                    product=analysis['product'],
                    severity=analysis['severity_score']
                )

                if problem.id is None:  # New problem
                    stats['new_problems'] += 1
                else:
                    stats['updated_problems'] += 1

                # Update problem stats
                problem.frequency += 1
                problem.last_seen = mention_data['created_at']
                problem.sentiment_score = (problem.sentiment_score + sentiment) / 2  # Running average

                # Create mention record
                mention = Mention(
                    problem_id=problem.id,
                    source=source,
                    source_url=mention_data['source_url'],
                    raw_text=mention_data['raw_text'],
                    excerpt=extract_excerpt(mention_data['raw_text']),
                    author=mention_data.get('author'),
                    sentiment_score=sentiment,
                    created_at=mention_data['created_at'],
                    content_hash=content_hash
                )

                self.db.add(mention)
                self.db.commit()

            except Exception as e:
                print(f"Error processing mention: {e}")
                continue

        return stats

    def _find_or_create_problem(self, summary: str, description: str,
                                product: str, severity: float) -> Problem:
        """Find existing similar problem or create new one"""

        # Try to find similar problem (same product and similar summary)
        existing = self.db.query(Problem).filter(
            Problem.product == product,
            Problem.problem_summary.ilike(f"%{summary[:50]}%")
        ).first()

        if existing:
            # Update description if needed
            if len(description) > len(existing.problem_description):
                existing.problem_description = description
            return existing

        # Create new problem
        problem = Problem(
            problem_summary=summary,
            problem_description=description,
            product=product,
            severity_score=severity,
            sentiment_score=0.0,
            frequency=0,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            trend='stable'
        )

        self.db.add(problem)
        self.db.flush()  # Get the ID

        return problem
