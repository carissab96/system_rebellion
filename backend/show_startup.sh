#!/bin/bash
# Show ONLY startup logs - no filtering
# This captures the first 100 lines of backend startup

echo "=== BACKEND STARTUP LOG (first 100 lines) ==="
echo "Waiting for backend to start..."
echo ""

# Capture first 100 lines, then stop
head -n 100
