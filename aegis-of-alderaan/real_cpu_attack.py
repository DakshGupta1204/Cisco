#!/usr/bin/env python3
"""
Real-Time CPU Attack for Live Agent Testing
Triggers actual CPU load to test anomaly detection with live agent
"""

import subprocess
import time
import psutil
import threading

class RealCPUAttack:
    def __init__(self):
        self.attack_running = False
        self.attack_threads = []
        
    def cpu_bomb(self, duration=30, intensity=50):
        """Create real CPU load"""
        print(f"💣 Starting REAL CPU attack - {intensity}% for {duration}s")
        
        # Calculate how many cores to use
        cores = psutil.cpu_count()
        threads_to_use = max(1, int(cores * intensity / 100))
        
        print(f"🔥 Using {threads_to_use} threads on {cores} cores")
        
        self.attack_running = True
        self.attack_threads = []
        
        # Start attack threads
        for i in range(threads_to_use):
            thread = threading.Thread(target=self._cpu_worker, args=(duration,))
            thread.daemon = True
            thread.start()
            self.attack_threads.append(thread)
        
        # Monitor CPU during attack
        start_time = time.time()
        while time.time() - start_time < duration and self.attack_running:
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"📊 Real CPU usage: {cpu_percent:.1f}%")
            
            if cpu_percent > 10:  # Our anomaly threshold
                print(f"🚨 ANOMALY THRESHOLD EXCEEDED! {cpu_percent:.1f}% > 10%")
        
        self.stop_attack()
        print(f"✅ CPU attack finished")
    
    def _cpu_worker(self, duration):
        """Worker thread for CPU load"""
        end_time = time.time() + duration
        
        while time.time() < end_time and self.attack_running:
            # Busy loop to consume CPU
            for _ in range(10000):
                pass
    
    def stop_attack(self):
        """Stop the CPU attack"""
        self.attack_running = False
        for thread in self.attack_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        self.attack_threads.clear()

def main():
    print("💣 REAL-TIME CPU Attack for Live Agent")
    print("="*50)
    print("This will create REAL CPU load to trigger anomaly detection")
    print("Make sure your agent is running with lowered thresholds!")
    print("="*50)
    
    attack = RealCPUAttack()
    
    try:
        # Start with moderate attack
        print("\n🎯 Phase 1: Moderate CPU attack (50% for 30s)")
        attack.cpu_bomb(duration=30, intensity=50)
        
        print("\n⏳ Cooldown period...")
        time.sleep(10)
        
        # More intense attack
        print("\n🎯 Phase 2: High CPU attack (80% for 20s)")
        attack.cpu_bomb(duration=20, intensity=80)
        
        print("\n🎉 REAL CPU attack demonstration complete!")
        print("Check your agent logs and Guardian for anomaly detection!")
        
    except KeyboardInterrupt:
        print("\n🛑 Attack stopped by user")
        attack.stop_attack()
    except Exception as e:
        print(f"\n❌ Attack error: {e}")
        attack.stop_attack()

if __name__ == "__main__":
    main()
