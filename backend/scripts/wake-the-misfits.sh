#!/bin/bash
# wake-the-misfits.sh - Master orchestration script for System Rebellion
# Run this from Dell (192.168.1.127) to wake all services with auto-restart
# 
# Hotkeys:
#   Super+Shift+W - Wake the rebellion
#   Super+Shift+S - Shutdown the rebellion

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Machine configurations
IBM_HOST="carissa@192.168.1.216"
HP_HOST="carissa@192.168.1.199"
DELL_USER="carissab"

# Project paths
PROJECT_ROOT="/home/carissab/Documents/system_rebellion"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SCRIPTS_DIR="$BACKEND_DIR/scripts"
LOG_DIR="$BACKEND_DIR/logs"

# PID file locations
PID_DIR="/tmp/rebellion-pids"
mkdir -p "$PID_DIR"

# Log file locations
mkdir -p "$LOG_DIR"
REDIS_LOG="$LOG_DIR/redis.log"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
MASTER_LOG="$LOG_DIR/master.log"

# Trap to handle cleanup on exit
trap cleanup EXIT INT TERM

cleanup() {
    echo -e "\n${YELLOW}🛑 Caught signal, cleaning up...${NC}"
    # Don't shutdown services on cleanup, just exit gracefully
    exit 0
}

