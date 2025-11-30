#!/bin/bash
# Run backend with logging to file

LOG_FILE="backend_$(date +%Y%m%d_%H%M%S).log"

echo "Starting backend with logging to: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo ""

cd /home/carissa/Documents/system_rebellion/backend
source venv/bin/activate

# Run uvicorn and tee output to both console and file
uvicorn main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee "$LOG_FILE"
