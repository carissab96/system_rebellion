#!/usr/bin/env python3

import os
import sys
import shutil
import json
import logging
import traceback
import subprocess
from typing import Dict, List, Any, Optional
import glob
import re

class SystemRebellionLogger:
    def __init__(self, log_file='system_rebellion_migration.log'):
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Full path for log file
        full_log_path = os.path.join('logs', log_file)
        
        # Configure logging
        self.logger = logging.getLogger('SystemRebellionMigration')
        self.logger.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('🚀 %(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File Handler
        file_handler = logging.FileHandler(full_log_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

class SystemDiagnostics:
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        return {
            "Python Version": sys.version,
            "Python Executable": sys.executable,
            "Operating System": os.name,
            "Platform": sys.platform,
            "Current Directory": os.getcwd(),
            "User": os.getlogin(),
            "Home Directory": os.path.expanduser('~')
        }

    @staticmethod
    def check_dependencies() -> Dict[str, List[str]]:
        dependencies = {
            "python": [],
            "system": []
        }
        
        try:
            # Python dependencies
            pip_result = subprocess.run(
                ['pip', 'freeze'], 
                capture_output=True, 
                text=True
            )
            dependencies['python'] = pip_result.stdout.splitlines()
        except Exception as e:
            print(f"Failed to get Python dependencies: {e}")
        
        return dependencies

class MigrationConfiguration:
    DEFAULT_CONFIG = {
        "project_name": "System Rebellion",
        "source_root": ".",
        "destination_root": "system_rebellion",
        "file_mappings": {
            "python": {
                "core/": "backend/app/",
                "authentication/": "backend/app/auth/",
            },
            "typescript": {
                "src/store/": "frontend/src/store/",
                "src/components/": "frontend/src/components/"
            }
        },
        "ignore_patterns": [
            "*.pyc", "__pycache__", "node_modules", ".git", 
            "*.log", "*.sqlite3", "venv", ".venv"
        ]
    }

    @classmethod
    def generate_config(cls, output_path='migration_config.json'):
        with open(output_path, 'w') as f:
            json.dump(cls.DEFAULT_CONFIG, f, indent=2)
        return cls.DEFAULT_CONFIG

class SystemRebellionMigrator:
    def __init__(self, source_dir=None, destination_dir=None):
        # Use home directory for destination if not specified
        self.source_dir = source_dir or os.getcwd()
        self.destination_dir = destination_dir or os.path.join(os.path.expanduser('~'), 'Documents', 'system_rebellion')
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Log source and destination
        self.logger.info(f"Source Directory: {self.source_dir}")
        self.logger.info(f"Destination Directory: {self.destination_dir}")

    def _setup_logger(self):
        # Create logs directory
        os.makedirs(os.path.join(self.destination_dir, 'logs'), exist_ok=True)
        
        logger = logging.getLogger('SystemRebellionMigration')
        logger.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('🚀 %(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File Handler
        log_file = os.path.join(self.destination_dir, 'logs', 'migration.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger

    def create_project_structure(self):
        """Create new project directory structure"""
        structure = {
            "backend": ["app", "tests", "migrations"],
            "frontend": ["src", "tests"],
            "scripts": [],
            "docs": []
        }
        
        # Create directories
        for top_dir, subdirs in structure.items():
            top_path = os.path.join(self.destination_dir, top_dir)
            os.makedirs(top_path, exist_ok=True)
            
            for subdir in subdirs:
                os.makedirs(os.path.join(top_path, subdir), exist_ok=True)
        
        self.logger.info(f"Project structure created in {self.destination_dir}")

    def migrate_files(self):
        """Migrate files from source to destination"""
        migration_rules = {
            'backend': {
                'source_patterns': [
                    'core/*.py', 
                    'authentication/*.py', 
                    'manage.py', 
                    'requirements.txt'
                ],
                'destination': 'backend/app'
            },
            'frontend': {
                'source_patterns': [
                    'frontend/src/*.ts', 
                    'frontend/src/*.tsx', 
                    'frontend/package.json'
                ],
                'destination': 'frontend/src'
            },
            'root': {
                'source_patterns': [
                    'README.md', 
                    '.gitignore'
                ],
                'destination': '.'
            }
        }

        for category, rules in migration_rules.items():
            for pattern in rules['source_patterns']:
                full_pattern = os.path.join(self.source_dir, pattern)
                destination = os.path.join(self.destination_dir, rules['destination'])
                
                for source_file in glob.glob(full_pattern):
                    dest_file = os.path.join(destination, os.path.basename(source_file))
                    
                    try:
                        shutil.copy2(source_file, dest_file)
                        self.logger.info(f"Migrated: {source_file} -> {dest_file}")
                    except Exception as e:
                        self.logger.error(f"Failed to migrate {source_file}: {e}")

    def transform_imports(self):
        """Transform import statements in migrated Python files"""
        python_files = glob.glob(os.path.join(self.destination_dir, '**/*.py'), recursive=True)
        
        import_transformations = [
            (r'from core\.', 'from app.'),
            (r'from authentication\.', 'from app.auth.'),
            (r'import django', 'import fastapi'),
        ]

        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                modified = False
                for pattern, replacement in import_transformations:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        content = new_content
                        modified = True
                
                if modified:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.logger.info(f"Transformed imports in {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to transform imports in {file_path}: {e}")

    def migrate(self):
        """Execute full migration"""
        try:
            # Ensure destination directory exists
            os.makedirs(self.destination_dir, exist_ok=True)
            
            # Create project structure
            self.create_project_structure()
            
            # Migrate files
            self.migrate_files()
            
            # Transform imports
            self.transform_imports()
            
            self.logger.info("🎉 System Rebellion Migration Complete!")
            
        except Exception as e:
            self.logger.error(f"🚨 Migration Failed: {e}")
            self.logger.error(traceback.format_exc())
            sys.exit(1)

def main():
    # Allow optional source and destination directories
    source_dir = sys.argv[1] if len(sys.argv) > 1 else None
    destination_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    migrator = SystemRebellionMigrator(source_dir, destination_dir)
    migrator.migrate()

if __name__ == "__main__":
    main()


