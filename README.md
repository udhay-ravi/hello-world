# DigitalOcean Customer Insight Dashboard

A real-time customer insight dashboard that aggregates and displays the top 10 customer problems/pain points for DigitalOcean's IaaS networking products from multiple online sources.

## Features

- **Real-time Data Collection**: Scrapes data from 7+ sources including Reddit, Twitter, Stack Overflow, Hacker News, Trustpilot, Google Trends, and DigitalOcean Ideas portal
- **AI-Powered Analysis**: Uses Claude API (Anthropic) to intelligently categorize and analyze customer feedback
- **Smart Ranking Algorithm**: Ranks problems by frequency × recency × severity with source-weighted scoring
- **Interactive Dashboard**: Beautiful React dashboard with charts, filters, and detailed problem views
- **Export Functionality**: Export insights to CSV or Markdown format
- **Product Filtering**: Filter by specific networking products (VPC, Load Balancer, NAT Gateway, Floating IP, Firewall)
- **Time Range Analysis**: View problems from last 7, 30, or 90 days
- **Trend Indicators**: Rising (↑), stable (→), or declining (↓) trends for each problem

## Architecture

### Backend (Python FastAPI)
- **FastAPI** REST API server
- **SQLite** database for local storage (easily upgradeable to PostgreSQL)
- **Beautiful Soup** for web scraping
- **PRAW** for Reddit API
- **Tweepy** for Twitter API
- **Anthropic Claude API** for intelligent text analysis
- **APScheduler** for automated data refresh (every 6 hours)

### Frontend (React + TypeScript)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Recharts** for data visualizations
- **Axios** for API communication

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker & Docker Compose (optional, for containerized deployment)

## API Keys Required

You'll need to obtain the following API keys:

1. **Anthropic Claude API**: https://console.anthropic.com/
2. **Reddit API**: https://www.reddit.com/prefs/apps
   - Create an app to get `client_id` and `client_secret`
3. **Twitter API**: https://developer.twitter.com/
   - Apply for developer access to get bearer token

*Note: Google Trends doesn't require authentication*

## Installation & Setup

### Option 1: Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd hello-world
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys
```

**Edit `backend/.env`** and add your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DigitalOcean Insight Dashboard/1.0
TWITTER_BEARER_TOKEN=your_bearer_token
DATABASE_URL=sqlite:///./customer_insights.db
FRONTEND_URL=http://localhost:3000
```

#### 3. Populate Sample Data (Optional but Recommended)

```bash
# From backend directory
python populate_sample_data.py
```

This creates realistic sample data so you can see the dashboard in action immediately.

#### 4. Start Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

#### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at http://localhost:3000

### Option 2: Docker Deployment

```bash
# Create .env file in backend directory with your API keys
cp backend/.env.example backend/.env
# Edit backend/.env and add your API keys

# Build and start containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

### Dashboard Features

1. **Top Problems Table**: Click any problem to view detailed information and all source mentions
2. **Filters**:
   - Filter by product (VPC, Load Balancer, etc.)
   - Select time range (7, 30, or 90 days)
3. **Refresh Data**: Manually trigger data collection from all sources
4. **Export**:
   - Export to CSV for data analysis
   - Export to Markdown for reports
5. **Share Insight**: Copy problem summary with sources to clipboard

### Data Collection

#### Manual Refresh
Click the "Refresh Data" button in the dashboard to trigger immediate data collection.

#### Automatic Scheduled Collection
The backend runs data collection automatically every 6 hours (configurable in `.env`).

#### Programmatic Trigger
```bash
curl -X POST http://localhost:8000/api/scraping/trigger
```

### API Endpoints

Full API documentation is available at http://localhost:8000/docs

Key endpoints:
- `GET /api/dashboard/top-problems` - Get top N problems
- `GET /api/dashboard/problem/{id}` - Get problem details
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/time-series` - Get time series data
- `POST /api/scraping/trigger` - Trigger data collection
- `GET /api/scraping/status` - Get scraping status

## Data Sources

The dashboard collects data from:

| Source | Type | Weight | Notes |
|--------|------|--------|-------|
| DigitalOcean Ideas | Feature Requests | 2.0x | Official feedback portal |
| Twitter | Social Media | 1.5x | Real-time complaints |
| Trustpilot | Reviews | 1.4x | Verified customer reviews |
| Hacker News | Discussion | 1.3x | Technical audience |
| Stack Overflow | Q&A | 1.2x | Developer problems |
| Google Trends | Search Interest | 1.1x | Search volume trends |
| Reddit | Community | 1.0x | Community discussions |

## Configuration

### Backend Configuration (`backend/.env`)

```env
# API Keys
ANTHROPIC_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_token

# Database
DATABASE_URL=sqlite:///./customer_insights.db

# Scheduler (hours)
SCRAPE_INTERVAL_HOURS=6

# Server
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Frontend Configuration

Create `frontend/.env.local`:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── models/          # Database models and schemas
│   │   ├── routers/         # API endpoints
│   │   ├── scrapers/        # Data collection scrapers
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Helper functions
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── populate_sample_data.py  # Sample data generator
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Helper functions
│   ├── package.json
│   └── Dockerfile
├── config/
│   └── config.template.env  # Configuration template
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Backend Issues

**Database locked error:**
```bash
# Stop all instances and delete the database
rm backend/customer_insights.db
python backend/populate_sample_data.py
```

**API key errors:**
- Verify your API keys in `backend/.env`
- Some scrapers will gracefully skip if credentials are missing

**Import errors:**
```bash
# Make sure you're in the virtual environment
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend Issues

**Module not found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Proxy errors:**
- Make sure backend is running on port 8000
- Check `frontend/package.json` proxy setting

## Development

### Running Tests

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Adding New Data Sources

1. Create a new scraper in `backend/app/scrapers/`
2. Inherit from `BaseScraper`
3. Implement the `scrape()` method
4. Add to `DataCollector` in `backend/app/services/data_collector.py`
5. Update source weights in ranking algorithm

### Customizing the Ranking Algorithm

Edit `backend/app/services/ranking_service.py`:

```python
# Modify source weights
self.source_weights = {
    'your_source': 2.0,  # Higher = more important
}

# Modify ranking calculation in _calculate_ranking_score()
```

## Production Deployment

### Upgrading to PostgreSQL

1. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

2. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

### Security Recommendations

- Use environment variables for all secrets
- Enable HTTPS with SSL certificates
- Set up rate limiting on API endpoints
- Use authentication for scraping trigger endpoints
- Regularly rotate API keys
- Monitor API usage to avoid rate limits

### Performance Optimization

- Implement Redis caching for frequently accessed data
- Use connection pooling for database
- Enable database indexing on frequently queried fields
- Set up CDN for frontend assets
- Implement pagination for large datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for demonstration purposes.

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section
- Check application logs for errors

## Roadmap

- [ ] Add more data sources (GitHub issues, Discord, Slack communities)
- [ ] Implement email alerts for critical issues
- [ ] Add sentiment timeline charts
- [ ] Create mobile-responsive design improvements
- [ ] Add user authentication and saved filters
- [ ] Implement real-time WebSocket updates
- [ ] Add AI-generated recommendations for each problem
- [ ] Create public API for third-party integrations

---

Built with ❤️ for DigitalOcean customer success
