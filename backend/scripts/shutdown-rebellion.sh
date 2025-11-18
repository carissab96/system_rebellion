#!/bin/bash
# shutdown-rebellion.sh - Clean shutdown of all System Rebellion services
# Run this from Dell (192.168.1.127) to shutdown all services and clean logs
#
# Hotkey: Super+Shift+S

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Machine configurations
IBM_HOST="carissa@192.168.1.216"
HP_HOST="carissa@192.168.1.199"

# Project paths
PROJECT_ROOT="/home/carissab/Documents/system_rebellion"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$BACKEND_DIR/logs"
PID_DIR="/tmp/rebellion-pids"

# Banner
show_banner() {
    clear
    echo -e "${MAGENTA}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║      🛑 SYSTEM REBELLION - SHUTDOWN SEQUENCE 🛑          ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# Status display
show_status() {
    local service=$1
    local status=$2
    local message=$3
    
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✅ $service${NC} - $message"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $service${NC} - $message"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}❌ $service${NC} - $message"
    else
        echo -e "${BLUE}🔄 $service${NC} - $message"
    fi
}

# Shutdown Frontend on Dell (local)
shutdown_frontend() {
    echo -e "\n${BLUE}${BOLD}━━━ STEP 1: SHUTTING DOWN FRONTEND ━━━${NC}"
    
    show_status "Frontend" "info" "Stopping frontend dev server..."
    
    # Kill vite processes
    pkill -f "vite" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    
    # Kill the terminal window if PID exists
    if [ -f "$PID_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        kill "$FRONTEND_PID" 2>/dev/null || true
        rm "$PID_DIR/frontend.pid"
    fi
    
    # Verify it's stopped
    sleep 2
    if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
        show_status "Frontend" "success" "Frontend stopped"
    else
        show_status "Frontend" "warning" "Frontend may still be running"
    fi
}

# Shutdown Backend on HP
shutdown_backend() {
    echo -e "\n${BLUE}${BOLD}━━━ STEP 2: SHUTTING DOWN BACKEND ━━━${NC}"
    
    show_status "Backend" "info" "Stopping backend server on HP..."
    
    # Kill uvicorn processes on HP
    ssh "$HP_HOST" "pkill -f 'uvicorn app.main:app' 2>/dev/null || true" || true
    
    # Kill the SSH session if PID exists
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        kill "$BACKEND_PID" 2>/dev/null || true
        rm "$PID_DIR/backend.pid"
    fi
    
    # Verify it's stopped
    sleep 2
    if ! ssh "$HP_HOST" "curl -s http://localhost:8000/health" > /dev/null 2>&1; then
        show_status "Backend" "success" "Backend stopped"
    else
        show_status "Backend" "warning" "Backend may still be running"
    fi
}

# Shutdown Redis on IBM ThinkPad
shutdown_redis() {
    echo -e "\n${BLUE}${BOLD}━━━ STEP 3: SHUTTING DOWN REDIS ━━━${NC}"
    
    show_status "Redis" "info" "Stopping Redis server on IBM ThinkPad..."
    
    # Stop Redis gracefully
    ssh "$IBM_HOST" "redis-cli SHUTDOWN SAVE 2>/dev/null || sudo systemctl stop redis-server 2>/dev/null || sudo pkill redis-server" || true
    
    # Kill any redis-cli monitor processes
    ssh "$IBM_HOST" "pkill -f 'redis-cli MONITOR' 2>/dev/null" || true
    
    # Verify it's stopped
    sleep 2
    if ! ssh "$IBM_HOST" "redis-cli ping" > /dev/null 2>&1; then
        show_status "Redis" "success" "Redis stopped"
    else
        show_status "Redis" "warning" "Redis may still be running"
    fi
}

# Clean up logs
cleanup_logs() {
    echo -e "\n${BLUE}${BOLD}━━━ STEP 4: CLEANING UP LOGS ━━━${NC}"
    
    show_status "Logs" "info" "Cleaning up log files..."
    
    # Remove logs on Dell
    if [ -d "$LOG_DIR" ]; then
        rm -f "$LOG_DIR"/*.log 2>/dev/null || true
        show_status "Logs" "success" "Local logs cleaned"
    fi
    
    # Remove logs on HP
    ssh "$HP_HOST" "rm -f /tmp/backend.log 2>/dev/null" || true
    show_status "Logs" "success" "HP logs cleaned"
    
    # Remove PID directory
    rm -rf "$PID_DIR" 2>/dev/null || true
    show_status "Logs" "success" "PID files cleaned"
}

# Main execution
main() {
    show_banner
    
    echo -e "${BOLD}Shutting down System Rebellion distributed services...${NC}\n"
    
    # Shutdown in reverse order
    shutdown_frontend
    shutdown_backend
    shutdown_redis
    cleanup_logs
    
    # Show success banner
    echo -e "\n${GREEN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║         💤 THE REBELLION IS ASLEEP 💤                    ║"
    echo "║                                                           ║"
    echo "║   All services stopped                                    ║"
    echo "║   Logs cleaned                                            ║"
    echo "║   Ready for next wake-up                                  ║"
    echo "║                                                           ║"
    echo "║   Run wake-the-misfits.sh to start again                 ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# Run main
main "$@"
