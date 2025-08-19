# debug_dashboard.py - SQLite version
"""
System Rebellion Debug Dashboard (SQLite Edition)
Run this to see EVERYTHING happening in your system in real-time
No fancy UI needed - just pure terminal goodness!
"""

import asyncio
import aiosqlite
import psutil
import aiohttp
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from typing import Dict, Any, List
import os

console = Console()

class SystemRebellionDebugDashboard:
    def __init__(self, db_path: str = "system_rebellion.db", api_base_url: str = "http://localhost:8000"):
        self.db_path = db_path
        self.api_base_url = api_base_url
        self.db = None
        self.session = None
        
        # Track recent events
        self.recent_logs = []
        self.max_logs = 20
        
        # Agent status cache
        self.agent_status = {
            'the_stick': {'status': 'Unknown', 'anxiety': 0, 'paper_bags': 0},
            'hamsters': {'status': 'Unknown', 'steve': 'idle', 'bob': 'idle', 'carl': 'idle'},
            'sir_hawkington': {'status': 'Unknown', 'monocle': 'secure'},
            'meth_snail': {'status': 'Unknown', 'speed': 0},
            'qsp': {'status': 'Unknown', 'phase': 'unknown'},
            'vic_20': {'status': 'Unknown', 'wisdom': 'processing'}
        }
        
    async def connect(self):
        """Connect to database and API"""
        try:
            # Check if database exists
            if not os.path.exists(self.db_path):
                self.log_event("System", f"❌ Database not found at {self.db_path}", "error")
                return
                
            self.db = await aiosqlite.connect(self.db_path)
            self.session = aiohttp.ClientSession()
            self.log_event("System", f"✅ Connected to SQLite database: {self.db_path}", "success")
        except Exception as e:
            self.log_event("System", f"❌ Connection failed: {str(e)}", "error")
    
    async def disconnect(self):
        """Clean up connections"""
        if self.db:
            await self.db.close()
        if self.session:
            await self.session.close()
    
    def log_event(self, source: str, message: str, severity: str = "info"):
        """Add event to recent logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_logs.append({
            'time': timestamp,
            'source': source,
            'message': message,
            'severity': severity
        })
        
        # Keep only recent logs
        if len(self.recent_logs) > self.max_logs:
            self.recent_logs.pop(0)
    
    async def fetch_stick_anxiety(self) -> Dict[str, Any]:
        """Get The Stick's current anxiety status"""
        if not self.db:
            return
            
        try:
            # Get current anxiety level
            async with self.db.execute("""
                SELECT anxiety_level_after, trigger, timestamp
                FROM stick_anxiety_log
                ORDER BY timestamp DESC
                LIMIT 1
            """) as cursor:
                result = await cursor.fetchone()
            
            # Get paper bag inventory
            async with self.db.execute("""
                SELECT 
                    COALESCE(SUM(bags_added), 0) - COALESCE(SUM(bags_consumed), 0) as inventory
                FROM stick_paper_bag_usage
            """) as cursor:
                bags = await cursor.fetchone()
            
            # Get recent triggers
            async with self.db.execute("""
                SELECT trigger, COUNT(*) as count
                FROM stick_anxiety_log
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY trigger
                ORDER BY count DESC
                LIMIT 5
            """) as cursor:
                triggers = await cursor.fetchall()
            
            if result:
                self.agent_status['the_stick'] = {
                    'status': 'ACTIVE',
                    'anxiety': result[0],
                    'paper_bags': bags[0] if bags else 100,
                    'last_trigger': result[1],
                    'triggers': [{'trigger': t[0], 'count': t[1]} for t in triggers]
                }
                
                # Log significant anxiety
                if result[0] > 80:
                    self.log_event("The Stick", f"😱 PANIC MODE! Anxiety at {result[0]:.1f}%", "error")
                elif result[0] > 60:
                    self.log_event("The Stick", f"😰 High anxiety: {result[0]:.1f}%", "warning")
                    
        except Exception as e:
            self.log_event("The Stick", f"Query failed: {str(e)}", "error")
    
    async def fetch_hamster_activity(self):
        """Get Hamster activity"""
        if not self.db:
            return
            
        try:
            # Recent hamster encounters
            async with self.db.execute("""
                SELECT hamsters_present, panic_level, timestamp,
                       steve_location, bob_location, carl_location
                FROM stick_hamster_encounters
                WHERE timestamp > datetime('now', '-5 minutes')
                ORDER BY timestamp DESC
                LIMIT 3
            """) as cursor:
                results = await cursor.fetchall()
            
            if results:
                latest = results[0]
                self.agent_status['hamsters'] = {
                    'status': 'ACTIVE',
                    'steve': latest[3] or 'unknown',
                    'bob': latest[4] or 'unknown',
                    'carl': latest[5] or 'unknown',
                    'panic_level': latest[1]
                }
                
                # Log Bob sightings
                if latest[4]:  # bob_location
                    self.log_event("Hamsters", f"🐹 BOB DETECTED: {latest[4]}", "error")
                    
        except Exception as e:
            self.log_event("Hamsters", f"Query failed: {str(e)}", "error")
    
    async def fetch_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        try:
            # Try API first
            async with self.session.get(f"{self.api_base_url}/metrics/system") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'cpu': data.get('cpu', {}).get('percent', 0),
                        'memory': data.get('memory', {}).get('percent', 0),
                        'disk': data.get('disk', {}).get('percent', 0)
                    }
        except:
            pass
        
        # Fallback to direct psutil
        return {
            'cpu': psutil.cpu_percent(interval=0.1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
    
    async def fetch_database_stats(self) -> Dict[str, int]:
        """Get row counts from key tables"""
        if not self.db:
            return {}
            
        stats = {}
        tables = [
            ('stick_anxiety_log', 'Anxiety Events'),
            ('stick_hamster_encounters', 'Hamster Encounters'),
            ('stick_paper_bag_usage', 'Paper Bags'),
            ('stick_memory_bank', 'Memories'),
            ('metrics', 'Metrics')
        ]
        
        for table, name in tables:
            try:
                async with self.db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                    count = await cursor.fetchone()
                    stats[name] = count[0] if count else 0
            except:
                stats[name] = 0
                
        return stats
    
    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        # Main layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=20),
            Layout(name="logs", size=10)
        )
        
        # Split main area
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="metrics", ratio=1)
        )
        
        # Split agents area
        layout["agents"].split_column(
            Layout(name="stick_status"),
            Layout(name="hamster_status"),
            Layout(name="db_stats")
        )
        
        return layout
    
    def render_header(self) -> Panel:
        """Render header panel"""
        header_text = Text()
        header_text.append("🚨 SYSTEM REBELLION DEBUG DASHBOARD 🚨\n", style="bold red")
        header_text.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ", style="dim")
        header_text.append(f"DB: {os.path.basename(self.db_path)}", style="dim cyan")
        
        return Panel(header_text, border_style="red")
    
    def render_stick_status(self) -> Panel:
        """Render The Stick's status"""
        stick = self.agent_status['the_stick']
        
        # Color code anxiety level
        anxiety = stick.get('anxiety', 0)
        if anxiety > 80:
            anxiety_color = "red on white"
            status_emoji = "😱"
        elif anxiety > 60:
            anxiety_color = "red"
            status_emoji = "😰"
        elif anxiety > 40:
            anxiety_color = "yellow"
            status_emoji = "😟"
        else:
            anxiety_color = "green"
            status_emoji = "😌"
        
        content = f"""
{status_emoji} THE STICK - {stick.get('status', 'Unknown')}
Anxiety Level: [{anxiety_color}]{anxiety:.1f}%[/{anxiety_color}]
Paper Bags: {stick.get('paper_bags', '?')} remaining
Last Trigger: {stick.get('last_trigger', 'None')}
"""
        
        # Add top triggers if available
        if 'triggers' in stick and stick['triggers']:
            content += "\nTop Anxiety Triggers:\n"
            for t in stick['triggers'][:3]:
                content += f"  • {t['trigger']}: {t['count']}x\n"
        
        return Panel(content, title="📏 The Stick Status", border_style="cyan")
    
    def render_hamster_status(self) -> Panel:
        """Render Hamster status"""
        hamsters = self.agent_status['hamsters']
        
        panic_color = {
            'LOW': 'green',
            'MODERATE': 'yellow',
            'HIGH': 'red',
            'MAXIMUM': 'red on white'
        }.get(hamsters.get('panic_level', 'LOW'), 'white')
        
        content = f"""
🐹 HAMSTERS - {hamsters.get('status', 'Unknown')}
Panic Level: [{panic_color}]{hamsters.get('panic_level', 'Unknown')}[/{panic_color}]

Steve: {hamsters.get('steve', 'idle')}
Bob: [{('red' if hamsters.get('bob') != 'idle' else 'green')}]{hamsters.get('bob', 'idle')}[/]
Carl: {hamsters.get('carl', 'idle')}
"""
        
        return Panel(content, title="🐹 Hamster Activity", border_style="yellow")
    
    async def render_db_stats(self) -> Panel:
        """Render database statistics"""
        stats = await self.fetch_database_stats()
        
        table = Table(show_header=False)
        table.add_column("Table", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        
        for name, count in stats.items():
            table.add_row(name, f"{count:,}")
        
        return Panel(table, title="📊 Database Stats", border_style="blue")
    
    def render_logs(self) -> Panel:
        """Render recent logs"""
        log_text = Text()
        
        for log in self.recent_logs[-15:]:  # Show last 15 logs
            color = {
                'info': 'green',
                'warning': 'yellow',
                'error': 'red',
                'success': 'bright_green'
            }.get(log['severity'], 'white')
            
            log_text.append(f"{log['time']} ", style="dim")
            log_text.append(f"[{log['source']}] ", style="cyan")
            log_text.append(f"{log['message']}\n", style=color)
        
        return Panel(log_text, title="📜 Recent Events", border_style="magenta")
    
    def create_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """Create a simple progress bar"""
        filled = int((value / max_value) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color based on value
        if value > 80:
            return f"[red]{bar}[/red]"
        elif value > 60:
            return f"[yellow]{bar}[/yellow]"
        else:
            return f"[green]{bar}[/green]"
    
    async def update_display(self, layout: Layout):
        """Update all display components"""
        # Fetch all data concurrently
        await asyncio.gather(
            self.fetch_stick_anxiety(),
            self.fetch_hamster_activity(),
            return_exceptions=True
        )
        
        # Update layout
        layout["header"].update(self.render_header())
        layout["stick_status"].update(self.render_stick_status())
        layout["hamster_status"].update(self.render_hamster_status())
        layout["db_stats"].update(await self.render_db_stats())
        
        # Update metrics
        metrics = await self.fetch_system_metrics()
        metrics_content = f"""
CPU Usage:    {self.create_bar(metrics['cpu'], 100)} {metrics['cpu']:.1f}%
Memory Usage: {self.create_bar(metrics['memory'], 100)} {metrics['memory']:.1f}%
Disk Usage:   {self.create_bar(metrics['disk'], 100)} {metrics['disk']:.1f}%

Uptime: {self.get_uptime()}
Processes: {len(list(psutil.process_iter()))}
Python Procs: {self.count_python_processes()}
"""
        layout["metrics"].update(Panel(metrics_content, title="📊 System Metrics", border_style="green"))
        layout["logs"].update(self.render_logs())
    
    def get_uptime(self) -> str:
        """Get system uptime as readable string"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def count_python_processes(self) -> int:
        """Count Python processes"""
        count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if 'python' in proc.info['name'].lower():
                    count += 1
            except:
                pass
        return count
    
    async def run(self):
        """Main dashboard loop"""
        await self.connect()
        
        if not self.db:
            console.print("[red]Failed to connect to database. Exiting.[/red]")
            return
        
        layout = self.create_layout()
        
        try:
            with Live(layout, refresh_per_second=1, console=console) as live:
                while True:
                    try:
                        await self.update_display(layout)
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        self.log_event("Dashboard", f"Update error: {str(e)}", "error")
                        await asyncio.sleep(5)
                        
        except KeyboardInterrupt:
            console.print("\n[red]Dashboard stopped by user[/red]")
        finally:
            await self.disconnect()

# Quick check functions for SQLite

async def quick_db_check(db_path: str):
    """Quick database connectivity and data check"""
    console.print("\n[bold cyan]🔍 Quick SQLite Database Check[/bold cyan]\n")
    
    if not os.path.exists(db_path):
        console.print(f"❌ Database not found: {db_path}", style="red")
        return
    
    try:
        db = await aiosqlite.connect(db_path)
        
        # Get file size
        file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        console.print(f"📁 Database size: {file_size:.2f} MB\n")
        
        # Check key tables
        tables_to_check = [
            ('stick_anxiety_log', 'Anxiety Events'),
            ('stick_hamster_encounters', 'Hamster Encounters'),
            ('stick_paper_bag_usage', 'Paper Bag Usage'),
            ('stick_memory_bank', 'Memory Bank'),
            ('metrics', 'System Metrics')
        ]
        
        for table_name, display_name in tables_to_check:
            try:
                # Count records
                async with db.execute(f"SELECT COUNT(*) FROM {table_name}") as cursor:
                    count = await cursor.fetchone()
                    count = count[0] if count else 0
                
                # Get latest timestamp
                async with db.execute(f"SELECT MAX(timestamp) FROM {table_name}") as cursor:
                    latest = await cursor.fetchone()
                    latest = latest[0] if latest and latest[0] else None
                
                console.print(f"✅ {display_name}: {count:,} records")
                if latest:
                    console.print(f"   Latest: {latest}", style="dim")
                    
            except Exception as e:
                console.print(f"❌ {display_name}: Table not found or error", style="red")
        
        # Show some interesting stats
        console.print("\n[bold cyan]📊 Interesting Stats[/bold cyan]\n")
        
        # Peak anxiety
        async with db.execute("""
            SELECT MAX(anxiety_level_after), trigger 
            FROM stick_anxiety_log 
            WHERE anxiety_level_after = (SELECT MAX(anxiety_level_after) FROM stick_anxiety_log)
        """) as cursor:
            peak = await cursor.fetchone()
            if peak and peak[0]:
                console.print(f"🌡️  Peak Anxiety: {peak[0]:.1f}% (Trigger: {peak[1]})")
        
        # Total paper bags consumed
        async with db.execute("SELECT SUM(bags_consumed) FROM stick_paper_bag_usage") as cursor:
            bags = await cursor.fetchone()
            if bags and bags[0]:
                console.print(f"🛍️  Total Paper Bags Consumed: {bags[0]}")
        
        # Bob sightings
        async with db.execute("""
            SELECT COUNT(*) FROM stick_hamster_encounters 
            WHERE bob_location IS NOT NULL
        """) as cursor:
            bob_count = await cursor.fetchone()
            if bob_count:
                console.print(f"🐹  Bob Sightings: {bob_count[0]}")
        
        await db.close()
        
    except Exception as e:
        console.print(f"❌ Database error: {str(e)}", style="red")

async def test_api_endpoints(base_url: str = "http://localhost:8000"):
    """Test key API endpoints"""
    console.print("\n[bold cyan]🔍 API Endpoint Check[/bold cyan]\n")
    
    endpoints = [
        ("/metrics/system", "System Metrics"),
        ("/agents/status", "Agent Status"),
        ("/health", "Health Check"),
        ("/docs", "API Documentation"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint, name in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}", timeout=5) as resp:
                    if resp.status == 200:
                        console.print(f"✅ {name}: OK", style="green")
                    elif resp.status == 404:
                        console.print(f"⚠️  {name}: Not Found (404)", style="yellow")
                    else:
                        console.print(f"⚠️  {name}: Status {resp.status}", style="yellow")
            except aiohttp.ClientConnectorError:
                console.print(f"❌ {name}: Connection refused (is the server running?)", style="red")
            except Exception as e:
                console.print(f"❌ {name}: {str(e)}", style="red")

# Bonus: Direct SQLite queries for debugging
def print_sqlite_queries():
    """Print useful SQLite queries for manual debugging"""
    console.print("\n[bold cyan]🔧 Useful SQLite Queries[/bold cyan]\n")
    
    queries = [
        ("Recent Anxiety Spikes", 
         "SELECT timestamp, anxiety_level_after, trigger FROM stick_anxiety_log WHERE anxiety_level_after > 60 ORDER BY timestamp DESC LIMIT 10;"),
        
        ("Paper Bag Inventory",
         "SELECT (SELECT COALESCE(SUM(bags_added), 0) FROM stick_paper_bag_usage) - (SELECT COALESCE(SUM(bags_consumed), 0) FROM stick_paper_bag_usage) as remaining;"),
        
        ("Bob Activity",
         "SELECT timestamp, bob_location, panic_level FROM stick_hamster_encounters WHERE bob_location IS NOT NULL ORDER BY timestamp DESC LIMIT 5;"),
        
        ("Hourly Anxiety Average",
         "SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour, AVG(anxiety_level_after) as avg_anxiety FROM stick_anxiety_log GROUP BY hour ORDER BY hour DESC LIMIT 24;"),
        
        ("Memory Bank Size",
         "SELECT COUNT(*) as total_memories, COUNT(CASE WHEN never_forget = 1 THEN 1 END) as permanent_memories FROM stick_memory_bank;"),
    ]
    
    for title, query in queries:
        console.print(f"[yellow]{title}:[/yellow]")
        console.print(f"[dim]{query}[/dim]\n")

# Main entry point
async def main():
    """Run the debug dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Rebellion Debug Dashboard (SQLite)")
    parser.add_argument("--db", default="system_rebellion.db",
                       help="SQLite database path (default: system_rebellion.db)")
    parser.add_argument("--api-url", default="http://localhost:8000",
                       help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--quick-check", action="store_true",
                       help="Run quick checks instead of dashboard")
    parser.add_argument("--show-queries", action="store_true",
                       help="Show useful SQLite queries and exit")
    
    args = parser.parse_args()
    
    if args.show_queries:
        print_sqlite_queries()
    elif args.quick_check:
        # Run quick checks
        await quick_db_check(args.db)
        await test_api_endpoints(args.api_url)
    else:
        # Run full dashboard
        console.print("\n[bold red]🚨 SYSTEM REBELLION DEBUG DASHBOARD (SQLite) 🚨[/bold red]\n")
        console.print(f"Database: [cyan]{args.db}[/cyan]")
        console.print(f"API URL: [cyan]{args.api_url}[/cyan]")
        console.print("\nPress [bold]Ctrl+C[/bold] to exit\n")
        
        dashboard = SystemRebellionDebugDashboard(args.db, args.api_url)
        await dashboard.run()

if __name__ == "__main__":
    asyncio.run(main())