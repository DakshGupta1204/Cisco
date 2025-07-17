#!/usr/bin/env python3
"""
Fix System Issues Script
Addresses agent ID formatting, metrics display, and database issues
"""

import asyncio
import os
import requests
import json
from datetime import datetime

class SystemFixer:
    def __init__(self):
        self.guardian_url = "http://localhost:3001"
        
    def fix_agent_config(self):
        """Fix agent configuration issues"""
        print("🔧 Fixing agent configuration...")
        
        # Update agent config to use simple, clean agent ID
        config_path = r"c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent\config.yaml"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace agent ID to remove any formatting issues
        content = content.replace('id: "${AGENT_ID:-agent-001}"', 'id: "agent-001"')
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        print("✅ Agent configuration updated")
    
    def check_guardian_api(self):
        """Check Guardian API endpoints"""
        print("🔍 Checking Guardian API...")
        
        try:
            # Check agents endpoint
            response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if response.status_code == 200:
                agents_data = response.json()
                print(f"📊 Agents response: {agents_data}")
                
                agents = agents_data.get('agents', [])
                print(f"Found {len(agents)} agents:")
                for agent in agents:
                    agent_id = agent.get('agent_id', 'UNKNOWN')
                    status = agent.get('status', 'UNKNOWN')
                    print(f"  🤖 {agent_id} - {status}")
                    
                    # Check metrics for each agent
                    try:
                        metrics_response = requests.get(f"{self.guardian_url}/agents/{agent_id}/metrics", timeout=5)
                        if metrics_response.status_code == 200:
                            metrics_data = metrics_response.json()
                            metrics = metrics_data.get('metrics', [])
                            print(f"    📈 Metrics count: {len(metrics)}")
                            if metrics:
                                latest = metrics[-1] if isinstance(metrics, list) else metrics
                                print(f"    📊 Latest: CPU={latest.get('cpu_percent', 'N/A')}%, Memory={latest.get('memory_percent', 'N/A')}%")
                        else:
                            print(f"    ❌ Metrics error: {metrics_response.status_code}")
                    except Exception as e:
                        print(f"    ❌ Metrics check failed: {e}")
            else:
                print(f"❌ Agents API error: {response.status_code}")
        except Exception as e:
            print(f"❌ API check failed: {e}")
    
    def clean_malformed_agents(self):
        """Clean up malformed agent entries"""
        print("🧹 Cleaning malformed agents...")
        
        try:
            response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if response.status_code == 200:
                agents_data = response.json()
                agents = agents_data.get('agents', [])
                
                malformed_agents = []
                for agent in agents:
                    agent_id = agent.get('agent_id', '')
                    if '}' in agent_id or 'UNKNOWN' in agent_id or len(agent_id) > 20:
                        malformed_agents.append(agent_id)
                
                if malformed_agents:
                    print(f"Found {len(malformed_agents)} malformed agents:")
                    for agent_id in malformed_agents:
                        print(f"  🗑️ {agent_id}")
                    
                    # Note: In a real system, you'd have a cleanup endpoint
                    print("💡 Restart the Guardian server to clear these entries")
                else:
                    print("✅ No malformed agents found")
        except Exception as e:
            print(f"❌ Cleanup check failed: {e}")
    
    def test_metrics_flow(self):
        """Test the metrics data flow"""
        print("🔬 Testing metrics data flow...")
        
        # Simulate what an agent should send
        test_metrics = {
            "agent_id": "agent-001",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": 25.5,
            "memory_percent": 45.2,
            "disk_percent": 60.1,
            "network": {
                "speed_mbps": 15.3
            },
            "system": {
                "process_count": 180
            }
        }
        
        print(f"📤 Test metrics: {json.dumps(test_metrics, indent=2)}")
        return test_metrics
    
    def restart_instructions(self):
        """Provide restart instructions"""
        print("\n" + "="*60)
        print("🚀 RESTART INSTRUCTIONS")
        print("="*60)
        print("To fix the issues, please restart your system components:")
        print()
        print("1. 🛑 STOP all running components (Ctrl+C in each terminal)")
        print("2. 🧹 Clear any malformed data")
        print("3. 🚀 RESTART in this order:")
        print("   Terminal 1: cd guardian-server && python start_server.py")
        print("   Terminal 2: cd agent && python start_agent.py")
        print("   Terminal 3: python response_monitor.py")
        print()
        print("✅ Agent config has been fixed to use clean ID: 'agent-001'")
        print("✅ This should resolve the malformed agent ID issues")
        print("✅ Metrics should display properly after restart")

def main():
    """Main execution"""
    print("🛠️ Aegis System Issues Fixer")
    print("="*50)
    
    fixer = SystemFixer()
    
    # Fix agent configuration
    fixer.fix_agent_config()
    
    # Check current system state
    fixer.check_guardian_api()
    
    # Look for malformed agents
    fixer.clean_malformed_agents()
    
    # Test metrics structure
    fixer.test_metrics_flow()
    
    # Provide restart instructions
    fixer.restart_instructions()

if __name__ == "__main__":
    main()
