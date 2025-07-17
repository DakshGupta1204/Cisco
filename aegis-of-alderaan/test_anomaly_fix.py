#!/usr/bin/env python3
"""
Test the Anomaly Communication Fix
This script verifies that anomalies are now being sent to Guardian
"""

import requests
import time
import json
from datetime import datetime

def main():
    print("🔧 Testing Anomaly Communication Fix")
    print("="*50)
    
    guardian_url = "http://localhost:3001"
    
    # Check initial anomaly count
    print("📊 Step 1: Checking initial anomaly count...")
    try:
        response = requests.get(f"{guardian_url}/anomalies", timeout=5)
        if response.status_code == 200:
            data = response.json()
            initial_count = len(data.get('anomalies', []))
            print(f"   Initial anomalies: {initial_count}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Check agent metrics to see current CPU
    print("\n📈 Step 2: Checking current CPU usage...")
    try:
        response = requests.get(f"{guardian_url}/agents/agent-001/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', [])
            if metrics:
                latest = metrics[-1] if isinstance(metrics, list) else metrics
                cpu = latest.get('cpu_percent', 0)
                print(f"   Current CPU: {cpu}%")
                if cpu > 10:
                    print(f"   🚨 CPU > 10% - Should trigger anomaly!")
                else:
                    print(f"   ℹ️ CPU < 10% - Need to run attack to test")
            else:
                print(f"   ⚠️ No metrics found")
        else:
            print(f"   ❌ Metrics API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Metrics check failed: {e}")
    
    print(f"\n🚀 Step 3: Instructions to test the fix")
    print("="*50)
    print("Now test the fix:")
    print()
    print("1. 🛑 RESTART your agent to apply the fix:")
    print("   - Stop agent (Ctrl+C in agent terminal)")
    print("   - Start agent: cd agent && python start_agent.py")
    print("   - Wait for 'Connected to Guardian server'")
    print()
    print("2. 🧪 Run attack simulator:")
    print("   - cd c:\\Users\\mohan\\Desktop\\Cisco\\aegis-of-alderaan")
    print("   - python attack_simulator.py")
    print("   - Choose option 1 (CPU attack)")
    print("   - Set intensity: 70%")
    print("   - Set duration: 60 seconds")
    print()
    print("3. 👀 Watch agent terminal for:")
    print("   - '🚨 ANOMALY: cpu_bomb_detected - High CPU usage detected'")
    print("   - '📤 Anomaly sent to Guardian: cpu_bomb_detected'")
    print()
    print("4. 👀 Watch Guardian terminal for:")
    print("   - 'Received anomaly from agent-001: CPU_SPIKE'")
    print("   - 'Storing anomaly in database'")
    print()
    print("5. 📺 Check response monitor:")
    print("   - 'Recent Anomalies: 1+' (should increase!)")
    print()
    print("✅ THE FIX:")
    print("   - Connected anomaly_detector to communicator")
    print("   - Added anomaly sending in detection loop")
    print("   - Now anomalies should be sent to Guardian!")
    
    print(f"\n⏰ Waiting 30 seconds, then checking again...")
    time.sleep(30)
    
    print(f"\n📊 Step 4: Checking if new anomalies appeared...")
    try:
        response = requests.get(f"{guardian_url}/anomalies", timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_count = len(data.get('anomalies', []))
            new_anomalies = current_count - initial_count
            
            print(f"   Initial: {initial_count}")
            print(f"   Current: {current_count}")
            print(f"   New: {new_anomalies}")
            
            if new_anomalies > 0:
                print(f"   ✅ SUCCESS! New anomalies detected!")
                # Show latest anomaly
                anomalies = data.get('anomalies', [])
                if anomalies:
                    latest_anomaly = anomalies[0]
                    print(f"   Latest: {latest_anomaly.get('type')} from {latest_anomaly.get('agent_id')}")
            else:
                print(f"   ⚠️ No new anomalies yet - keep monitoring or run attack")
        else:
            print(f"   ❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Check failed: {e}")

if __name__ == "__main__":
    main()
