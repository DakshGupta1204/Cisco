#!/usr/bin/env python3
"""
Aegis of Alderaan - Attack Simulation Suite
Simulates various network and system attacks to test the resilient protection system
"""

import asyncio
import psutil
import time
import random
import threading
import subprocess
import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

class AttackSimulator:
    def __init__(self):
        self.running = False
        self.attack_threads = []
        
    def log_attack(self, attack_type, details):
        """Log attack details"""
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"🚨 [{timestamp}] ATTACK: {attack_type} - {details}")
        
    # =============================================================================
    # CPU ATTACKS
    # =============================================================================
    
    def cpu_stress_attack(self, duration=30, intensity=90):
        """Simulate high CPU usage attack"""
        self.log_attack("CPU_STRESS", f"Starting {intensity}% CPU load for {duration} seconds")
        self.running = True  # Set running flag
        
        def cpu_burner():
            end_time = time.time() + duration
            while time.time() < end_time and self.running:
                # More aggressive busy loop to consume CPU
                for _ in range(100000):  # Increased from 10000
                    pass
                # Control intensity with smaller sleep
                if intensity < 100:
                    time.sleep(0.0001 * (100 - intensity))
        
        # Start multiple threads for higher CPU usage
        cpu_threads = []
        num_threads = max(1, int(psutil.cpu_count() * intensity / 100))
        print(f"🔥 Starting {num_threads} CPU-intensive threads...")
        
        for i in range(num_threads):
            thread = threading.Thread(target=cpu_burner)
            thread.daemon = True
            thread.start()
            cpu_threads.append(thread)
            print(f"   📈 Thread {i+1} started")
        
        # Wait for attack duration
        time.sleep(duration)
        self.running = False
        
        # Wait for threads to finish
        for thread in cpu_threads:
            thread.join(timeout=2)
        
        print("✅ CPU stress attack completed")
        return cpu_threads
    
    # =============================================================================
    # MEMORY ATTACKS
    # =============================================================================
    
    def memory_leak_attack(self, duration=30, leak_rate=50):
        """Simulate memory leak/exhaustion attack"""
        self.log_attack("MEMORY_LEAK", f"Starting memory leak attack for {duration} seconds")
        
        def memory_leaker():
            memory_hog = []
            end_time = time.time() + duration
            
            while time.time() < end_time and self.running:
                # Allocate memory chunks
                chunk = [0] * (leak_rate * 1024 * 1024)  # leak_rate MB chunks
                memory_hog.append(chunk)
                time.sleep(1)
                
                # Occasionally check if we should stop
                if not self.running:
                    break
            
            # Clean up
            del memory_hog
            
        thread = threading.Thread(target=memory_leaker)
        thread.daemon = True
        thread.start()
        return [thread]
    
    # =============================================================================
    # DISK ATTACKS
    # =============================================================================
    
    def disk_fill_attack(self, duration=30, file_size_mb=100):
        """Simulate disk space exhaustion attack"""
        self.log_attack("DISK_FILL", f"Creating large files to consume disk space")
        
        def disk_filler():
            attack_dir = Path("./attack_temp")
            attack_dir.mkdir(exist_ok=True)
            
            end_time = time.time() + duration
            file_count = 0
            
            while time.time() < end_time and self.running:
                try:
                    file_path = attack_dir / f"attack_file_{file_count}.tmp"
                    
                    # Create large file
                    with open(file_path, 'wb') as f:
                        f.write(b'0' * (file_size_mb * 1024 * 1024))
                    
                    file_count += 1
                    time.sleep(2)
                    
                except Exception as e:
                    self.log_attack("DISK_FILL", f"Failed to create file: {e}")
                    break
            
            # Cleanup
            try:
                import shutil
                shutil.rmtree(attack_dir)
            except:
                pass
                
        thread = threading.Thread(target=disk_filler)
        thread.daemon = True
        thread.start()
        return [thread]
    
    # =============================================================================
    # NETWORK ATTACKS
    # =============================================================================
    
    def network_flood_attack(self, duration=30, target_host="8.8.8.8"):
        """Simulate network flooding attack"""
        self.log_attack("NETWORK_FLOOD", f"Starting network flood to {target_host}")
        
        def network_flooder():
            end_time = time.time() + duration
            
            while time.time() < end_time and self.running:
                try:
                    # Rapid ping requests
                    subprocess.run([
                        "ping", "-n", "1", "-w", "100", target_host
                    ], capture_output=True, timeout=1)
                except:
                    pass
                time.sleep(0.1)
                
        # Start multiple flood threads
        flood_threads = []
        for _ in range(5):
            thread = threading.Thread(target=network_flooder)
            thread.daemon = True
            thread.start()
            flood_threads.append(thread)
            
        return flood_threads
    
    # =============================================================================
    # PROCESS ATTACKS
    # =============================================================================
    
    def process_bomb_attack(self, duration=30, max_processes=50):
        """Simulate fork bomb / process exhaustion attack"""
        self.log_attack("PROCESS_BOMB", f"Starting process bomb attack")
        
        def process_bomber():
            processes = []
            end_time = time.time() + duration
            
            while time.time() < end_time and self.running and len(processes) < max_processes:
                try:
                    # Start dummy processes
                    proc = subprocess.Popen([
                        "ping", "-t", "127.0.0.1"
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    processes.append(proc)
                    time.sleep(0.5)
                except:
                    break
            
            # Cleanup
            for proc in processes:
                try:
                    proc.terminate()
                except:
                    pass
                    
        thread = threading.Thread(target=process_bomber)
        thread.daemon = True
        thread.start()
        return [thread]
    
    # =============================================================================
    # COMBINED ATTACKS
    # =============================================================================
    
    def multi_vector_attack(self, duration=60):
        """Launch multiple attack vectors simultaneously"""
        self.log_attack("MULTI_VECTOR", f"Starting coordinated multi-vector attack for {duration} seconds")
        
        all_threads = []
        
        # CPU stress (lighter for multi-attack)
        all_threads.extend(self.cpu_stress_attack(duration, intensity=60))
        
        # Memory leak (smaller chunks)
        all_threads.extend(self.memory_leak_attack(duration, leak_rate=20))
        
        # Network flood
        all_threads.extend(self.network_flood_attack(duration))
        
        # Disk fill (smaller files)
        all_threads.extend(self.disk_fill_attack(duration, file_size_mb=50))
        
        return all_threads
    
    # =============================================================================
    # STEALTH ATTACKS
    # =============================================================================
    
    def stealth_resource_drain(self, duration=120):
        """Slow, stealthy resource consumption to avoid detection"""
        self.log_attack("STEALTH_DRAIN", f"Starting stealth attack for {duration} seconds")
        
        def stealth_drain():
            memory_hog = []
            end_time = time.time() + duration
            
            while time.time() < end_time and self.running:
                # Very gradual resource consumption
                
                # Slight CPU load
                for _ in range(1000):
                    pass
                
                # Gradual memory consumption (1MB per 10 seconds)
                if int(time.time()) % 10 == 0:
                    chunk = [0] * (1024 * 1024)  # 1MB
                    memory_hog.append(chunk)
                
                time.sleep(5)  # Long sleep to stay under radar
            
            del memory_hog
            
        thread = threading.Thread(target=stealth_drain)
        thread.daemon = True
        thread.start()
        return [thread]
    
    def core_multi_vector_attack(self, duration=60):
        """Launch core attack vectors simultaneously (CPU, Memory, Network only)"""
        self.log_attack("CORE_MULTI_VECTOR", f"Starting coordinated core attack for {duration} seconds")
        
        all_threads = []
        
        # CPU stress (moderate intensity for multi-attack)
        all_threads.extend(self.cpu_stress_attack(duration, intensity=70))
        
        # Memory leak (moderate rate)
        all_threads.extend(self.memory_leak_attack(duration, leak_rate=30))
        
        # Network flood (DDoS simulation)
        all_threads.extend(self.network_flood_attack(duration))
        
        return all_threads
    
    # =============================================================================
    # CONTROL METHODS
    # =============================================================================
    
    def start_attack(self, attack_type="cpu_stress", **kwargs):
        """Start a specific attack"""
        self.running = True
        
        attack_methods = {
            "cpu_stress": self.cpu_stress_attack,
            "memory_leak": self.memory_leak_attack,
            "network_flood": self.network_flood_attack,
            "core_multi_vector": self.core_multi_vector_attack
        }
        
        if attack_type in attack_methods:
            self.attack_threads = attack_methods[attack_type](**kwargs)
            self.log_attack("ATTACK_STARTED", f"{attack_type} attack initiated")
        else:
            print(f"❌ Unknown attack type: {attack_type}")
    
    def stop_attack(self):
        """Stop all running attacks"""
        self.running = False
        self.log_attack("ATTACK_STOPPED", "All attacks terminated")
        
        # Wait for threads to finish
        for thread in self.attack_threads:
            try:
                thread.join(timeout=5)
            except:
                pass
        
        self.attack_threads = []

def main():
    """Interactive attack simulation menu"""
    simulator = AttackSimulator()
    
    print("=" * 70)
    print("🚨 Aegis of Alderaan - Attack Simulation Suite")
    print("=" * 70)
    print("⚠️  WARNING: This will stress your system! Use in test environment only!")
    print("=" * 70)
    
    while True:
        print("\n📋 Available Attacks (Core 4 Types):")
        print("1. CPU Stress Attack (High CPU usage)")
        print("2. Memory Leak Attack (RAM exhaustion)")
        print("3. DDoS Simulation (Network traffic flood)")
        print("4. Network Traffic Spike (Traffic burst)")
        print("5. Multi-Vector Attack (CPU + Memory + Network)")
        print("6. Stop Current Attack")
        print("7. Exit")
        
        try:
            choice = input("\n🎯 Choose attack type (1-7): ").strip()
            
            if choice == "1":
                duration = int(input("Duration (seconds, default 30): ") or "30")
                intensity = int(input("Intensity % (default 90): ") or "90")
                simulator.start_attack("cpu_stress", duration=duration, intensity=intensity)
                
            elif choice == "2":
                duration = int(input("Duration (seconds, default 30): ") or "30")
                leak_rate = int(input("Memory leak rate MB/sec (default 50): ") or "50")
                simulator.start_attack("memory_leak", duration=duration, leak_rate=leak_rate)
                
            elif choice == "3":
                duration = int(input("Duration (seconds, default 30): ") or "30")
                target = input("Target host (default 8.8.8.8): ") or "8.8.8.8"
                simulator.start_attack("network_flood", duration=duration, target_host=target)
                
            elif choice == "4":
                duration = int(input("Duration (seconds, default 30): ") or "30")
                target = input("Target host (default 8.8.8.8): ") or "8.8.8.8"
                simulator.start_attack("network_flood", duration=duration, target_host=target)
                
            elif choice == "5":
                duration = int(input("Duration (seconds, default 60): ") or "60")
                # Multi-vector with only core 4 types
                simulator.start_attack("core_multi_vector", duration=duration)
                
            elif choice == "6":
                simulator.stop_attack()
                
            elif choice == "7":
                simulator.stop_attack()
                print("👋 Attack simulation terminated")
                break
                
            else:
                print("❌ Invalid choice!")
                
        except KeyboardInterrupt:
            simulator.stop_attack()
            print("\n🛑 Attack simulation interrupted")
            break
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
