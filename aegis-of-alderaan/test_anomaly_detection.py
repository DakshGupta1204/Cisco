#!/usr/bin/env python3
"""
Test Anomaly Detection Flow
This script tests if anomaly detection is working properly
"""

import asyncio
import json
import requests
from datetime import datetime

def test_api_endpoints():
    """Test Guardian API endpoints"""
    guardian_url = "http://localhost:3001"
    
    print("🧪 Testing API Endpoints")
    print("="*40)
    
    # Test agents endpoint
    try:
        response = requests.get(f"{guardian_url}/agents", timeout=5)
        print(f"📊 /agents: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"   Found {len(agents)} agents")
            for agent in agents:
                agent_id = agent.get('agent_id')
                print(f"   - {agent_id}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test anomalies endpoint
    try:
        response = requests.get(f"{guardian_url}/anomalies", timeout=5)
        print(f"🚨 /anomalies: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            anomalies = data.get('anomalies', [])
            print(f"   Found {len(anomalies)} anomalies")
            if anomalies:
                latest = anomalies[0]
                print(f"   Latest: {latest.get('type')} from {latest.get('agent_id')}")
            else:
                print("   ⚠️ No anomalies found!")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

def test_metrics_for_agent(agent_id="agent-001"):
    """Test metrics for specific agent"""
    guardian_url = "http://localhost:3001"
    
    print(f"\n📈 Testing Metrics for {agent_id}")
    print("="*40)
    
    try:
        response = requests.get(f"{guardian_url}/agents/{agent_id}/metrics", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', [])
            print(f"Metrics count: {len(metrics)}")
            
            if metrics:
                latest = metrics[-1] if isinstance(metrics, list) else metrics
                cpu = latest.get('cpu_percent', 'N/A')
                memory = latest.get('memory_percent', 'N/A')
                timestamp = latest.get('timestamp', 'N/A')
                
                print(f"Latest metrics:")
                print(f"  CPU: {cpu}%")
                print(f"  Memory: {memory}%")
                print(f"  Timestamp: {timestamp}")
                
                # Check if CPU is above 10% threshold
                if isinstance(cpu, (int, float)) and cpu > 10:
                    print(f"  🚨 CPU ({cpu}%) is above 10% threshold!")
                    print(f"  This should trigger an anomaly!")
                else:
                    print(f"  ✅ CPU ({cpu}%) is below 10% threshold")
            else:
                print("  ⚠️ No metrics data")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def create_manual_test_data():
    """Show what test data should look like"""
    print(f"\n🧪 Expected Test Data Formats")
    print("="*40)
    
    # Sample metrics that should trigger anomaly
    test_metrics = {
        "agent_id": "agent-001",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": 45.5,  # Above 10% threshold
        "memory_percent": 35.2,
        "disk_percent": 60.1
    }
    
    print("📊 Test Metrics (should trigger CPU anomaly):")
    print(json.dumps(test_metrics, indent=2))
    
    # Sample anomaly that should be created
    test_anomaly = {
        "agent_id": "agent-001",
        "type": "cpu_bomb_detected",
        "severity": "critical",
        "description": "High CPU usage detected (>10% threshold)",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "cpu_percent": 45.5,
            "threshold": 10.0,
            "pattern": "cpu_bomb"
        }
    }
    
    print("\n🚨 Expected Anomaly:")
    print(json.dumps(test_anomaly, indent=2))

def check_agent_logs():
    """Instructions for checking agent logs"""
    print(f"\n📋 Agent Log Check Instructions")
    print("="*40)
    print("In your agent terminal, look for these messages:")
    print()
    print("✅ Good signs:")
    print("  - 'Checking metrics: CPU=XX.X%'")
    print("  - '🚨 ANOMALY: cpu_bomb_detected - High CPU usage detected'")
    print("  - 'Sending anomaly alert to Guardian'")
    print("  - 'Anomaly sent successfully'")
    print()
    print("❌ Problem signs:")
    print("  - 'No metrics in buffer yet'")
    print("  - 'Failed to send anomaly'")
    print("  - 'WebSocket connection closed'")
    print()
    print("🔧 If you see problems:")
    print("  1. Check WebSocket connection")
    print("  2. Restart agent")
    print("  3. Check Guardian server logs")

def provide_debugging_steps():
    """Provide step-by-step debugging"""
    print(f"\n🔍 Debugging Steps")
    print("="*40)
    print("1. 🧪 Run attack simulator to generate CPU load:")
    print("   python attack_simulator.py")
    print("   Choose option 1 (CPU attack)")
    print("   Set intensity to 50% for 30 seconds")
    print()
    print("2. 👀 Watch agent terminal for:")
    print("   - 'Checking metrics: CPU=XX.X%'")
    print("   - '🚨 ANOMALY: cpu_bomb_detected'")
    print()
    print("3. 🔍 Check Guardian terminal for:")
    print("   - 'Received anomaly from agent-001'")
    print("   - 'Storing anomaly in database'")
    print()
    print("4. 📊 Check response monitor for:")
    print("   - Anomaly count increasing")
    print("   - Recent anomalies showing")
    print()
    print("5. ✅ If still no anomalies:")
    print("   - Restart all components")
    print("   - Check database connections")
    print("   - Verify CPU threshold is 10% in anomaly_detector.py")

def main():
    print("🧪 Aegis Anomaly Detection Test Suite")
    print("="*50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test metrics for main agent
    test_metrics_for_agent("agent-001")
    
    # Show expected data formats
    create_manual_test_data()
    
    # Provide log checking instructions
    check_agent_logs()
    
    # Provide debugging steps
    provide_debugging_steps()
    
    print(f"\n🎯 Summary")
    print("="*20)
    print("Run this test, then follow the debugging steps.")
    print("The key is to watch all terminals during a CPU attack!")

if __name__ == "__main__":
    main()
