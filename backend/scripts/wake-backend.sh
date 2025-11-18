#!/bin/bash
# wake-backend.sh - Start Backend on HP
# Run this ON the HP (192.168.1.199) after SSH from Dell

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🖥️  WAKING BACKEND ON HP...${NC}"

# Navigate to backend directory
BACKEND_DIR="/home/carissa/Documents/system_rebellion/backend"

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

cd "$BACKEND_DIR"
echo "📂 Working directory: $(pwd)"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Verify Python and dependencies
echo "🔍 Python version: $(python --version)"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo -e "${RED}❌ Uvicorn not found in venv!${NC}"
    exit 1
fi

# Set environment variables
export REDIS_URL="redis://192.168.1.216:6379"
export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH}"

# Check Redis connectivity
echo "🔴 Checking Redis connection..."
if python -c "import redis; r = redis.from_url('redis://192.168.1.216:6379'); r.ping()" 2>/dev/null; then
    echo -e "${GREEN}✅ Redis connection verified!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Cannot connect to Redis${NC}"
fi

# Kill any existing backend processes
echo "🧹 Cleaning up old backend processes..."
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start the backend server
echo -e "${GREEN}🚀 STARTING BACKEND SERVER...${NC}"
echo "   URL: http://192.168.1.199:8000"
echo "   Docs: http://192.168.1.199:8000/docs"
echo ""

# Run with auto-reload
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

# This line only runs if uvicorn exits
echo -e "${RED}❌ Backend server stopped${NC}"
exit 1
