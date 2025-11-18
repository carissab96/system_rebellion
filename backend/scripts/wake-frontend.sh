#!/bin/bash
# wake-frontend.sh - Start Frontend on Dell
# Run this ON the Dell (192.168.1.127)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}💻 WAKING FRONTEND ON DELL...${NC}"

# Navigate to frontend directory
FRONTEND_DIR="/home/carissab/Documents/system_rebellion/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"
echo "📂 Working directory: $(pwd)"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Running npm install...${NC}"
    npm install
fi

# Verify Node and npm
echo "🔍 Node version: $(node --version)"
echo "🔍 NPM version: $(npm --version)"

# Kill any existing frontend processes
echo "🧹 Cleaning up old frontend processes..."
pkill -f "vite" || true
pkill -f "node.*vite" || true
sleep 2

# Check backend connectivity
echo "🖥️  Checking backend connection..."
if curl -s http://192.168.1.199:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is reachable!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Cannot reach backend at http://192.168.1.199:8000${NC}"
fi

# Start the frontend dev server
echo -e "${GREEN}🚀 STARTING FRONTEND DEV SERVER...${NC}"
echo "   URL: http://localhost:5173"
echo "   Network: http://192.168.1.127:5173"
echo ""

# Run npm dev with auto-reload
npm run dev

# This line only runs if npm exits
echo -e "${RED}❌ Frontend server stopped${NC}"
exit 1
