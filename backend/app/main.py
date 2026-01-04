from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .models.database import init_db
from .routers import dashboard, scraping

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="DigitalOcean Customer Insights API",
    description="API for Customer Insight Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(scraping.router)

@app.get("/")
async def root():
    return {
        "message": "DigitalOcean Customer Insights API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
