#!/usr/bin/env python3
"""
Debug script to test real-time metrics collection
"""

import psutil
import time
import asyncio
from datetime import datetime

async def test_metrics():
    print("🔍 Testing Real-Time Metrics Collection")
    print("=" * 60)
    
    for i in range(10):
        print(f"\n📊 Measurement #{i+1}:")
        
        # Test CPU
        cpu = psutil.cpu_percent(interval=0.5)
        print(f"   CPU: {cpu:.1f}%")
        
        # Test Memory
        memory = psutil.virtual_memory()
        print(f"   Memory: {memory.percent:.1f}%")
        
        # Test Disk
        try:
            disk = psutil.disk_usage('C:\\')
            print(f"   Disk: {disk.percent:.1f}%")
        except:
            disk = psutil.disk_usage('.')
            print(f"   Disk: {disk.percent:.1f}%")
        
        # Test with load
        if i == 5:
            print("   🔥 Generating CPU load...")
            end_time = time.time() + 2
            while time.time() < end_time:
                for _ in range(100000):
                    pass
        
        await asyncio.sleep(1)
    
    print("\n✅ If you see varying numbers above, metrics collection is working!")

if __name__ == "__main__":
    asyncio.run(test_metrics())
