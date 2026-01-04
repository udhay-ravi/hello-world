from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class MentionBase(BaseModel):
    source: str
    source_url: Optional[str] = None
    raw_text: str
    excerpt: Optional[str] = None
    author: Optional[str] = None
    sentiment_score: float = 0.0

class MentionCreate(MentionBase):
    problem_id: Optional[int] = None
    content_hash: str

class MentionResponse(MentionBase):
    id: int
    problem_id: Optional[int]
    created_at: datetime
    scraped_at: datetime

    class Config:
        from_attributes = True

class ProblemBase(BaseModel):
    problem_summary: str
    problem_description: str
    product: str
    severity_score: float = Field(ge=1.0, le=10.0)
    sentiment_score: float = Field(ge=-1.0, le=1.0)

class ProblemCreate(ProblemBase):
    pass

class ProblemResponse(ProblemBase):
    id: int
    frequency: int
    first_seen: datetime
    last_seen: datetime
    trend: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProblemWithMentions(ProblemResponse):
    mentions: List[MentionResponse] = []

class TopProblem(BaseModel):
    rank: int
    problem_summary: str
    product: str
    mentions_count: int
    trend: str
    sources: List[str]
    severity_score: float
    sentiment_score: float
    ranking_score: float
    problem_id: int

class DashboardStats(BaseModel):
    total_problems: int
    total_mentions: int
    last_updated: Optional[datetime]
    sources_count: dict
    product_distribution: dict

class TimeSeriesData(BaseModel):
    date: str
    count: int
    product: Optional[str] = None

class ScrapingStatus(BaseModel):
    is_running: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    sources_status: dict
