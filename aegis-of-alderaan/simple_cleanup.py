#!/usr/bin/env python3
"""
Simple API-based cleanup tool
"""

import requests
import json

def main():
    guardian_url = "http://localhost:3001"
    
    print("🧹 Simple Agent Cleanup Tool")
    print("="*40)
    
    try:
        # Get current agents
        response = requests.get(f"{guardian_url}/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"📊 Current agents in system: {len(agents)}")
            
            valid_count = 0
            malformed_count = 0
            
            for agent in agents:
                agent_id = agent.get('agent_id', '')
                hostname = agent.get('hostname', '')
                status = agent.get('status', '')
                
                # Check if malformed
                is_malformed = (
                    '}' in agent_id or 
                    'UNKNOWN' in agent_id or 
                    '${HOSTNAME}' in hostname or
                    len(agent_id) > 15
                )
                
                if is_malformed:
                    print(f"🚨 MALFORMED: '{agent_id}' (hostname: '{hostname}')")
                    malformed_count += 1
                else:
                    print(f"✅ VALID: '{agent_id}' (hostname: '{hostname}') - {status}")
                    valid_count += 1
            
            print(f"\n📊 Summary:")
            print(f"   ✅ Valid agents: {valid_count}")
            print(f"   🚨 Malformed agents: {malformed_count}")
            
            if malformed_count > 0:
                print(f"\n🛠️ TO FIX THE ISSUE:")
                print(f"1. The malformed agents are stored in MongoDB")
                print(f"2. Stop Guardian server (Ctrl+C)")
                print(f"3. Restart Guardian server - this will clear active connections")
                print(f"4. Only start ONE agent (don't start multiple)")
                print(f"5. Check response monitor - should show 1 agent with real metrics")
                print(f"\n💡 The 0% metrics issue comes from malformed agents in database")
                print(f"💡 Restarting Guardian server should solve this")
            else:
                print(f"\n✅ All agents are valid!")
                print(f"💡 If you're still seeing 0% metrics, restart the response monitor")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Make sure Guardian server is running")

if __name__ == "__main__":
    main()
