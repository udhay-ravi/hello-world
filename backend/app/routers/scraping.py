from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.database import get_db, ScrapingLog
from ..models.schemas import ScrapingStatus
from ..services.data_collector import DataCollector

router = APIRouter(prefix="/api/scraping", tags=["scraping"])

# Global flag to track scraping status
_scraping_in_progress = False
_last_scraping_result = None

@router.post("/trigger")
async def trigger_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger data collection"""
    global _scraping_in_progress

    if _scraping_in_progress:
        return {'status': 'already_running', 'message': 'Scraping is already in progress'}

    background_tasks.add_task(run_scraping, db)

    return {
        'status': 'started',
        'message': 'Data collection started in background'
    }

@router.get("/status", response_model=ScrapingStatus)
async def get_scraping_status(db: Session = Depends(get_db)):
    """Get current scraping status"""
    global _scraping_in_progress, _last_scraping_result

    # Get last completed scraping
    last_log = db.query(ScrapingLog).filter(
        ScrapingLog.status == 'success'
    ).order_by(ScrapingLog.completed_at.desc()).first()

    # Get sources status
    sources = ['reddit', 'twitter', 'stackoverflow', 'hackernews',
               'google_trends', 'trustpilot', 'digitalocean_ideas']

    sources_status = {}
    for source in sources:
        last_source_log = db.query(ScrapingLog).filter(
            ScrapingLog.source == source
        ).order_by(ScrapingLog.started_at.desc()).first()

        if last_source_log:
            sources_status[source] = {
                'status': last_source_log.status,
                'last_run': last_source_log.completed_at,
                'items_collected': last_source_log.items_collected
            }
        else:
            sources_status[source] = {
                'status': 'never_run',
                'last_run': None,
                'items_collected': 0
            }

    return {
        'is_running': _scraping_in_progress,
        'last_run': last_log.completed_at if last_log else None,
        'next_run': None,  # TODO: Implement with scheduler
        'sources_status': sources_status
    }

async def run_scraping(db: Session):
    """Background task to run scraping"""
    global _scraping_in_progress, _last_scraping_result

    _scraping_in_progress = True

    try:
        collector = DataCollector(db)
        result = await collector.collect_all_data()
        _last_scraping_result = result
    except Exception as e:
        print(f"Scraping error: {e}")
        _last_scraping_result = {'error': str(e)}
    finally:
        _scraping_in_progress = False
