#!/usr/bin/env python3
"""
Simple CPU Attack Test - Guaranteed to trigger detection
"""

import psutil
import time
import threading
import multiprocessing

def aggressive_cpu_load(duration=15):
    """Run aggressive CPU load that should definitely be detected"""
    print(f"🔥 STARTING AGGRESSIVE CPU ATTACK FOR {duration} SECONDS")
    print(f"🖥️  CPU Cores: {psutil.cpu_count()}")
    
    # Get baseline
    baseline_cpu = psutil.cpu_percent(interval=1)
    print(f"📊 Baseline CPU: {baseline_cpu:.1f}%")
    
    def cpu_burner():
        end_time = time.time() + duration
        while time.time() < end_time:
            # Very aggressive CPU burning
            for _ in range(10000000):  # 10 million iterations
                pass
    
    # Start one thread per CPU core
    threads = []
    for i in range(psutil.cpu_count()):
        thread = threading.Thread(target=cpu_burner)
        thread.start()
        threads.append(thread)
        print(f"🚀 Started CPU burner thread {i+1}")
    
    # Monitor CPU during attack
    for second in range(duration):
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        print(f"⏰ {second+1:2d}s - CPU: {cpu:5.1f}% | Memory: {memory:5.1f}%")
        
        if cpu > 80:
            print(f"🚨 HIGH CPU DETECTED: {cpu:.1f}% (Threshold: 80%)")
    
    # Wait for threads
    for thread in threads:
        thread.join()
    
    # Final check
    final_cpu = psutil.cpu_percent(interval=1)
    print(f"✅ Attack completed. Final CPU: {final_cpu:.1f}%")

if __name__ == "__main__":
    print("🎯 AEGIS ATTACK DETECTION TEST")
    print("=" * 50)
    aggressive_cpu_load(15)
    print("=" * 50)
    print("🔍 Check your agent logs for anomaly detection!")
