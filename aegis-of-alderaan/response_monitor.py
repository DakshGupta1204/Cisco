#!/usr/bin/env python3
"""
Aegis Response Monitor
Monitor how the Aegis system detects and responds to attacks
"""

import time
import requests
import json
from datetime import datetime

class AegisMonitor:
    def __init__(self, guardian_url="http://localhost:3001"):
        self.guardian_url = guardian_url
        
    def check_agent_status(self):
        """Check status of all agents"""
        try:
            response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', []) if isinstance(data, dict) else data
                print(f"📊 Active Agents: {len(agents)}")
                for agent in agents:
                    agent_id = agent.get('agent_id', 'Unknown') if isinstance(agent, dict) else str(agent)
                    status = agent.get('status', 'Unknown') if isinstance(agent, dict) else 'Active'
                    print(f"   🤖 {agent_id} - {status}")
            else:
                print(f"⚠️  Could not fetch agent status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking agents: {e}")
    
    def check_anomalies(self):
        """Check for detected anomalies"""
        try:
            response = requests.get(f"{self.guardian_url}/anomalies", timeout=5)
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get('anomalies', []) if isinstance(data, dict) else data
                print(f"🚨 Recent Anomalies: {len(anomalies)}")
                # Show last 5 anomalies
                recent_anomalies = anomalies[-5:] if len(anomalies) > 5 else anomalies
                for anomaly in recent_anomalies:
                    if isinstance(anomaly, dict):
                        timestamp = anomaly.get('timestamp', 'Unknown')
                        severity = anomaly.get('severity', 'Unknown')
                        desc = anomaly.get('description', 'No description')
                        print(f"   ⚠️  [{timestamp}] {severity}: {desc}")
                    else:
                        print(f"   ⚠️  {anomaly}")
            else:
                print(f"⚠️  Could not fetch anomalies: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking anomalies: {e}")
    
    def check_metrics(self):
        """Check latest system metrics"""
        try:
            # First get list of agents
            agents_response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                agents = agents_data.get('agents', []) if isinstance(agents_data, dict) else agents_data
                if agents:
                    # Get metrics for the first agent
                    agent = agents[0]
                    agent_id = agent.get('agent_id') if isinstance(agent, dict) else str(agent)
                    response = requests.get(f"{self.guardian_url}/agents/{agent_id}/metrics", timeout=5)
                    if response.status_code == 200:
                        metrics_data = response.json()
                        metrics = metrics_data.get('metrics', []) if isinstance(metrics_data, dict) else metrics_data
                        if metrics:
                            latest = metrics[-1] if isinstance(metrics, list) and metrics else metrics
                            if isinstance(latest, dict):
                                print(f"📈 Latest Metrics ({agent_id}):")
                                print(f"   CPU: {latest.get('cpu_percent', 0):.1f}%")
                                print(f"   Memory: {latest.get('memory_percent', 0):.1f}%")
                                print(f"   Disk: {latest.get('disk_percent', 0):.1f}%")
                            else:
                                print(f"📈 Metrics data format unexpected: {type(latest)}")
                        else:
                            print("📈 No metrics data available")
                    else:
                        print(f"⚠️  Could not fetch metrics: {response.status_code}")
                else:
                    print("📈 No agents available for metrics")
            else:
                print(f"⚠️  Could not fetch agents for metrics: {agents_response.status_code}")
        except Exception as e:
            print(f"❌ Error checking metrics: {e}")
    
    def monitor_continuous(self, interval=10):
        """Continuously monitor the system"""
        print("🔍 Starting continuous monitoring...")
        print(f"🔄 Refresh interval: {interval} seconds")
        print("🛑 Press Ctrl+C to stop\n")
        
        try:
            while True:
                print("=" * 60)
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 60)
                
                self.check_agent_status()
                print()
                self.check_metrics()
                print()
                self.check_anomalies()
                
                print(f"\n⏳ Next update in {interval} seconds...\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    monitor = AegisMonitor()
    
    print("=" * 60)
    print("🛡️  Aegis of Alderaan - Response Monitor")
    print("=" * 60)
    print("📋 Choose monitoring mode:")
    print("1. Single status check")
    print("2. Continuous monitoring")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n📊 Single Status Check:")
        print("=" * 40)
        monitor.check_agent_status()
        print()
        monitor.check_metrics()
        print()
        monitor.check_anomalies()
        
    elif choice == "2":
        interval = input("Monitor interval in seconds (default 10): ").strip()
        interval = int(interval) if interval.isdigit() else 10
        monitor.monitor_continuous(interval)
        
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
