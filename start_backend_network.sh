#!/bin/bash
# Start backend with network access for HP frontend
# Run this on Dell

cd "$(dirname "$0")/backend"

echo "🚀 Starting System Rebellion Backend (Network Mode)"
echo "📡 Accessible at: http://192.168.1.127:8000"
echo "🔌 WebSocket at: ws://192.168.1.127:8000/ws"
echo ""

source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
