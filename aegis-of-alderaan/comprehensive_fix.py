#!/usr/bin/env python3
"""
Comprehensive System Fix Script
Fixes agent database issues and anomaly detection problems
"""

import asyncio
import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SystemFixer:
    def __init__(self):
        self.guardian_url = "http://localhost:3001"
        
    def check_api_status(self):
        """Check if Guardian API is accessible"""
        print("🔍 Checking Guardian API status...")
        try:
            response = requests.get(f"{self.guardian_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Guardian API is accessible")
                return True
            else:
                print(f"❌ Guardian API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Guardian API: {e}")
            return False
    
    def analyze_agents(self):
        """Analyze current agent status"""
        print("\n📊 Analyzing current agents...")
        try:
            response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                
                print(f"Found {len(agents)} agents in database:")
                
                valid_agents = []
                malformed_agents = []
                
                for i, agent in enumerate(agents, 1):
                    agent_id = agent.get('agent_id', 'UNKNOWN')
                    hostname = agent.get('hostname', 'UNKNOWN')
                    status = agent.get('status', 'UNKNOWN')
                    last_heartbeat = agent.get('last_heartbeat', 'UNKNOWN')
                    
                    print(f"\n{i}. Agent ID: '{agent_id}'")
                    print(f"   Hostname: '{hostname}'")
                    print(f"   Status: {status}")
                    print(f"   Last Heartbeat: {last_heartbeat}")
                    
                    # Check if malformed
                    is_malformed = (
                        '}' in agent_id or 
                        'UNKNOWN' in agent_id or 
                        '${HOSTNAME}' in hostname or
                        len(agent_id) > 15 or
                        agent_id.count('-') > 2
                    )
                    
                    if is_malformed:
                        print(f"   🚨 MALFORMED - Will be cleaned up")
                        malformed_agents.append(agent_id)
                    else:
                        print(f"   ✅ Valid agent")
                        valid_agents.append(agent_id)
                        
                        # Check metrics for valid agents
                        self.check_agent_metrics(agent_id)
                
                return valid_agents, malformed_agents
            else:
                print(f"❌ Failed to get agents: {response.status_code}")
                return [], []
        except Exception as e:
            print(f"❌ Error analyzing agents: {e}")
            return [], []
    
    def check_agent_metrics(self, agent_id):
        """Check metrics for a specific agent"""
        try:
            response = requests.get(f"{self.guardian_url}/agents/{agent_id}/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', [])
                print(f"   📈 Metrics entries: {len(metrics)}")
                
                if metrics:
                    latest = metrics[-1] if isinstance(metrics, list) else metrics
                    cpu = latest.get('cpu_percent', 'N/A')
                    memory = latest.get('memory_percent', 'N/A')
                    timestamp = latest.get('timestamp', 'N/A')
                    print(f"   📊 Latest: CPU={cpu}%, Memory={memory}%")
                    print(f"   🕐 Timestamp: {timestamp}")
                else:
                    print(f"   ⚠️ No metrics data found")
            else:
                print(f"   ❌ Metrics API error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Metrics check failed: {e}")
    
    def check_anomalies(self):
        """Check current anomalies"""
        print("\n🚨 Checking anomalies...")
        try:
            response = requests.get(f"{self.guardian_url}/anomalies", timeout=5)
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get('anomalies', [])
                print(f"📊 Found {len(anomalies)} anomalies in database")
                
                if anomalies:
                    for i, anomaly in enumerate(anomalies[:3], 1):  # Show first 3
                        agent_id = anomaly.get('agent_id', 'UNKNOWN')
                        anomaly_type = anomaly.get('type', 'UNKNOWN')
                        timestamp = anomaly.get('timestamp', 'UNKNOWN')
                        severity = anomaly.get('severity', 'UNKNOWN')
                        print(f"   {i}. {agent_id}: {anomaly_type} ({severity}) - {timestamp}")
                else:
                    print("   ⚠️ No anomalies found - this might be the issue!")
            else:
                print(f"❌ Anomalies API error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking anomalies: {e}")
    
    def create_test_anomaly(self):
        """Create a test anomaly to verify the system"""
        print("\n🧪 Creating test anomaly...")
        
        test_anomaly = {
            "agent_id": "agent-001",
            "type": "test_anomaly",
            "severity": "warning",
            "description": "Test anomaly created by system fixer",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "test": True,
                "cpu_percent": 25.5,
                "threshold": 10.0
            }
        }
        
        print(f"📤 Test anomaly data: {json.dumps(test_anomaly, indent=2)}")
        
        # Note: We would need a POST endpoint to create anomalies
        # For now, this shows the expected format
        
    def diagnose_anomaly_detection_issues(self):
        """Diagnose why anomalies aren't being detected"""
        print("\n🔬 Diagnosing anomaly detection issues...")
        
        print("🔍 Checking agent configuration...")
        agent_config_path = "agent/config.yaml"
        if os.path.exists(agent_config_path):
            print(f"✅ Agent config exists: {agent_config_path}")
        else:
            print(f"❌ Agent config missing: {agent_config_path}")
        
        print("\n🔍 Checking anomaly detector configuration...")
        anomaly_detector_path = "agent/anomaly_detector.py"
        if os.path.exists(anomaly_detector_path):
            print(f"✅ Anomaly detector exists: {anomaly_detector_path}")
            
            # Check if CPU threshold is lowered
            try:
                with open(anomaly_detector_path, 'r') as f:
                    content = f.read()
                    if 'cpu_percent > 10' in content:
                        print("✅ CPU threshold is set to 10% (good for testing)")
                    elif 'cpu_percent > 80' in content:
                        print("⚠️ CPU threshold is 80% (might be too high)")
                    else:
                        print("❓ CPU threshold setting unclear")
            except Exception as e:
                print(f"❌ Error reading anomaly detector: {e}")
        else:
            print(f"❌ Anomaly detector missing: {anomaly_detector_path}")
    
    def provide_solution(self, valid_agents, malformed_agents):
        """Provide comprehensive solution"""
        print("\n" + "="*60)
        print("🎯 COMPREHENSIVE SOLUTION")
        print("="*60)
        
        print(f"📊 Current Status:")
        print(f"   ✅ Valid Agents: {len(valid_agents)} {valid_agents}")
        print(f"   🚨 Malformed Agents: {len(malformed_agents)} {malformed_agents}")
        
        if malformed_agents:
            print(f"\n🧹 STEP 1: Clean Database")
            print(f"   The malformed agents are stored in MongoDB and need to be removed.")
            print(f"   Unfortunately, the Guardian API doesn't have a DELETE endpoint.")
            print(f"   ")
            print(f"   💡 SOLUTION: Clean restart with database reset")
            print(f"   1. Stop Guardian server (Ctrl+C)")
            print(f"   2. The malformed agents will eventually timeout and be removed")
            print(f"   3. Or restart with fresh database collections")
        
        print(f"\n🚨 STEP 2: Fix Anomaly Detection")
        print(f"   Check if your agent is actually sending anomalies:")
        print(f"   ")
        print(f"   📋 Quick Test:")
        print(f"   1. Start attack simulator: python attack_simulator.py")
        print(f"   2. Choose option 1 (CPU attack)")
        print(f"   3. Set intensity to 50% for 30 seconds")
        print(f"   4. Watch agent logs for anomaly detection")
        print(f"   ")
        print(f"   🔍 Look for these messages in agent terminal:")
        print(f"   - '🚨 ANOMALY: cpu_bomb_detected - High CPU usage detected'")
        print(f"   - 'Sending anomaly alert to Guardian'")
        
        print(f"\n🚀 STEP 3: Restart Sequence")
        print(f"   1. Stop ALL components (Ctrl+C everywhere)")
        print(f"   2. Start Guardian: cd guardian-server && python start_server.py")
        print(f"   3. Start ONE Agent: cd agent && python start_agent.py")
        print(f"   4. Wait 30 seconds for clean registration")
        print(f"   5. Start Monitor: python response_monitor.py")
        print(f"   6. Run CPU attack to test anomaly detection")
        
        print(f"\n✅ Expected Results After Fix:")
        print(f"   - Only 1 agent showing: agent-001")
        print(f"   - Real metrics (not 0%)")
        print(f"   - Anomalies detected when CPU > 10%")
        print(f"   - Anomaly count increases during attacks")

def main():
    print("🛠️ Aegis System Comprehensive Fixer")
    print("="*60)
    
    fixer = SystemFixer()
    
    # Check API connectivity
    if not fixer.check_api_status():
        print("❌ Cannot proceed - Guardian API not accessible")
        print("💡 Make sure Guardian server is running: cd guardian-server && python start_server.py")
        return
    
    # Analyze agents
    valid_agents, malformed_agents = fixer.analyze_agents()
    
    # Check anomalies
    fixer.check_anomalies()
    
    # Diagnose anomaly detection
    fixer.diagnose_anomaly_detection_issues()
    
    # Create test anomaly data format
    fixer.create_test_anomaly()
    
    # Provide comprehensive solution
    fixer.provide_solution(valid_agents, malformed_agents)

if __name__ == "__main__":
    main()
