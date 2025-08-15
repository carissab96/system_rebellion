#!/bin/bash

# Remove old files

echo "Cleaning up backend environment..."

#remove cached files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

#remove old logs
rm -f *.log
rm -f *.sqlite3

echo "Backend cleaned and ready for operation"