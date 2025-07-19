#!/usr/bin/env python3
"""
Anomaly Flow Debug Script
Traces the complete anomaly detection and storage flow
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class AnomalyFlowDebugger:
    def __init__(self):
        self.guardian_url = "http://localhost:3001"
        
    def step1_check_current_state(self):
        """Step 1: Check current anomaly state"""
        print("🔍 STEP 1: Checking Current Anomaly State")
        print("="*50)
        
        try:
            response = requests.get(f"{self.guardian_url}/anomalies", timeout=5)
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get('anomalies', [])
                print(f"📊 Current anomalies in database: {len(anomalies)}")
                
                if anomalies:
                    print("🔍 Latest anomalies:")
                    for i, anomaly in enumerate(anomalies[:3], 1):
                        agent_id = anomaly.get('agent_id', 'N/A')
                        type_val = anomaly.get('type', 'N/A')
                        timestamp = anomaly.get('timestamp', 'N/A')
                        print(f"   {i}. {agent_id}: {type_val} - {timestamp}")
                else:
                    print("   ⚠️ NO ANOMALIES FOUND - This is the problem!")
                    
                return len(anomalies)
            else:
                print(f"❌ API Error: {response.status_code}")
                return -1
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return -1
    
    def step2_check_agent_metrics(self):
        """Step 2: Check if agent is sending metrics"""
        print("\n🔍 STEP 2: Checking Agent Metrics Flow")
        print("="*50)
        
        try:
            response = requests.get(f"{self.guardian_url}/agents/agent-001/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', [])
                print(f"📊 Metrics entries for agent-001: {len(metrics)}")
                
                if metrics:
                    latest = metrics[-1] if isinstance(metrics, list) else metrics
                    cpu = latest.get('cpu_percent', 'N/A')
                    memory = latest.get('memory_percent', 'N/A')
                    timestamp = latest.get('timestamp', 'N/A')
                    
                    print(f"📈 Latest metrics:")
                    print(f"   CPU: {cpu}%")
                    print(f"   Memory: {memory}%")
                    print(f"   Timestamp: {timestamp}")
                    
                    # Check if CPU should trigger anomaly
                    if isinstance(cpu, (int, float)):
                        if cpu > 10:
                            print(f"   🚨 CPU ({cpu}%) > 10% - SHOULD TRIGGER ANOMALY!")
                            return True, cpu
                        else:
                            print(f"   ✅ CPU ({cpu}%) < 10% - No anomaly expected")
                            return False, cpu
                    else:
                        print(f"   ⚠️ CPU data is not numeric: {cpu}")
                        return False, cpu
                else:
                    print("   ❌ No metrics found")
                    return False, 0
            else:
                print(f"❌ Metrics API Error: {response.status_code}")
                return False, 0
        except Exception as e:
            print(f"❌ Metrics check failed: {e}")
            return False, 0
    
    def step3_simulate_high_cpu(self):
        """Step 3: Generate high CPU to trigger anomalies"""
        print("\n🔍 STEP 3: Simulating High CPU Load")
        print("="*50)
        print("💡 To test anomaly detection, we need high CPU load.")
        print("   Run this in a separate terminal:")
        print()
        print("   cd c:\\Users\\mohan\\Desktop\\Cisco\\aegis-of-alderaan")
        print("   python attack_simulator.py")
        print("   Choose option 1 (CPU Stress Attack)")
        print("   Set intensity: 70%")
        print("   Set duration: 60 seconds")
        print()
        print("⏳ Waiting 10 seconds for you to start the attack...")
        
        for i in range(10, 0, -1):
            print(f"   {i}...", end="", flush=True)
            time.sleep(1)
        print(" ✅")
    
    def step4_monitor_real_time(self):
        """Step 4: Monitor anomalies in real-time"""
        print("\n🔍 STEP 4: Real-time Anomaly Monitoring")
        print("="*50)
        print("👀 Monitoring for new anomalies...")
        print("   Press Ctrl+C to stop monitoring")
        
        initial_count = self.step1_check_current_state()
        if initial_count == -1:
            initial_count = 0
        
        try:
            for cycle in range(30):  # Monitor for 30 cycles (about 5 minutes)
                time.sleep(10)  # Check every 10 seconds
                
                print(f"\n🔄 Check #{cycle + 1} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Check metrics
                should_trigger, cpu_val = self.step2_check_agent_metrics()
                
                # Check anomalies
                current_count = self.step1_check_current_state()
                if current_count == -1:
                    current_count = 0
                
                new_anomalies = current_count - initial_count
                
                print(f"📊 Summary:")
                print(f"   CPU: {cpu_val}% {'(Should trigger!)' if should_trigger else '(Normal)'}")
                print(f"   Total anomalies: {current_count}")
                print(f"   New anomalies: {new_anomalies}")
                
                if new_anomalies > 0:
                    print(f"✅ SUCCESS! New anomalies detected!")
                    break
                elif should_trigger:
                    print(f"⚠️ HIGH CPU but no new anomalies - ISSUE CONFIRMED!")
                else:
                    print(f"⏳ Waiting for high CPU load...")
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
    
    def step5_diagnose_communication(self):
        """Step 5: Diagnose communication issues"""
        print("\n🔍 STEP 5: Diagnosing Communication Issues")
        print("="*50)
        
        print("🔍 Common issues and solutions:")
        print()
        print("1. 🤖 Agent not detecting anomalies:")
        print("   - Check agent terminal for '🚨 ANOMALY:' messages")
        print("   - Verify CPU threshold is 10% in anomaly_detector.py")
        print("   - Restart agent if no detection messages")
        print()
        print("2. 📡 Agent detecting but not sending:")
        print("   - Check agent terminal for 'Sending anomaly alert'")
        print("   - Check for WebSocket connection errors")
        print("   - Verify Guardian server URL in agent config")
        print()
        print("3. 🛡️ Guardian not receiving:")
        print("   - Check Guardian terminal for 'Received anomaly from agent-001'")
        print("   - Check WebSocket connection status")
        print("   - Restart Guardian server if needed")
        print()
        print("4. 💾 Guardian not storing:")
        print("   - Check Guardian terminal for 'Storing anomaly in database'")
        print("   - Check MongoDB connection")
        print("   - Check for database errors")
        print()
        print("5. 📊 API not returning stored anomalies:")
        print("   - Check /anomalies endpoint directly")
        print("   - Check MongoDB collections")
        print("   - Restart Guardian server")
    
    def step6_provide_fix(self):
        """Step 6: Provide targeted fix"""
        print("\n🔍 STEP 6: Targeted Fix Instructions")
        print("="*50)
        
        print("🎯 IMMEDIATE FIX SEQUENCE:")
        print()
        print("1. 🛑 Stop all components (Ctrl+C in all terminals)")
        print()
        print("2. 🏠 Start Guardian (Terminal 1):")
        print("   cd c:\\Users\\mohan\\Desktop\\Cisco\\aegis-of-alderaan\\guardian-server")
        print("   python start_server.py")
        print("   ✅ Wait for: 'Guardian Server started on port 3001'")
        print()
        print("3. 🤖 Start Agent (Terminal 2):")
        print("   cd c:\\Users\\mohan\\Desktop\\Cisco\\aegis-of-alderaan\\agent")
        print("   python start_agent.py")
        print("   ✅ Wait for: 'Connected to Guardian server'")
        print("   ✅ Watch for: 'Checking metrics: CPU=XX.X%'")
        print()
        print("4. 🧪 Test Anomaly (Terminal 3):")
        print("   cd c:\\Users\\mohan\\Desktop\\Cisco\\aegis-of-alderaan")
        print("   python attack_simulator.py")
        print("   - Choose option 1")
        print("   - Set intensity: 70%")
        print("   - Set duration: 60 seconds")
        print()
        print("5. 👀 Watch ALL terminals for:")
        print("   Agent: '🚨 ANOMALY: cpu_bomb_detected'")
        print("   Agent: 'Sending anomaly alert to Guardian'")
        print("   Guardian: 'Received anomaly from agent-001'")
        print("   Guardian: 'Storing anomaly in database'")
        print()
        print("6. 📺 Check Monitor (Terminal 4):")
        print("   python response_monitor.py")
        print("   ✅ Should show: 'Recent Anomalies: 1+' (increasing)")

def main():
    print("🧪 Anomaly Flow Debugger")
    print("="*60)
    print("This script will trace why anomalies aren't being updated")
    print("="*60)
    
    debugger = AnomalyFlowDebugger()
    
    # Check current state
    initial_anomalies = debugger.step1_check_current_state()
    
    # Check metrics flow
    debugger.step2_check_agent_metrics()
    
    # Simulate high CPU
    debugger.step3_simulate_high_cpu()
    
    # Monitor real-time
    debugger.step4_monitor_real_time()
    
    # Diagnose communication
    debugger.step5_diagnose_communication()
    
    # Provide fix
    debugger.step6_provide_fix()

if __name__ == "__main__":
    main()
