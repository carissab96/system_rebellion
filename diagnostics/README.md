# Metrics Database Diagnostic Tool

## Purpose

Read-only reconnaissance script to analyze the current state of your PostgreSQL metrics database.

## What It Does

1. Connects to PostgreSQL database
2. Identifies all metrics-related tables
3. For each table, reports:
   - Row count
   - Date range of data (if timestamp columns exist)
   - All columns with types
   - Table size on disk
4. Provides summary statistics

## Setup

### Install Dependencies

```bash
pip install asyncpg tabulate
```

### Configure Database Connection

Edit `metrics_db_diagnostic.py` and update these values:

```python
DB_HOST = "localhost"        # Your PostgreSQL host
DB_PORT = 5432              # Your PostgreSQL port
DB_NAME = "system_rebellion" # Your database name
DB_USER = "carissa"         # Your database user
DB_PASSWORD = "your_password_here"  # Your database password
```

**Alternative:** Use environment variable:

```bash
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

## Usage

```bash
cd /home/carissa/Documents/system_rebellion/diagnostics
python3 metrics_db_diagnostic.py
```

## Output

The script generates a comprehensive report showing:

- **Table List**: All metrics-related tables found
- **Detailed Analysis**: For each table:
  - Row count
  - Disk size
  - Date range (earliest to latest timestamp)
  - Complete column listing with data types
- **Summary Table**: Quick overview of all metrics tables
- **Non-Metrics Tables**: Other tables in the database

## Safety

This script is **READ-ONLY**. It performs only SELECT queries and metadata lookups. No data is modified.

## Example Output

```
🔍 Starting Metrics Database Diagnostic...

✅ Connected to PostgreSQL database

================================================================================
METRICS DATABASE DIAGNOSTIC REPORT
Generated: 2026-01-25 14:15:00
================================================================================

📊 Total tables in database: 25
📈 Metrics-related tables found: 8

================================================================================
DETAILED TABLE ANALYSIS
================================================================================

📋 Table: system_metrics
--------------------------------------------------------------------------------
   Rows: 15,234
   Size: 2.5 MB
   Date Range (timestamp):
     Earliest: 2025-12-01 00:00:00
     Latest: 2026-01-25 14:00:00
     Duration: 55 days, 14:00:00
   Columns (12):
   Column              Type                      Nullable
   ------------------  ------------------------  ----------
   id                  integer                      NO
   timestamp           timestamp without time zone  NO
   cpu_percent         double precision             YES
   memory_percent      double precision             YES
   ...

[... more tables ...]

================================================================================
SUMMARY
================================================================================

+------------------+--------+--------+----------+
| Table            | Rows   | Size   | Columns  |
+==================+========+========+==========+
| system_metrics   | 15,234 | 2.5 MB | 12       |
| resource_alerts  | 1,456  | 512 KB | 8        |
| ...              | ...    | ...    | ...      |
+------------------+--------+--------+----------+

📊 Total metrics tables: 8
📈 Total rows across all metrics tables: 45,678
```

## Troubleshooting

**Connection Failed:**
- Verify PostgreSQL is running
- Check host, port, database name
- Verify user credentials
- Ensure user has SELECT permissions

**No Tables Found:**
- Database might be empty
- Tables might not match metrics keywords
- Check the "OTHER TABLES" section in output

**Permission Denied:**
- User needs SELECT permission on tables
- User needs access to `information_schema` and `pg_tables`
