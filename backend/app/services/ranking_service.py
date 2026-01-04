from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.database import Problem, Mention

class RankingService:
    """Calculate problem rankings based on multiple factors"""

    def __init__(self, db: Session):
        self.db = db

        # Source weights
        self.source_weights = {
            'digitalocean_ideas': 2.0,
            'twitter': 1.5,
            'reddit': 1.0,
            'stackoverflow': 1.2,
            'hackernews': 1.3,
            'trustpilot': 1.4,
            'google_trends': 1.1
        }

    def get_top_problems(self, limit: int = 10, product_filter: str = None,
                        days_filter: int = 30) -> List[Dict]:
        """
        Get top N problems ranked by (frequency × recency × severity)
        """

        # Base query
        query = self.db.query(Problem)

        # Apply filters
        if product_filter and product_filter != 'All':
            query = query.filter(Problem.product == product_filter)

        cutoff_date = datetime.utcnow() - timedelta(days=days_filter)
        query = query.filter(Problem.last_seen >= cutoff_date)

        problems = query.all()

        # Calculate ranking scores
        ranked_problems = []
        for problem in problems:
            score = self._calculate_ranking_score(problem, days_filter)

            if score > 0:
                # Get sources
                sources = self.db.query(Mention.source).filter(
                    Mention.problem_id == problem.id
                ).distinct().all()

                sources_list = [s[0] for s in sources]

                ranked_problems.append({
                    'problem_id': problem.id,
                    'problem_summary': problem.problem_summary,
                    'product': problem.product,
                    'mentions_count': problem.frequency,
                    'trend': self._calculate_trend(problem),
                    'sources': sources_list,
                    'severity_score': problem.severity_score,
                    'sentiment_score': problem.sentiment_score,
                    'ranking_score': score
                })

        # Sort by ranking score
        ranked_problems.sort(key=lambda x: x['ranking_score'], reverse=True)

        # Add rank numbers
        for idx, problem in enumerate(ranked_problems[:limit]):
            problem['rank'] = idx + 1

        return ranked_problems[:limit]

    def _calculate_ranking_score(self, problem: Problem, days_filter: int) -> float:
        """
        Calculate ranking score: frequency × recency_factor × severity × source_weights
        """

        # Frequency component
        frequency = problem.frequency

        # Recency factor (exponential decay)
        days_since_last_seen = (datetime.utcnow() - problem.last_seen).days
        recency_factor = 1.0 / (1.0 + (days_since_last_seen / 7.0))  # Decay over weeks

        # Severity component (normalized 1-10 to 0.1-1.0)
        severity_factor = problem.severity_score / 10.0

        # Calculate weighted mentions by source
        mentions = self.db.query(Mention).filter(
            Mention.problem_id == problem.id
        ).all()

        source_weight_sum = sum(
            self.source_weights.get(m.source, 1.0) for m in mentions
        )

        # Final score
        score = frequency * recency_factor * severity_factor * (source_weight_sum / max(len(mentions), 1))

        return score

    def _calculate_trend(self, problem: Problem) -> str:
        """
        Calculate if problem is rising, stable, or declining
        """

        # Get mentions from last 7 days vs previous 7 days
        now = datetime.utcnow()
        last_week_start = now - timedelta(days=7)
        prev_week_start = now - timedelta(days=14)

        last_week_count = self.db.query(func.count(Mention.id)).filter(
            Mention.problem_id == problem.id,
            Mention.created_at >= last_week_start
        ).scalar()

        prev_week_count = self.db.query(func.count(Mention.id)).filter(
            Mention.problem_id == problem.id,
            Mention.created_at >= prev_week_start,
            Mention.created_at < last_week_start
        ).scalar()

        if prev_week_count == 0:
            return 'rising' if last_week_count > 0 else 'stable'

        ratio = last_week_count / prev_week_count

        if ratio > 1.5:
            return 'rising'
        elif ratio < 0.5:
            return 'declining'
        else:
            return 'stable'

    def get_time_series_data(self, days: int = 30, product: str = None) -> List[Dict]:
        """Get time series data for charts"""

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(
            func.date(Mention.created_at).label('date'),
            func.count(Mention.id).label('count')
        ).filter(
            Mention.created_at >= cutoff_date
        )

        if product and product != 'All':
            query = query.join(Problem).filter(Problem.product == product)

        query = query.group_by(func.date(Mention.created_at)).order_by('date')

        results = query.all()

        return [
            {'date': str(r.date), 'count': r.count}
            for r in results
        ]

    def get_source_distribution(self) -> Dict[str, int]:
        """Get count of mentions by source"""

        results = self.db.query(
            Mention.source,
            func.count(Mention.id).label('count')
        ).group_by(Mention.source).all()

        return {r.source: r.count for r in results}

    def get_product_distribution(self) -> Dict[str, int]:
        """Get count of problems by product"""

        results = self.db.query(
            Problem.product,
            func.count(Problem.id).label('count')
        ).group_by(Problem.product).all()

        return {r.product: r.count for r in results}
