#!/usr/bin/env python3
"""
Quick system check to verify current metrics and test attack detection
"""

import psutil
import time
import threading

def show_current_metrics():
    """Show current system metrics"""
    print("🔍 Current System Metrics:")
    print(f"   CPU: {psutil.cpu_percent(interval=1):.1f}%")
    print(f"   Memory: {psutil.virtual_memory().percent:.1f}%")
    print(f"   Disk: {psutil.disk_usage('.').percent:.1f}%")
    print()

def simple_cpu_test(duration=10):
    """Simple CPU stress test"""
    print(f"🔥 Starting {duration}s CPU stress test...")
    
    def cpu_burner():
        end_time = time.time() + duration
        while time.time() < end_time:
            # Busy loop
            for _ in range(1000000):
                pass
    
    # Start multiple threads
    threads = []
    for _ in range(psutil.cpu_count()):
        thread = threading.Thread(target=cpu_burner)
        thread.start()
        threads.append(thread)
    
    # Monitor during test
    for i in range(duration):
        cpu = psutil.cpu_percent(interval=1)
        print(f"   ⏰ {i+1}s: CPU {cpu:.1f}%")
    
    # Wait for threads to finish
    for thread in threads:
        thread.join()
    
    print("✅ CPU test completed")

if __name__ == "__main__":
    print("🚨 Aegis Attack Detection Test")
    print("=" * 40)
    
    # Show baseline
    show_current_metrics()
    
    # Run test
    simple_cpu_test(10)
    
    # Show after
    time.sleep(2)
    show_current_metrics()
