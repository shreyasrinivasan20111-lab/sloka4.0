#!/bin/bash

# Sloka 4.0 - Production Server Start
# Sets environment to production and starts the server

echo "🚀 Starting Sloka 4.0 in PRODUCTION Mode"
echo "======================================="

# Set production environment
export ENVIRONMENT=production

# Use the virtual environment's uvicorn
PYTHON_ENV=".venv/bin"

# Stop any existing servers
pkill -f "uvicorn main:app" 2>/dev/null || true

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

# Start the server in production mode
echo "🔥 Starting PRODUCTION server at http://localhost:8000"
echo "Environment: PRODUCTION"
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_ENV/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
