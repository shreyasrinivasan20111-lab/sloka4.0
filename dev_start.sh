#!/bin/bash

# Sloka 4.0 - Quick Start
# Simple server start with minimal setup

echo "🚀 Quick Starting Sloka 4.0 (DEVELOPMENT)..."
echo "============================================="

# Set development environment
export ENVIRONMENT=development

# Stop any existing servers
pkill -f "uvicorn main:app" 2>/dev/null || true

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

# Use the virtual environment's uvicorn
PYTHON_ENV=".venv/bin"

# Start the server directly
echo "🔥 Starting DEVELOPMENT server at http://localhost:8000"
echo "Environment: DEVELOPMENT"
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_ENV/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
