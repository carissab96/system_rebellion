#!/usr/bin/env python3
"""Quick health check for all purified services"""

import asyncio
from datetime import datetime

async def quick_health_check():
    print("\n" + "="*80)
    print(" 🧐 QUICK HEALTH CHECK - ALL PURIFIED SERVICES")
    print("="*80)
    
    services = [
        ('CPU', 'app.services.metrics.simplified_cpu_service', 'SimplifiedCPUService'),
        ('Memory', 'app.services.metrics.simplified_memory_service', 'SimplifiedMemoryService'),
        ('Disk', 'app.services.metrics.simplified_disk_service', 'SimplifiedDiskService'),
        ('Network', 'app.services.metrics.simplified_network_service', 'SimplifiedNetworkService')
    ]
    
    for name, module, class_name in services:
        try:
            mod = __import__(module, fromlist=[class_name])
            service_class = getattr(mod, class_name)
            service = await service_class.get_instance()
            
            if hasattr(service, 'health_check'):
                health = await service.health_check()
                status = health.get('status', 'UNKNOWN')
                print(f"   {name:8}: {status} - {health.get('data_quality', 'N/A')}")
            else:
                print(f"   {name:8}: NO HEALTH CHECK")
                
        except Exception as e:
            print(f"   {name:8}: ERROR - {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_health_check())