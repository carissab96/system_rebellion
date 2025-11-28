#!/bin/bash
# Filter backend logs to show only important events
# Usage: ./filter_logs.sh | less
# Or pipe backend output: python main.py 2>&1 | ./filter_logs.sh

grep -E "(✅|❌|🔮|💥|🧐|🖥️|INSERT INTO|UPDATE|DELETE FROM|Loading embedding|Stored.*vector|Queued vector|agent.*initialized|ERROR|CRITICAL)" | \
grep -v "redis" | \
grep -v "websocket" | \
grep -v "heartbeat" | \
grep -v "pub/sub"
