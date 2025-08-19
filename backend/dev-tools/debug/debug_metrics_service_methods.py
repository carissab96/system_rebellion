# backend/debug_metrics_service_methods.py
"""
Debug what methods SimplifiedMetricsService actually has
"""

import asyncio
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService

async def debug_metrics_service_methods():
    """Check what methods the SimplifiedMetricsService actually has"""
    print("🔍 DEBUGGING SIMPLIFIED METRICS SERVICE METHODS")
    print("="*60)
    
    try:
        metrics_service = await SimplifiedMetricsService.get_instance()
        
        print(f"📋 SimplifiedMetricsService methods:")
        methods = [method for method in dir(metrics_service) if not method.startswith('_')]
        for method in methods:
            print(f"   • {method}")
        
        # Check if it has get_metrics
        if hasattr(metrics_service, 'get_metrics'):
            print(f"\n✅ Has get_metrics method")
        else:
            print(f"\n❌ NO get_metrics method!")
            
            # Check for similar methods
            possible_methods = [m for m in methods if 'metric' in m.lower()]
            print(f"📊 Possible metrics methods: {possible_methods}")
        
        # Let's also check the class definition
        import inspect
        print(f"\n🔍 Class signature:")
        print(f"   Class: {metrics_service.__class__.__name__}")
        print(f"   Module: {metrics_service.__class__.__module__}")
        
        # Try to see the source
        try:
            class_source = inspect.getsource(metrics_service.__class__)
            if "def get_metrics" in class_source:
                print(f"✅ get_metrics found in source")
            else:
                print(f"❌ get_metrics NOT found in source")
                
                # Look for other metric methods
                lines = class_source.split('\n')
                metric_methods = [line.strip() for line in lines if 'def ' in line and 'metric' in line.lower()]
                print(f"📊 Found metric methods in source: {metric_methods}")
                
        except Exception as e:
            print(f"⚠️ Could not get source: {e}")
        
    except Exception as e:
        print(f"💥 Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_metrics_service_methods())