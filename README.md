# System Design Architect Agent

An agentic web application that guides users through a series of questions about their application and generates system design architecture diagrams.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Web Browser                     │
│          (Chat UI + Mermaid.js renderer)         │
└──────────────────┬──────────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────────┐
│              FastAPI Server                      │
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  Parent Agent    │  │   Worker Agent       │  │
│  │  - Orchestrates  │  │   - Generates        │  │
│  │    conversation  │──│     Mermaid.js       │  │
│  │  - Collects      │  │     diagrams         │  │
│  │    requirements  │  │   - 3 complexity     │  │
│  │  - Validates     │  │     levels           │  │
│  │    answers       │  │   - Architecture     │  │
│  └─────────────────┘  │     summaries        │  │
│                        └──────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## How It Works

1. **Parent Agent** guides the user through 9 questions with selectable options:
   - App name and description
   - Application type (Web, Mobile, API, IoT, etc.)
   - Complexity level (Standard / Complex / Highly Complex)
   - Authentication method
   - Database choice
   - Expected scale
   - Deployment target
   - Additional features

2. **Worker Agent** takes the collected requirements and generates:
   - A Mermaid.js architecture diagram at the chosen complexity level
   - A structured summary of architecture decisions

### Complexity Levels

| Level | Description |
|-------|-------------|
| **Standard** | Clean monolith / client-server. Load balancer, app server, database. |
| **Complex** | Microservices with API gateway, caching, message queues, monitoring. |
| **Highly Complex** | Distributed system with service mesh, event bus (Kafka), CQRS, multi-region, chaos engineering. |

## Quick Start

```bash
# Install dependencies and start the server
./run.sh

# Or manually:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000` in your browser.

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic
- **Frontend**: Vanilla HTML/CSS/JS, Mermaid.js
- **Diagrams**: Mermaid.js (rendered client-side)

## Project Structure

```
app/
├── main.py              # FastAPI server & API routes
├── models.py            # Pydantic models & session state
├── agents/
│   ├── parent_agent.py  # Conversation orchestrator
│   └── worker_agent.py  # Diagram generator
└── templates/
    └── index.html       # Single-page chat UI
```
