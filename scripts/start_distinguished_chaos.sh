#!/bin/bash

# Colors for our distinguished output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🧐 Sir Hawkington's Distinguished Startup Sequence${NC}"
echo -e "${BLUE}===========================================${NC}"

# Check if postgres is running
echo -e "${CYAN}📊 Checking PostgreSQL status...${NC}"
if ! pg_isready &> /dev/null; then
    echo -e "${RED}🚨 PostgreSQL is not running! Starting it...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start postgresql
    else
        # Linux
        sudo service postgresql start
    fi
    sleep 2  # Give postgres time to wake the fuck up
fi

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}🎭 Tmux is not installed. Installing it for proper window management...${NC}"
    sudo apt-get install tmux -y
fi

# Create a new tmux session named "distinguished_chaos"
tmux new-session -d -s distinguished_chaos

# Split the window into three panes
tmux split-window -h
tmux split-window -v

# Database monitoring in bottom right pane
tmux send-keys -t distinguished_chaos:0.2 "echo -e '${CYAN}🐘 PostgreSQL Status:${NC}'" C-m
tmux send-keys -t distinguished_chaos:0.2 "psql -l" C-m
tmux send-keys -t distinguished_chaos:0.2 "echo 'Monitoring database connections...'" C-m
tmux send-keys -t distinguished_chaos:0.2 "echo -e '${CYAN}🐘 PostgreSQL Metrics:${NC}'" C-m
tmux send-keys -t distinguished_chaos:0.2 "watch -n 5 'echo \"=== Database Connections ===\" && \
    psql -c \"SELECT datname, numbackends, xact_commit, xact_rollback, blks_read, blks_hit FROM pg_stat_database WHERE datname IS NOT NULL;\" && \
    echo \"\n=== Longest Running Queries ===\" && \
    psql -c \"SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE query != \'\<IDLE\>\' AND query NOT ILIKE \"%pg_stat_activity%\" ORDER BY duration DESC LIMIT 3;\" && \
    echo \"\n=== Connection Count ===\" && \
    psql -c \"SELECT count(*) FROM pg_stat_activity;\"'" C-m
# Backend startup in left pane with proper fucking settings
tmux send-keys -t distinguished_chaos:0.0 "echo -e '${CYAN}🚀 Initiating Backend Fuckery...${NC}'" C-m
tmux send-keys -t distinguished_chaos:0.0 "source venv/bin/activate" C-m
tmux send-keys -t distinguished_chaos:0.0 "echo -e '${PURPLE}🧠 Setting up the distinguished Django environment...${NC}'" C-m

# Prepare the distinguished Django environment with proper fucking settings
tmux send-keys -t distinguished_chaos:0.0 "echo -e '${PURPLE}🧐 Sir Hawkington is preparing Django for the ball...${NC}'" C-m
tmux send-keys -t distinguished_chaos:0.0 "export DJANGO_SETTINGS_MODULE=config.settings.development" C-m
tmux send-keys -t distinguished_chaos:0.0 "python -c \"import os; print('Django settings module set to: ' + os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT FUCKING SET!'))\"" C-m
tmux send-keys -t distinguished_chaos:0.0 "echo -e '${GREEN}🎩 Django settings properly configured like a gentleman!${NC}'" C-m

# Run the Django server with distinguished elegance
tmux send-keys -t distinguished_chaos:0.0 "python -m uvicorn config.asgi:application --reload --host 0.0.0.0 --port 5000" C-m

# Frontend startup in top right pane
tmux send-keys -t distinguished_chaos:0.1 "echo -e '${CYAN}🎨 Launching Frontend Chaos...${NC}'" C-m
tmux send-keys -t distinguished_chaos:0.1 "cd frontend" C-m
tmux send-keys -t distinguished_chaos:0.1 "npm run dev" C-m

# Attach to the tmux session
tmux attach-session -t distinguished_chaos

echo -e "${GREEN}✨ Distinguished services are running!${NC}"
echo -e "${PURPLE}🧐 Sir Hawkington is monitoring the situation...${NC}"