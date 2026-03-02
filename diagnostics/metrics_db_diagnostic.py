#!/usr/bin/env python3
"""
Metrics Database Diagnostic Script
Read-only reconnaissance of PostgreSQL metrics tables
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any
import asyncpg
from tabulate import tabulate


class MetricsDatabaseDiagnostic:
    """Diagnostic tool for analyzing metrics database state"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        
    async def connect(self):
        """Establish database connection"""
        try:
            self.conn = await asyncpg.connect(self.db_url)
            print("✅ Connected to PostgreSQL database\n")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
            
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            print("\n✅ Database connection closed")
            
    async def get_all_tables(self) -> List[str]:
        """Get all table names in the database"""
        query = """
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """
        rows = await self.conn.fetch(query)
        return [row['tablename'] for row in rows]
        
    async def get_metrics_tables(self) -> List[str]:
        """Filter tables related to metrics"""
        all_tables = await self.get_all_tables()
        
        # Keywords that indicate metrics-related tables
        metrics_keywords = [
            'metric', 'resource', 'system', 'cpu', 'memory', 
            'disk', 'network', 'swap', 'alert', 'monitor',
            'performance', 'health', 'stats', 'measurement'
        ]
        
        metrics_tables = []
        for table in all_tables:
            if any(keyword in table.lower() for keyword in metrics_keywords):
                metrics_tables.append(table)
                
        return metrics_tables
        
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        info = {
            'table_name': table_name,
            'row_count': 0,
            'columns': [],
            'date_range': None,
            'size': None
        }
        
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table_name};"
        try:
            result = await self.conn.fetchrow(count_query)
            info['row_count'] = result['count']
        except Exception as e:
            info['row_count'] = f"Error: {e}"
            
        # Get columns
        columns_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position;
        """
        try:
            columns = await self.conn.fetch(columns_query, table_name)
            info['columns'] = [
                {
                    'name': col['column_name'],
                    'type': col['data_type'],
                    'nullable': col['is_nullable']
                }
                for col in columns
            ]
        except Exception as e:
            info['columns'] = f"Error: {e}"
            
        # Try to find date range (look for timestamp columns)
        timestamp_columns = [
            col['name'] for col in info['columns'] 
            if isinstance(info['columns'], list) and 
            ('timestamp' in col['type'].lower() or 'date' in col['type'].lower())
        ]
        
        if timestamp_columns and isinstance(info['row_count'], int) and info['row_count'] > 0:
            # Use the first timestamp column found
            ts_col = timestamp_columns[0]
            date_query = f"""
                SELECT 
                    MIN({ts_col}) as earliest,
                    MAX({ts_col}) as latest
                FROM {table_name};
            """
            try:
                result = await self.conn.fetchrow(date_query)
                if result['earliest'] and result['latest']:
                    info['date_range'] = {
                        'earliest': result['earliest'],
                        'latest': result['latest'],
                        'column': ts_col
                    }
            except Exception as e:
                info['date_range'] = f"Error: {e}"
                
        # Get table size
        size_query = """
            SELECT pg_size_pretty(pg_total_relation_size($1)) as size;
        """
        try:
            result = await self.conn.fetchrow(size_query, table_name)
            info['size'] = result['size']
        except Exception as e:
            info['size'] = f"Error: {e}"
            
        return info
        
    async def run_diagnostic(self):
        """Run complete diagnostic analysis"""
        print("=" * 80)
        print("METRICS DATABASE DIAGNOSTIC REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Get all tables
        all_tables = await self.get_all_tables()
        print(f"📊 Total tables in database: {len(all_tables)}")
        
        # Get metrics-related tables
        metrics_tables = await self.get_metrics_tables()
        print(f"📈 Metrics-related tables found: {len(metrics_tables)}")
        print()
        
        if not metrics_tables:
            print("⚠️  No metrics-related tables found!")
            print("\nAll tables in database:")
            for table in all_tables:
                print(f"  - {table}")
            return
            
        # Analyze each metrics table
        print("=" * 80)
        print("DETAILED TABLE ANALYSIS")
        print("=" * 80)
        print()
        
        total_rows = 0
        table_summaries = []
        
        for table_name in metrics_tables:
            print(f"📋 Table: {table_name}")
            print("-" * 80)
            
            info = await self.get_table_info(table_name)
            
            # Row count
            if isinstance(info['row_count'], int):
                print(f"   Rows: {info['row_count']:,}")
                total_rows += info['row_count']
            else:
                print(f"   Rows: {info['row_count']}")
                
            # Size
            print(f"   Size: {info['size']}")
            
            # Date range
            if info['date_range'] and isinstance(info['date_range'], dict):
                dr = info['date_range']
                print(f"   Date Range ({dr['column']}):")
                print(f"     Earliest: {dr['earliest']}")
                print(f"     Latest: {dr['latest']}")
                if dr['earliest'] and dr['latest']:
                    duration = dr['latest'] - dr['earliest']
                    print(f"     Duration: {duration}")
            elif info['date_range']:
                print(f"   Date Range: {info['date_range']}")
            else:
                print(f"   Date Range: No timestamp columns found")
                
            # Columns
            if isinstance(info['columns'], list):
                print(f"   Columns ({len(info['columns'])}):")
                col_table = [
                    [col['name'], col['type'], col['nullable']]
                    for col in info['columns']
                ]
                print(tabulate(
                    col_table,
                    headers=['Column', 'Type', 'Nullable'],
                    tablefmt='simple',
                    colalign=('left', 'left', 'center')
                ))
            else:
                print(f"   Columns: {info['columns']}")
                
            # Add to summary
            table_summaries.append({
                'Table': table_name,
                'Rows': info['row_count'] if isinstance(info['row_count'], int) else 0,
                'Size': info['size'],
                'Columns': len(info['columns']) if isinstance(info['columns'], list) else 0
            })
            
            print()
            
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        
        summary_table = [
            [s['Table'], f"{s['Rows']:,}", s['Size'], s['Columns']]
            for s in table_summaries
        ]
        print(tabulate(
            summary_table,
            headers=['Table', 'Rows', 'Size', 'Columns'],
            tablefmt='grid'
        ))
        
        print()
        print(f"📊 Total metrics tables: {len(metrics_tables)}")
        print(f"📈 Total rows across all metrics tables: {total_rows:,}")
        print()
        
        # Non-metrics tables
        non_metrics = [t for t in all_tables if t not in metrics_tables]
        if non_metrics:
            print("=" * 80)
            print("OTHER TABLES (Non-Metrics)")
            print("=" * 80)
            print()
            for table in non_metrics:
                print(f"  - {table}")
            print()


async def main():
    """Main entry point"""
    
    # Database connection URL - matches System Rebellion backend configuration
    # Default configuration from backend/app/core/database.py
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "system_rebellion"
    DB_USER = "carissab"
    DB_PASSWORD = "Garfield7734"
    
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # You can also override with environment variable
    import os
    db_url = os.getenv('DATABASE_URL', db_url)
    
    diagnostic = MetricsDatabaseDiagnostic(db_url)
    
    try:
        await diagnostic.connect()
        await diagnostic.run_diagnostic()
    finally:
        await diagnostic.close()


if __name__ == "__main__":
    print("\n🔍 Starting Metrics Database Diagnostic...\n")
    asyncio.run(main())
