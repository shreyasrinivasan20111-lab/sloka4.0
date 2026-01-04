#!/bin/bash

# Sloka 4.0 - Server Stop Script
# This script safely stops the FastAPI server and cleans up resources

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for quiet mode
QUIET=false
if [[ "$1" == "--quiet" ]]; then
    QUIET=true
fi

# Function to print colored output (only if not in quiet mode)
print_status() {
    if [ "$QUIET" = false ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

print_success() {
    if [ "$QUIET" = false ]; then
        echo -e "${GREEN}[SUCCESS]${NC} $1"
    fi
}

print_warning() {
    if [ "$QUIET" = false ]; then
        echo -e "${YELLOW}[WARNING]${NC} $1"
    fi
}

print_error() {
    if [ "$QUIET" = false ]; then
        echo -e "${RED}[ERROR]${NC} $1"
    fi
}

if [ "$QUIET" = false ]; then
    echo "🛑 Stopping Sloka 4.0 Server"
    echo "============================"
fi

# Function to kill processes gracefully
kill_processes() {
    local signal=$1
    local description=$2
    local pids=$3
    
    if [ -n "$pids" ]; then
        print_status "$description"
        echo "$pids" | xargs kill $signal 2>/dev/null || true
        sleep 2
        return 0
    fi
    return 1
}

# Find all Python processes running main.py
MAIN_PIDS=$(pgrep -f "python.*main.py" 2>/dev/null || true)

# Find all processes using port 8000
PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)

# Find all uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn" 2>/dev/null || true)

# Combine all PIDs and remove duplicates
ALL_PIDS=$(echo "$MAIN_PIDS $PORT_PIDS $UVICORN_PIDS" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    print_success "No server processes found running"
    exit 0
fi

print_status "Found server processes: $ALL_PIDS"

# Try graceful shutdown first (SIGTERM)
if kill_processes "-TERM" "Sending graceful shutdown signal (SIGTERM)..." "$ALL_PIDS"; then
    # Wait a bit for graceful shutdown
    sleep 3
    
    # Check if any processes are still running
    REMAINING_PIDS=""
    for pid in $ALL_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            REMAINING_PIDS="$REMAINING_PIDS $pid"
        fi
    done
    
    # If processes still running, force kill them
    if [ -n "$REMAINING_PIDS" ]; then
        print_warning "Some processes didn't respond to graceful shutdown"
        kill_processes "-KILL" "Force killing remaining processes (SIGKILL)..." "$REMAINING_PIDS"
        sleep 1
    fi
fi

# Final check
FINAL_PIDS=$(pgrep -f "python.*main.py" 2>/dev/null || true)
FINAL_PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)

if [ -n "$FINAL_PIDS" ] || [ -n "$FINAL_PORT_PIDS" ]; then
    print_error "Some processes may still be running. You may need to restart your terminal."
    if [ "$QUIET" = false ]; then
        echo "Remaining processes:"
        ps aux | grep -E "(python.*main.py|uvicorn)" | grep -v grep || true
    fi
    exit 1
else
    print_success "All server processes stopped successfully"
fi

# Clear any temporary files
if [ -f ".server.pid" ]; then
    print_status "Cleaning up PID file..."
    rm -f .server.pid
fi

# Optional: Clear session data for security
if [ -d "sessions" ]; then
    print_status "Clearing session data for security..."
    rm -rf sessions/*
fi

# Optional: Clear any temp uploads
if [ -d "temp_uploads" ]; then
    print_status "Cleaning up temporary uploads..."
    rm -rf temp_uploads/*
fi

if [ "$QUIET" = false ]; then
    print_success "🛑 Server cleanup completed"
fi
