# Quick Start Guide

Get the DigitalOcean Customer Insights Dashboard running in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- (Optional) API keys for live data collection

## Step 1: Backend Setup with Sample Data

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Populate sample data (no API keys needed!)
python populate_sample_data.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend running at **http://localhost:8000** ✅

## Step 2: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend running at **http://localhost:3000** ✅

## Step 3: View the Dashboard

Open your browser and go to:
**http://localhost:3000**

You should see:
- Top 10 customer problems for DigitalOcean networking products
- Interactive charts and visualizations
- Stats cards showing total problems and mentions
- Clickable problem details

## What's Included in Sample Data?

The sample data includes realistic customer problems for:
- **VPC**: Peering failures, custom IP ranges, network latency
- **Load Balancer**: Health check issues, WebSocket draining, SSL renewal
- **NAT Gateway**: Bandwidth limits, HA concerns
- **Floating IP**: Reassignment delays, account limits
- **Firewall**: Rule limits, logging gaps, update delays
- **Networking**: Private DNS, bandwidth monitoring

## Next Steps

### Add Real Data Collection

1. Get API keys:
   - **Claude API**: https://console.anthropic.com/
   - **Reddit**: https://www.reddit.com/prefs/apps
   - **Twitter**: https://developer.twitter.com/

2. Configure backend:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. Trigger data collection:
   - Click "Refresh Data" button in the dashboard
   - Or use API: `curl -X POST http://localhost:8000/api/scraping/trigger`

### Explore Features

- **Filter by Product**: Select VPC, Load Balancer, etc.
- **Change Time Range**: View last 7, 30, or 90 days
- **Click on Problems**: See all mentions and sources
- **Export Data**: Download as CSV or Markdown report
- **Share Insights**: Copy problem summaries to clipboard

### View API Documentation

Visit **http://localhost:8000/docs** for interactive API documentation

## Docker Alternative

If you prefer Docker:

```bash
# Create .env file
cp backend/.env.example backend/.env

# Build and run
docker-compose up --build
```

## Troubleshooting

**Port already in use?**
```bash
# Change ports in docker-compose.yml or kill process:
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

**Database errors?**
```bash
# Reset database
rm backend/customer_insights.db
python backend/populate_sample_data.py
```

**Module not found?**
```bash
# Backend: Ensure virtual environment is activated
source backend/venv/bin/activate

# Frontend: Reinstall dependencies
cd frontend && rm -rf node_modules && npm install
```

## Project Structure Quick Reference

```
hello-world/
├── backend/          # FastAPI server
│   ├── app/
│   │   ├── models/   # Database & schemas
│   │   ├── routers/  # API endpoints
│   │   ├── scrapers/ # Data collectors
│   │   └── services/ # Business logic
│   └── populate_sample_data.py
│
├── frontend/         # React dashboard
│   └── src/
│       ├── components/  # UI components
│       ├── pages/       # Dashboard page
│       └── services/    # API client
│
└── docker-compose.yml
```

## Common Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm start

# Sample data
python backend/populate_sample_data.py

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

**Ready to customize?** Check out the full [README.md](README.md) for advanced configuration, deployment, and development guides!