# Banner
show_banner() {
    clear
    echo -e "${MAGENTA}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║        🚀 SYSTEM REBELLION - WAKE THE MISFITS 🚀         ║"
    echo "║                                                           ║"
    echo "║   Dell (Redis)            → 192.168.1.127:6379          ║"
    echo "║   HP (Backend)            → 192.168.1.199:8000           ║"
    echo "║   Dell (Frontend)         → 192.168.1.127:5173           ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
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

# Check if a service is running
check_service() {
    local service=$1
    local host=$2
    local check_cmd=$3
    
    if [ "$host" = "local" ]; then
        eval "$check_cmd" > /dev/null 2>&1
    else
        ssh "$host" "$check_cmd" > /dev/null 2>&1
    fi
}

# Wake Redis on Dell (local)
wake_redis() {
    echo -e "\n${CYAN}${BOLD}━━━ STEP 1: WAKING REDIS ON DELL (LOCAL) ━━━${NC}"
    
    show_status "Redis" "info" "Starting Redis server locally..."
    
    if bash "$SCRIPTS_DIR/wake-redis.sh" > "$REDIS_LOG" 2>&1; then
        show_status "Redis" "success" "Redis is UP on redis://192.168.1.127:6379"
        return 0
    else
        show_status "Redis" "error" "Failed to start Redis (check $REDIS_LOG)"
        return 1
    fi
}

# Wake Backend on HP
wake_backend() {
    echo -e "\n${CYAN}${BOLD}━━━ STEP 2: WAKING BACKEND ON HP ━━━${NC}"
    
    show_status "Backend" "info" "Checking HP connection..."
    
    if ! ssh -o ConnectTimeout=5 "$HP_HOST" "echo 'connected'" > /dev/null 2>&1; then
        show_status "Backend" "error" "Cannot connect to HP"
        return 1
    fi
    
    show_status "Backend" "success" "HP is reachable"
    
    # Copy the wake script
    show_status "Backend" "info" "Starting backend server..."
    scp -q "$SCRIPTS_DIR/wake-backend.sh" "$HP_HOST:/tmp/" > /dev/null 2>&1
    
    # Start backend in a new terminal window on HP
    # We'll use SSH with a persistent session
    ssh -f "$HP_HOST" "bash /tmp/wake-backend.sh > /tmp/backend.log 2>&1" &
    BACKEND_PID=$!
    echo "$BACKEND_PID" > "$PID_DIR/backend.pid"
    
    # Wait for backend to be ready
    show_status "Backend" "info" "Waiting for backend to start..."
    for i in {1..30}; do
        if ssh "$HP_HOST" "curl -s http://localhost:8000/health" > /dev/null 2>&1; then
            show_status "Backend" "success" "Backend is UP on http://192.168.1.199:8000"
            return 0
        fi
        sleep 1
    done
    
    show_status "Backend" "warning" "Backend may still be starting..."
    return 0
}

# Wake Frontend on Dell (local)
wake_frontend() {
    echo -e "\n${CYAN}${BOLD}━━━ STEP 3: WAKING FRONTEND ON DELL ━━━${NC}"
    
    show_status "Frontend" "info" "Starting frontend dev server..."
    
    # Start frontend in a new xfce4-terminal
    xfce4-terminal \
        --title="System Rebellion - Frontend" \
        --working-directory="$FRONTEND_DIR" \
        --command="bash $SCRIPTS_DIR/wake-frontend.sh" \
        --hold &
    
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > "$PID_DIR/frontend.pid"
    
    # Wait for frontend to be ready
    show_status "Frontend" "info" "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            show_status "Frontend" "success" "Frontend is UP on http://localhost:5173"
            return 0
        fi
        sleep 1
    done
    
    show_status "Frontend" "warning" "Frontend may still be starting..."
    return 0
}

# Monitor services and auto-restart if they crash
monitor_services() {
    echo -e "\n${CYAN}${BOLD}━━━ MONITORING SERVICES (Auto-Restart Enabled) ━━━${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring (services will keep running)${NC}\n"
    
    local check_interval=10
    local redis_down_count=0
    local backend_down_count=0
    local frontend_down_count=0
    
    while true; do
        # Check Redis (local on Dell)
        if check_service "Redis" "local" "redis-cli ping"; then
            if [ $redis_down_count -gt 0 ]; then
                show_status "Redis" "success" "Recovered!"
                redis_down_count=0
            fi
        else
            redis_down_count=$((redis_down_count + 1))
            if [ $redis_down_count -eq 1 ]; then
                show_status "Redis" "warning" "Not responding, attempting restart..."
                wake_redis
            fi
        fi
        
        # Check Backend
        if check_service "Backend" "$HP_HOST" "curl -s http://localhost:8000/health"; then
            if [ $backend_down_count -gt 0 ]; then
                show_status "Backend" "success" "Recovered!"
                backend_down_count=0
            fi
        else
            backend_down_count=$((backend_down_count + 1))
            if [ $backend_down_count -eq 1 ]; then
                show_status "Backend" "warning" "Not responding, attempting restart..."
                wake_backend
            fi
        fi
        
        # Check Frontend
        if check_service "Frontend" "local" "curl -s http://localhost:5173"; then
            if [ $frontend_down_count -gt 0 ]; then
                show_status "Frontend" "success" "Recovered!"
                frontend_down_count=0
            fi
        else
            frontend_down_count=$((frontend_down_count + 1))
            if [ $frontend_down_count -eq 1 ]; then
                show_status "Frontend" "warning" "Not responding, attempting restart..."
                wake_frontend
            fi
        fi
        
        sleep $check_interval
    done
}

# Main execution
main() {
    show_banner
    
    echo -e "${BOLD}Starting System Rebellion distributed services...${NC}\n"
    echo "Logs: $LOG_DIR"
    echo ""
    
    # Start services in sequence
    if ! wake_redis; then
        echo -e "\n${RED}${BOLD}❌ FAILED TO START REDIS${NC}"
        echo "Check logs: $REDIS_LOG"
        exit 1
    fi
    
    sleep 2
    
    if ! wake_backend; then
        echo -e "\n${RED}${BOLD}❌ FAILED TO START BACKEND${NC}"
        echo "Check logs: $BACKEND_LOG"
        exit 1
    fi
    
    sleep 2
    
    if ! wake_frontend; then
        echo -e "\n${RED}${BOLD}❌ FAILED TO START FRONTEND${NC}"
        echo "Check logs: $FRONTEND_LOG"
        exit 1
    fi
    
    # Show success banner
    echo -e "\n${GREEN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║           🎉 THE REBELLION IS AWAKE! 🎉                  ║"
    echo "║                                                           ║"
    echo "║   Redis:    redis://192.168.1.127:6379                   ║"
    echo "║   Backend:  http://192.168.1.199:8000                    ║"
    echo "║   Frontend: http://localhost:5173                        ║"
    echo "║   API Docs: http://192.168.1.199:8000/docs               ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    # Start monitoring
    monitor_services
}

# Run main
main "$@"