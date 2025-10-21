# debug_dashboard_hardcore.py
"""
System Rebellion Debug Dashboard - HARDCORE MODE
NO FAKE DATA. NO FALLBACKS. FAILS HONESTLY.
If something's broken, you'll know it.
"""

import asyncio
import aiosqlite
import psutil
import aiohttp
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import os
import sys

console = Console()

class HardcoreDebugDashboard:
    def __init__(self, db_path: str, api_base_url: str):
        self.db_path = db_path
        self.api_base_url = api_base_url
        self.db = None
        self.session = None
        self.connected = False
        self.failures = []
        
    async def connect(self):
        """Connect or DIE TRYING"""
        # Check database exists - NO FALLBACKS
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Connect to database - NO TRY/EXCEPT SAFETY NET
        self.db = await aiosqlite.connect(self.db_path)
        
        # Test database is actually working
        await self.db.execute("SELECT 1")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession()
        
        # Test API is reachable
        async with self.session.get(f"{self.api_base_url}/health", timeout=5) as resp:
            if resp.status != 200:
                raise Exception(f"API health check failed: {resp.status}")
        
        self.connected = True
        console.print("[green]✅ ALL CONNECTIONS ESTABLISHED[/green]")
    
    async def fetch_stick_anxiety(self):
        """Get REAL anxiety data or raise exception"""
        # NO DEFAULT VALUES
        cursor = await self.db.execute("""
            SELECT anxiety_level_after, trigger, timestamp
            FROM stick_anxiety_log
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        result = await cursor.fetchone()
        
        if not result:
            raise Exception("No anxiety data found")
        
        # Get ACTUAL paper bag count
        cursor = await self.db.execute("""
            SELECT 
                COALESCE(SUM(bags_added), 0) - COALESCE(SUM(bags_consumed), 0) as inventory
            FROM stick_paper_bag_usage
        """)
        bags = await cursor.fetchone()
        
        return {
            'anxiety': result[0],
            'trigger': result[1],
            'timestamp': result[2],
            'paper_bags': bags[0] if bags else 0  # NOT 100, actual 0
        }
    
    async def fetch_hamster_activity(self):
        """Get REAL hamster data or raise exception"""
        cursor = await self.db.execute("""
            SELECT hamsters_present, panic_level, 
                   steve_location, bob_location, carl_location
            FROM stick_hamster_encounters
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        result = await cursor.fetchone()
        
        if not result:
            raise Exception("No hamster data found")
            
        return {
            'hamsters': result[0],
            'panic': result[1],
            'steve': result[2],
            'bob': result[3],
            'carl': result[4]
        }
    
    async def fetch_system_metrics(self):
        """Get REAL metrics from API - NO FALLBACK TO PSUTIL"""
        async with self.session.get(
            f"{self.api_base_url}/metrics/system",
            timeout=3
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Metrics API failed: {resp.status}")
            
            data = await resp.json()
            
            # Extract ONLY what's actually there
            return {
                'cpu': data['cpu']['percent'],
                'memory': data['memory']['percent'],
                'disk': data['disk']['percent']
            }
    
    async def run(self):
        """Run the dashboard - NO ERROR RECOVERY"""
        # Connect first
        await self.connect()
        
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=1, console=console) as live:
            while True:
                # Update header with current time
                layout["header"].update(Panel(
                    f"[bold red]HARDCORE DEBUG MODE[/bold red]\n{utc_now() DATA",
                    border_style="red"
                ))
                
                # Fetch and display Stick data
                try:
                    stick_data = await self.fetch_stick_anxiety()
                    layout["stick"].update(self.render_stick(stick_data))
                except Exception as e:
                    layout["stick"].update(Panel(
                        f"[red]STICK FAILED: {str(e)}[/red]",
                        title="📏 The Stick",
                        border_style="red"
                    ))
                
                # Fetch and display Hamster data
                try:
                    hamster_data = await self.fetch_hamster_activity()
                    layout["hamsters"].update(self.render_hamsters(hamster_data))
                except Exception as e:
                    layout["hamsters"].update(Panel(
                        f"[red]HAMSTERS FAILED: {str(e)}[/red]",
                        title="🐹 Hamsters",
                        border_style="red"
                    ))
                
                # Fetch and display metrics
                try:
                    metrics = await self.fetch_system_metrics()
                    layout["metrics"].update(self.render_metrics(metrics))
                except Exception as e:
                    layout["metrics"].update(Panel(
                        f"[red]METRICS FAILED: {str(e)}[/red]",
                        title="📊 Metrics",
                        border_style="red"
                    ))
                
                # Database stats - REAL COUNTS ONLY
                try:
                    stats = await self.get_db_stats()
                    layout["stats"].update(self.render_stats(stats))
                except Exception as e:
                    layout["stats"].update(Panel(
                        f"[red]STATS FAILED: {str(e)}[/red]",
                        title="📈 Stats",
                        border_style="red"
                    ))
                
                await asyncio.sleep(1)
    
    def create_layout(self):
        """Create layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="top", size=10),
            Layout(name="bottom", size=10)
        )
        layout["top"].split_row(
            Layout(name="stick"),
            Layout(name="hamsters")
        )
        layout["bottom"].split_row(
            Layout(name="metrics"),
            Layout(name="stats")
        )
        return layout
    
    def render_stick(self, data):
        """Render REAL stick data"""
        anxiety = data['anxiety']
        color = "red" if anxiety > 80 else "yellow" if anxiety > 60 else "green"
        
        return Panel(
            f"Anxiety: [{color}]{anxiety:.1f}%[/{color}]\n"
            f"Trigger: {data['trigger']}\n"
            f"Paper Bags: {data['paper_bags']}\n"
            f"Last Update: {data['timestamp']}",
            title="📏 The Stick - REAL DATA",
            border_style=color
        )
    
    def render_hamsters(self, data):
        """Render REAL hamster data"""
        panic_color = "red" if data['panic'] == "MAXIMUM" else "yellow"
        
        return Panel(
            f"Active: {data['hamsters']}\n"
            f"Panic: [{panic_color}]{data['panic']}[/{panic_color}]\n"
            f"Steve: {data['steve'] or 'NULL'}\n"
            f"Bob: {data['bob'] or 'NULL'}\n"
            f"Carl: {data['carl'] or 'NULL'}",
            title="🐹 Hamsters - REAL DATA",
            border_style=panic_color
        )
    
    def render_metrics(self, data):
        """Render REAL metrics"""
        return Panel(
            f"CPU: {data['cpu']:.1f}%\n"
            f"Memory: {data['memory']:.1f}%\n"
            f"Disk: {data['disk']:.1f}%",
            title="📊 System Metrics - FROM API",
            border_style="green"
        )
    
    async def get_db_stats(self):
        """Get REAL row counts"""
        stats = {}
        
        # These queries WILL FAIL if tables don't exist
        tables = [
            'stick_anxiety_log',
            'stick_hamster_encounters',
            'stick_paper_bag_usage',
            'metrics'
        ]
        
        for table in tables:
            cursor = await self.db.execute(f"SELECT COUNT(*) FROM {table}")
            count = await cursor.fetchone()
            stats[table] = count[0]
            
        return stats
    
    def render_stats(self, stats):
        """Render REAL stats"""
        content = "\n".join([f"{k}: {v}" for k, v in stats.items()])
        return Panel(content, title="📈 Database Stats - ACTUAL COUNTS", border_style="blue")
    
    async def cleanup(self):
        """Clean up connections"""
        if self.db:
            await self.db.close()
        if self.session:
            await self.session.close()

async def main():
    """Run hardcore debug dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hardcore Debug Dashboard - NO FAKE DATA")
    parser.add_argument("--db", required=True, help="SQLite database path (REQUIRED)")
    parser.add_argument("--api", default="http://localhost:8000", help="API URL")
    
    args = parser.parse_args()
    
    console.print("[bold red]HARDCORE DEBUG DASHBOARD[/bold red]")
    console.print("NO FAKE DATA. NO FALLBACKS. REAL OR FAIL.\n")
    
    dashboard = HardcoreDebugDashboard(args.db, args.api)
    
    try:
        await dashboard.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")
    except FileNotFoundError as e:
        console.print(f"\n[red]FILE NOT FOUND: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]FATAL ERROR: {e}[/red]")
        console.print("[red]This is what failure looks like. Fix it.[/red]")
        sys.exit(1)
    finally:
        await dashboard.cleanup()

if __name__ == "__main__":
    asyncio.run(main())