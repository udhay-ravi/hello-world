#!/usr/bin/env bash
# Start the System Design Architect Agent
set -e

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting server on http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
