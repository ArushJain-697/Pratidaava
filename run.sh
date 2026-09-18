#!/usr/bin/env bash
# Start the API + UI shell on http://localhost:8000
set -e
pip install -r requirements.txt --break-system-packages --quiet
uvicorn backend.app:app --reload --port 8000
