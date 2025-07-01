#!/usr/bin/env python3
"""
Test script to verify the fixes for connection quality metrics and database validation
"""

import asyncio
import sys
import os
sys.path.append('/home/carissab/Documents/mod7/system_rebellion/backend')

from app.optimization.resource_monitor import ResourceMonitor
from app.schemas.metrics import MetricCreate
from datetime import datetime, timezone
from uuid import uuid4

async def test_connection_quality():
    """Test connection quality metrics collection"""
    print("🔍 Testing Connection Quality Metrics Collection...")
    
    monitor = ResourceMonitor()
    await monitor.initialize()
    
    try:
        # Test connection quality directly
        quality_data = await monitor._get_connection_quality()
        
        print(f"✅ Connection Quality Data Collected:")
        print(f"   - Data Available: {quality_data.get('data_available', False)}")
        print(f"   - Average Latency: {quality_data.get('average_latency')} ms")
        print(f"   - Packet Loss: {quality_data.get('packet_loss_percent')}%")
        print(f"   - Connection Stability: {quality_data.get('connection_stability')}")
        print(f"   - Overall Score: {quality_data.get('overall_score')}")
        
        if quality_data.get('error'):
            print(f"   - Error: {quality_data.get('error')}")
        
        # Test full network metrics collection
        print("\n🌐 Testing Full Network Metrics Collection...")
        network_metrics = await monitor._get_throttled_network_metrics()
        
        if 'connection_quality' in network_metrics:
            print("✅ Connection quality included in network metrics")
        else:
            print("❌ Connection quality missing from network metrics")
            
        return quality_data.get('data_available', False)
        
    except Exception as e:
        print(f"❌ Connection Quality Test Failed: {str(e)}")
        return False

def test_database_validation():
    """Test database validation for MetricCreate"""
    print("\n📊 Testing Database Validation...")
    
    try:
        # Test MetricCreate with all required fields
        test_user_id = uuid4()
        
        metric_create = MetricCreate(
            user_id=test_user_id,
            cpu_usage=45.5,
            memory_usage=67.2,
            disk_usage=23.8,
            network={'io_stats': {'bytes_sent': 1024, 'bytes_recv': 2048}},
            process_count=156,
            additional_metrics={'test': 'data'},
            timestamp=datetime.now(timezone.utc)
        )
        
        print("✅ MetricCreate validation successful")
        print(f"   - User ID: {metric_create.user_id}")
        print(f"   - CPU Usage: {metric_create.cpu_usage}%")
        print(f"   - Memory Usage: {metric_create.memory_usage}%")
        print(f"   - Disk Usage: {metric_create.disk_usage}%")
        print(f"   - Network Data: {type(metric_create.network)}")
        print(f"   - Process Count: {metric_create.process_count}")
        print(f"   - Timestamp: {metric_create.timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database Validation Test Failed: {str(e)}")
        return False

async def test_full_metrics_collection():
    """Test full metrics collection including connection quality"""
    print("\n🔄 Testing Full Metrics Collection...")
    
    monitor = ResourceMonitor()
    await monitor.initialize()
    
    try:
        # Collect all metrics
        metrics = await monitor.collect_metrics()
        
        print("✅ Full metrics collection successful")
        print(f"   - Timestamp: {metrics.get('timestamp')}")
        print(f"   - CPU Usage: {metrics.get('cpu_usage')}%")
        print(f"   - Memory Usage: {metrics.get('memory_usage')}%")
        print(f"   - Disk Usage: {metrics.get('disk_usage')}%")
        
        # Check if network metrics include connection quality
        network = metrics.get('network', {})
        if 'connection_quality' in network:
            conn_quality = network['connection_quality']
            print(f"   - Connection Quality Available: {conn_quality.get('data_available', False)}")
            if conn_quality.get('data_available'):
                print(f"     * Average Latency: {conn_quality.get('average_latency')} ms")
                print(f"     * Packet Loss: {conn_quality.get('packet_loss_percent')}%")
            elif conn_quality.get('error'):
                print(f"     * Error: {conn_quality.get('error')}")
        else:
            print("   - Connection Quality: Not included")
            
        return True
        
    except Exception as e:
        print(f"❌ Full Metrics Collection Failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 System Rebellion - Testing Fixes")
    print("=" * 50)
    
    # Test 1: Connection Quality Metrics
    quality_success = await test_connection_quality()
    
    # Test 2: Database Validation
    validation_success = test_database_validation()
    
    # Test 3: Full Metrics Collection
    full_metrics_success = await test_full_metrics_collection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   Connection Quality: {'✅ PASS' if quality_success else '❌ FAIL'}")
    print(f"   Database Validation: {'✅ PASS' if validation_success else '❌ FAIL'}")
    print(f"   Full Metrics Collection: {'✅ PASS' if full_metrics_success else '❌ FAIL'}")
    
    if all([quality_success, validation_success, full_metrics_success]):
        print("\n🎉 All tests passed! Fixes are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
