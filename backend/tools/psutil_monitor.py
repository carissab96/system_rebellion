"""Utility script to dump psutil system metrics with human-readable summaries.

Usage examples:
    poetry run python tools/psutil_monitor.py
    poetry run python tools/psutil_monitor.py --output psutil_snapshot.json
    poetry run python tools/psutil_monitor.py --summaries-only
"""

from __future__ import annotations

import argparse
import json
import psutil
from datetime import datetime
from typing import Dict, Any


def collect_cpu_metrics() -> Dict[str, Any]:
    cpu_percent_total = psutil.cpu_percent(interval=1)
    cpu_percent_per_cpu = psutil.cpu_percent(interval=None, percpu=True)
    cpu_times = psutil.cpu_times_percent(interval=None, percpu=True)
    return {
        "cpu_percent": cpu_percent_total,
        "cpu_percent_per_cpu": cpu_percent_per_cpu,
        "cpu_times_percent_per_cpu": [times._asdict() for times in cpu_times],
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
    }


def summarize_cpu(metrics: Dict[str, Any]) -> str:
    per_cpu = metrics.get("cpu_percent_per_cpu", [])
    avg_cpu = metrics.get("cpu_percent", 0)
    return (
        f"CPU usage: {avg_cpu:.1f}% avg across {len(per_cpu)} cores"
        if per_cpu else f"CPU usage: {avg_cpu:.1f}%"
    )


def collect_memory_metrics() -> Dict[str, Any]:
    virtual_mem = psutil.virtual_memory()._asdict()
    swap_mem = psutil.swap_memory()._asdict()
    return {
        "virtual_memory": virtual_mem,
        "swap_memory": swap_mem,
    }


def summarize_memory(metrics: Dict[str, Any]) -> str:
    vm = metrics.get("virtual_memory", {})
    total_gb = vm.get("total", 0) / (1024 ** 3)
    used_gb = vm.get("used", 0) / (1024 ** 3)
    percent = vm.get("percent", 0)
    return f"Memory usage: {used_gb:.2f} / {total_gb:.2f} GB ({percent:.1f}%)"


def collect_disk_metrics() -> Dict[str, Any]:
    partitions = [part.mountpoint for part in psutil.disk_partitions(all=False)]
    disk_usage = {
        mountpoint: psutil.disk_usage(mountpoint)._asdict()
        for mountpoint in partitions
    }
    disk_io = psutil.disk_io_counters(perdisk=True)
    return {
        "disk_usage_per_mount": disk_usage,
        "disk_io_counters": {dev: counters._asdict() for dev, counters in disk_io.items()},
    }


def summarize_disk(metrics: Dict[str, Any]) -> str:
    usage = metrics.get("disk_usage_per_mount", {})
    if not usage:
        return "Disk usage: no mounts detected"
    top = []
    for mount, stats in usage.items():
        total_gb = stats.get("total", 0) / (1024 ** 3)
        used_gb = stats.get("used", 0) / (1024 ** 3)
        percent = stats.get("percent", 0)
        top.append(f"{mount}: {used_gb:.2f}/{total_gb:.2f} GB ({percent:.1f}%)")
    return "Disk usage:\n  " + "\n  ".join(top)


def collect_network_metrics() -> Dict[str, Any]:
    net_io = psutil.net_io_counters(pernic=True)
    try:
        connections = psutil.net_connections(kind="inet")
        net_connections = [
            {
                "fd": conn.fd,
                "family": str(conn.family),
                "type": str(conn.type),
                "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                "status": conn.status,
                "pid": conn.pid,
            }
            for conn in connections
        ]
    except (psutil.AccessDenied, psutil.ZombieProcess):
        net_connections = ["Access denied"]

    return {
        "net_io_counters": {iface: counters._asdict() for iface, counters in net_io.items()},
        "net_if_addrs": {
            name: [addr._asdict() for addr in addrs]
            for name, addrs in psutil.net_if_addrs().items()
        },
        "net_if_stats": {
            name: stats._asdict()
            for name, stats in psutil.net_if_stats().items()
        },
        "net_connections": net_connections,
    }


def summarize_network(metrics: Dict[str, Any]) -> str:
    io = metrics.get("net_io_counters", {})
    summaries = []
    for iface, counters in io.items():
        recv_mb = counters.get("bytes_recv", 0) / (1024 ** 2)
        sent_mb = counters.get("bytes_sent", 0) / (1024 ** 2)
        summaries.append(f"{iface}: recv {recv_mb:.2f} MB / sent {sent_mb:.2f} MB")
    if not summaries:
        summaries.append("No network interfaces detected")
    connections = metrics.get("net_connections", [])
    active = sum(1 for conn in connections if isinstance(conn, dict) and conn.get("status") == "ESTABLISHED")
    return "Network IO:\n  " + "\n  ".join(summaries) + f"\nActive connections: {active}"


def write_output_file(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dump psutil metrics with summaries")
    parser.add_argument(
        "--output",
        help="Optional file path to write full JSON metrics",
    )
    parser.add_argument(
        "--summaries-only",
        action="store_true",
        help="Print only the human-readable summaries (no raw JSON)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cpu": collect_cpu_metrics(),
        "memory": collect_memory_metrics(),
        "disk": collect_disk_metrics(),
        "network": collect_network_metrics(),
    }

    if args.output:
        write_output_file(args.output, payload)

    summaries = [
        summarize_cpu(payload["cpu"]),
        summarize_memory(payload["memory"]),
        summarize_disk(payload["disk"]),
        summarize_network(payload["network"]),
    ]

    print("\n".join(summaries))

    if not args.summaries_only:
        print("\n--- RAW METRICS JSON ---")
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
