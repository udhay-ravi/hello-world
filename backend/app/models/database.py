from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./customer_insights.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_summary = Column(String(500), nullable=False)
    problem_description = Column(Text, nullable=False)
    product = Column(String(100), nullable=False, index=True)
    severity_score = Column(Float, default=5.0)
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    frequency = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    trend = Column(String(20), default="stable")  # rising, stable, declining
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Mention(Base):
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, index=True)
    source = Column(String(50), nullable=False, index=True)  # reddit, twitter, stackoverflow, etc.
    source_url = Column(String(500))
    raw_text = Column(Text, nullable=False)
    excerpt = Column(String(500))
    author = Column(String(100))
    sentiment_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String(64), unique=True, index=True)  # For deduplication

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, partial
    items_collected = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
