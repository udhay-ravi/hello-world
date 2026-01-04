from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import io

from ..models.database import get_db, Problem, Mention
from ..models.schemas import (
    TopProblem, ProblemWithMentions, DashboardStats,
    TimeSeriesData, MentionResponse
)
from ..services.ranking_service import RankingService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/top-problems", response_model=List[TopProblem])
async def get_top_problems(
    limit: int = Query(10, ge=1, le=50),
    product: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get top N problems ranked by frequency, recency, and severity"""
    ranking_service = RankingService(db)
    return ranking_service.get_top_problems(limit, product, days)

@router.get("/problem/{problem_id}", response_model=ProblemWithMentions)
async def get_problem_detail(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific problem"""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Get all mentions for this problem
    mentions = db.query(Mention).filter(Mention.problem_id == problem_id).all()

    return {
        **problem.__dict__,
        'mentions': mentions
    }

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics"""
    ranking_service = RankingService(db)

    total_problems = db.query(Problem).count()
    total_mentions = db.query(Mention).count()

    # Get last scraping time
    last_mention = db.query(Mention).order_by(Mention.scraped_at.desc()).first()
    last_updated = last_mention.scraped_at if last_mention else None

    return {
        'total_problems': total_problems,
        'total_mentions': total_mentions,
        'last_updated': last_updated,
        'sources_count': ranking_service.get_source_distribution(),
        'product_distribution': ranking_service.get_product_distribution()
    }

@router.get("/time-series", response_model=List[TimeSeriesData])
async def get_time_series(
    days: int = Query(30, ge=7, le=365),
    product: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get time series data for charts"""
    ranking_service = RankingService(db)
    return ranking_service.get_time_series_data(days, product)

@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    """Get list of all products"""
    products = db.query(Problem.product).distinct().all()
    return {'products': ['All'] + [p[0] for p in products]}

@router.get("/export/csv")
async def export_to_csv(
    limit: int = Query(10, ge=1, le=100),
    product: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Export top problems to CSV"""
    ranking_service = RankingService(db)
    problems = ranking_service.get_top_problems(limit, product, days)

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'rank', 'problem_summary', 'product', 'mentions_count',
        'trend', 'severity_score', 'sentiment_score', 'sources'
    ])

    writer.writeheader()
    for problem in problems:
        writer.writerow({
            'rank': problem['rank'],
            'problem_summary': problem['problem_summary'],
            'product': problem['product'],
            'mentions_count': problem['mentions_count'],
            'trend': problem['trend'],
            'severity_score': round(problem['severity_score'], 2),
            'sentiment_score': round(problem['sentiment_score'], 2),
            'sources': ', '.join(problem['sources'])
        })

    return {
        'filename': f'top_problems_{datetime.utcnow().strftime("%Y%m%d")}.csv',
        'content': output.getvalue()
    }

@router.get("/export/markdown")
async def export_to_markdown(
    limit: int = Query(10, ge=1, le=100),
    product: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Export weekly summary to Markdown"""
    ranking_service = RankingService(db)
    problems = ranking_service.get_top_problems(limit, product, days)

    # Create Markdown
    md = f"# Customer Insights Report - {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
    md += f"## Top {limit} Problems (Last {days} days)\n\n"

    if product and product != 'All':
        md += f"**Filtered by Product:** {product}\n\n"

    for problem in problems:
        trend_emoji = {'rising': '📈', 'stable': '➡️', 'declining': '📉'}
        emoji = trend_emoji.get(problem['trend'], '➡️')

        md += f"### {problem['rank']}. {problem['problem_summary']} {emoji}\n\n"
        md += f"- **Product:** {problem['product']}\n"
        md += f"- **Mentions:** {problem['mentions_count']}\n"
        md += f"- **Severity:** {problem['severity_score']}/10\n"
        md += f"- **Sentiment:** {problem['sentiment_score']:.2f}\n"
        md += f"- **Sources:** {', '.join(problem['sources'])}\n"
        md += f"- **Trend:** {problem['trend'].title()}\n\n"

        # Get problem details
        prob = db.query(Problem).filter(Problem.id == problem['problem_id']).first()
        if prob:
            md += f"{prob.problem_description}\n\n"

        md += "---\n\n"

    return {
        'filename': f'insights_report_{datetime.utcnow().strftime("%Y%m%d")}.md',
        'content': md
    }
