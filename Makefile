.PHONY: start stop restart dev db-start redis-start backend-start frontend-start monitor clean

# Project paths
PROJECT_ROOT = /home/carissab/Documents/system_rebellion
BACKEND_DIR = $(PROJECT_ROOT)/backend
FRONTEND_DIR = $(PROJECT_ROOT)/frontend

# Start everything
start: db-start redis-start backend-start frontend-start
	@echo "🚀 Full stack is running!"

# Development mode (with logs visible in tmux)
dev:
	@echo "Starting development environment..."
	@make db-start
	@make redis-start
	@tmux new-session -d -s system_rebellion
	@tmux split-window -h -t system_rebellion
	@tmux split-window -v -t system_rebellion
	@tmux send-keys -t system_rebellion:0.0 'cd $(BACKEND_DIR) && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000' C-m
	@tmux send-keys -t system_rebellion:0.1 'valkey-cli MONITOR' C-m
	@tmux send-keys -t system_rebellion:0.2 'cd $(FRONTEND_DIR) && npm run dev' C-m
	@tmux attach -t system_rebellion

# Start individual services
db-start:
	@echo "Starting PostgreSQL..."
	@sudo systemctl start postgresql
	@sleep 2

redis-start:
	@echo "Starting Valkey..."
	@valkey-server --daemonize yes
	@sleep 1

backend-start:
	@echo "Starting FastAPI backend..."
	@cd $(BACKEND_DIR) && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

frontend-start:
	@echo "Starting React frontend..."
	@cd $(FRONTEND_DIR) && npm run dev &

# Monitor Redis/Valkey
monitor:
	valkey-cli MONITOR

# Stop everything
stop:
	@echo "Stopping all services..."
	@pkill -f valkey-server || true
	@pkill -f uvicorn || true
	@pkill -f "npm run dev" || true
	@tmux kill-session -t system_rebellion 2>/dev/null || true
	@echo "✅ All services stopped"

# Restart everything
restart: stop start

# Clean up
clean: stop
	@echo "Cleaning up..."
	@find $(PROJECT_ROOT) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find $(PROJECT_ROOT) -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Help
help:
	@echo "System Rebellion - Development Commands"
	@echo ""
	@echo "  make start    - Start all services in background"
	@echo "  make dev      - Start in tmux with visible logs"
	@echo "  make stop     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make monitor  - Watch Valkey/Redis commands"
	@echo "  make clean    - Stop services and cleanup"