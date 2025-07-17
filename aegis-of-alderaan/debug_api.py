#!/usr/bin/env python3
"""
Debug script to check Guardian API responses
"""

import requests
import json

def check_api():
    base_url = "http://localhost:3001"
    
    print("🔍 Checking Guardian API responses...")
    print("=" * 60)
    
    try:
        # Check agents
        print("\n📊 Checking /agents endpoint:")
        r = requests.get(f"{base_url}/agents", timeout=5)
        if r.status_code == 200:
            agents_data = r.json()
            print(f"Status: {r.status_code}")
            print(f"Response: {json.dumps(agents_data, indent=2)}")
            
            # Check metrics for first agent
            if 'agents' in agents_data and agents_data['agents']:
                agent = agents_data['agents'][0]
                agent_id = agent.get('agent_id', 'unknown')
                print(f"\n📈 Checking /agents/{agent_id}/metrics endpoint:")
                
                r2 = requests.get(f"{base_url}/agents/{agent_id}/metrics", timeout=5)
                if r2.status_code == 200:
                    metrics_data = r2.json()
                    print(f"Status: {r2.status_code}")
                    print(f"Response: {json.dumps(metrics_data, indent=2)}")
                else:
                    print(f"❌ Metrics API error: {r2.status_code}")
        else:
            print(f"❌ Agents API error: {r.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api()
