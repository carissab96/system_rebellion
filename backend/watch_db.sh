#!/bin/bash
# Watch for database operations ONLY
# Shows SQL statements and vector operations

echo "=== WATCHING DATABASE OPERATIONS ==="
echo "Looking for: INSERT, UPDATE, DELETE, vector operations"
echo "Press Ctrl+C to stop"
echo ""

grep -i --line-buffered -E "(INSERT INTO|UPDATE.*SET|DELETE FROM|vector|embedding|pgvector|Loading embedding|Stored.*vector|Queued vector)"
