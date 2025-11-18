#!/bin/bash
# wake-redis.sh - Start Redis on IBM ThinkPad (headless)
# Run this ON the IBM ThinkPad (192.168.1.216)

set -e

echo "🔴 WAKING REDIS ON IBM THINKPAD..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is already running
if pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}⚠️  Redis is already running. Stopping it first...${NC}"
    pkill redis-server 2>/dev/null || true
    sleep 2
fi

# Clean up any stale Redis data (optional - uncomment if needed)
# echo "🧹 Cleaning stale Redis data..."
# redis-cli FLUSHALL 2>/dev/null || true

# Start Redis server (without sudo - assumes Redis is configured to run as user)
echo "🚀 Starting Redis server..."
if command -v systemctl > /dev/null 2>&1; then
    # Try systemctl first (might work without sudo if configured)
    systemctl --user start redis-server 2>/dev/null || redis-server --daemonize yes
else
    # Fall back to direct redis-server
    redis-server --daemonize yes
fi

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
for i in {1..10}; do
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is UP and responding!${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Redis failed to start after 10 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Verify Redis is listening on correct port
REDIS_PORT=$(redis-cli CONFIG GET port | tail -n 1)
echo "📡 Redis listening on port: $REDIS_PORT"

# Get Redis info
echo "📊 Redis Status:"
redis-cli INFO server | grep -E "redis_version|os|uptime_in_seconds" || true

# Start Redis monitor in background (output to /dev/null to save space)
# Uncomment if you want to monitor Redis commands
# echo "👁️  Starting Redis monitor..."
# redis-cli MONITOR > /dev/null 2>&1 &
# echo $! > /tmp/redis-monitor.pid

echo -e "${GREEN}🎉 REDIS IS AWAKE AND READY!${NC}"
echo "   Connection: redis://192.168.1.216:6379"

exit 0
