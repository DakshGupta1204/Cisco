#!/usr/bin/env python3
"""
Quick test to verify metrics collection and attack detection
"""

import asyncio
import psutil
import time

async def test_system():
    print("🧪 Testing System Metrics Collection")
    print("=" * 50)
    
    # Test metrics collection
    print("\n📊 Current System Metrics:")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    try:
        disk = psutil.disk_usage('C:\\')
    except:
        disk = psutil.disk_usage('.')
    
    print(f"   CPU: {cpu:.1f}%")
    print(f"   Memory: {memory.percent:.1f}%")
    print(f"   Disk: {disk.percent:.1f}%")
    
    # Test CPU load generation
    print("\n🔥 Testing CPU Load Generation...")
    print("Generating CPU load for 10 seconds...")
    
    end_time = time.time() + 10
    while time.time() < end_time:
        # Busy loop
        for _ in range(100000):
            pass
        
        # Check CPU every 2 seconds
        if int(time.time() - (end_time - 10)) % 2 == 0:
            current_cpu = psutil.cpu_percent(interval=0.1)
            print(f"   Current CPU: {current_cpu:.1f}%")
    
    print("\n✅ Test completed!")
    print("\n💡 If you see high CPU values above, your system should detect attacks.")

if __name__ == "__main__":
    asyncio.run(test_system())
