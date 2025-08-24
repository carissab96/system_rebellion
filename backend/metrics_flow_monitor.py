"""
Real-time Metrics Flow Monitor

This script provides a live dashboard showing the flow of metrics through the system,
including collection, processing, and any errors that occur.
"""
import asyncio
import logging
import platform
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricsFlowMonitor:
    def __init__(self):
        self.console = Console()
        self.metrics_history = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = time.time()
        self.last_metrics: Optional[Dict[str, Any]] = None
        self.last_update = time.time()
        
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect real system metrics."""
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'os': platform.system(),
                    'hostname': platform.node(),
                    'cpu_percent': cpu_percent,
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used
                    },
                    'disk': {
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free,
                        'percent': disk.percent
                    },
                    'network': {
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv,
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv
                    }
                },
                'collection_time': time.time()
            }
            
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:  # Keep last 100 metrics
                self.metrics_history.pop(0)
                
            self.last_metrics = metrics
            self.success_count += 1
            self.last_update = time.time()
            return metrics
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error collecting metrics: {e}", exc_info=True)
            raise
    
    async def process_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate processing metrics through the system."""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.1)
            
            # Add processing timestamp
            metrics['processed_at'] = datetime.utcnow().isoformat()
            
            # Add some analysis results
            metrics['analysis'] = {
                'needs_attention': metrics['system']['cpu_percent'] > 80,
                'bottleneck': self._identify_bottleneck(metrics),
                'timestamp': time.time()
            }
            
            return metrics
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing metrics: {e}", exc_info=True)
            raise
    
    def _identify_bottleneck(self, metrics: Dict[str, Any]) -> str:
        """Identify system bottleneck based on metrics."""
        cpu = metrics['system']['cpu_percent']
        memory = metrics['system']['memory']['percent']
        disk = metrics['system']['disk']['percent']
        
        if cpu > 90:
            return 'CPU'
        elif memory > 90:
            return 'Memory'
        elif disk > 90:
            return 'Disk'
        return 'None'
    
    async def run_monitor(self, interval: float = 1.0):
        """Run the metrics collection and display live dashboard."""
        with Live(self._create_dashboard(), refresh_per_second=4) as live:
            while True:
                try:
                    # Collect metrics
                    metrics = await self.collect_metrics()
                    
                    # Process metrics
                    processed_metrics = await self.process_metrics(metrics)
                    
                    # Update dashboard
                    live.update(self._create_dashboard(processed_metrics))
                    
                    # Wait for next interval
                    await asyncio.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[bold red]Stopping metrics monitor...[/]")
                    break
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"Error in monitor loop: {e}")
                    await asyncio.sleep(1)  # Prevent tight error loop
    
    def _create_dashboard(self, metrics: Optional[Dict[str, Any]] = None) -> Panel:
        """Create the live dashboard panel."""
        # Create main layout
        grid = Table.grid(expand=True)
        
        # Add header
        grid.add_row(
            Panel(
                f"[bold blue]Metrics Flow Monitor[/] | "
                f"[green]✓ {self.success_count}[/] | "
                f"[red]✗ {self.error_count}[/] | "
                f"Uptime: {time.time() - self.start_time:.1f}s"
            )
        )
        
        # Add metrics display
        if metrics:
            metrics_table = Table(title="System Metrics", show_header=True, header_style="bold magenta")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", justify="right")
            
            # Add CPU metrics
            metrics_table.add_row("CPU Usage", f"{metrics['system']['cpu_percent']:.1f}%")
            
            # Add memory metrics
            mem = metrics['system']['memory']
            metrics_table.add_row(
                "Memory",
                f"{mem['percent']:.1f}% ({mem['used']/1024/1024:.1f}MB / {mem['total']/1024/1024:.1f}MB)"
            )
            
            # Add disk metrics
            disk = metrics['system']['disk']
            metrics_table.add_row(
                "Disk",
                f"{disk['percent']:.1f}% used ({disk['used']/1024/1024:.1f}GB / {disk['total']/1024/1024:.1f}GB)"
            )
            
            # Add network metrics
            net = metrics['system']['network']
            metrics_table.add_row(
                "Network",
                f"↑ {net['bytes_sent']/1024:.1f}KB / ↓ {net['bytes_recv']/1024:.1f}KB"
            )
            
            # Add analysis
            if 'analysis' in metrics:
                analysis = metrics['analysis']
                metrics_table.add_row("Bottleneck", analysis['bottleneck'])
                metrics_table.add_row("Needs Attention", "✅ Yes" if analysis['needs_attention'] else "❌ No")
            
            grid.add_row(metrics_table)
        
        # Add status
        status = Text()
        status.append("Status: ", style="bold")
        if time.time() - self.last_update < 5:
            status.append("ACTIVE", style="bold green")
        else:
            status.append("STALLED", style="bold red")
        
        grid.add_row(Panel(status))
        
        return Panel(grid, title="[bold]Real-time Metrics Flow[/]", border_style="blue")

async def main():
    """Run the metrics flow monitor."""
    monitor = MetricsFlowMonitor()
    await monitor.run_monitor(interval=1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")
        raise
