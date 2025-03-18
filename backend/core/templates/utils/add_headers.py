# utils/add_headers.py
import os
from copyright_handler import update_file_header

def add_headers_recursive(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_file_header(file_path)

if __name__ == "__main__":
    # Add to core Python files
    add_headers_recursive('core/')
    add_headers_recursive('config/')