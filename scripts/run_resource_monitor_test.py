#!/usr/bin/env python3
"""
Run the resource monitor performance test with proper Python path handling.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the test script
from scripts.test_resource_monitor import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
