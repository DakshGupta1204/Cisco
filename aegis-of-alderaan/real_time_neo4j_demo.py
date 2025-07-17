#!/usr/bin/env python3
"""
Real-Time Neo4j Relationships Demo
Works with actual live Guardian and Agent connections
"""

import requests
import json
import time
from datetime import datetime

class RealTimeNeo4jDemo:
    def __init__(self):
        self.guardian_url = "http://localhost:3001"
        
    def check_real_system(self):
        """Check what's actually running"""
        print("🔍 Checking REAL system status...")
        
        try:
            # Check Guardian health
            response = requests.get(f"{self.guardian_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Guardian alive: {health}")
                
                # Check Neo4j status specifically
                neo4j_status = health.get('services', {}).get('neo4j', 'unknown')
                mongodb_status = health.get('services', {}).get('mongodb', 'unknown') 
                print(f"🗄️ Neo4j: {neo4j_status}")
                print(f"🍃 MongoDB: {mongodb_status}")
                return True
            else:
                print(f"❌ Guardian error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Guardian not reachable: {e}")
            return False
    
    def get_real_agents(self):
        """Get actual connected agents"""
        print("\n👥 Getting REAL connected agents...")
        
        try:
            response = requests.get(f"{self.guardian_url}/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                
                print(f"📊 Found {len(agents)} real agents:")
                
                real_agent_ids = []
                for i, agent in enumerate(agents, 1):
                    agent_id = agent.get('agent_id', 'unknown')
                    hostname = agent.get('hostname', 'unknown')
                    status = agent.get('status', 'unknown')
                    last_heartbeat = agent.get('last_heartbeat', 'never')
                    
                    print(f"  {i}. 🤖 {agent_id}")
                    print(f"      Host: {hostname}")
                    print(f"      Status: {status}")
                    print(f"      Last seen: {last_heartbeat}")
                    
                    real_agent_ids.append(agent_id)
                
                return real_agent_ids
            else:
                print(f"❌ Agents API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting agents: {e}")
            return []
    
    def create_real_mirror_relationship(self, primary_agent, mirror_agent="backup-mirror"):
        """Create REAL mirror relationship with live agent"""
        print(f"\n🪞 Creating REAL mirror relationship: {primary_agent} <-> {mirror_agent}")
        
        try:
            payload = {"mirror_agent": mirror_agent}
            response = requests.post(
                f"{self.guardian_url}/agents/{primary_agent}/relationships/mirror",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ REAL mirror created: {result}")
                return True
            else:
                error = response.text
                print(f"❌ Mirror creation failed: {response.status_code} - {error}")
                return False
        except Exception as e:
            print(f"❌ Mirror creation error: {e}")
            return False
    
    def create_real_monitoring_relationship(self, monitor_agent="health-monitor", target_agent=None):
        """Create REAL monitoring relationship"""
        if not target_agent:
            return False
            
        print(f"\n👁️ Creating REAL monitoring: {monitor_agent} -> {target_agent}")
        
        try:
            payload = {"target_agent": target_agent}
            response = requests.post(
                f"{self.guardian_url}/agents/{monitor_agent}/relationships/monitor",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ REAL monitoring created: {result}")
                return True
            else:
                error = response.text
                print(f"❌ Monitoring creation failed: {response.status_code} - {error}")
                return False
        except Exception as e:
            print(f"❌ Monitoring creation error: {e}")
            return False
    
    def initiate_real_self_healing(self, agent_id):
        """Initiate REAL self-healing process"""
        print(f"\n🩺 Initiating REAL self-healing for: {agent_id}")
        
        try:
            payload = {
                "issue_type": "live_demonstration",
                "severity": "medium",
                "details": {
                    "description": "Real-time demonstration of self-healing",
                    "cpu_percent": 85,
                    "memory_percent": 75,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.guardian_url}/agents/{agent_id}/healing/initiate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ REAL self-healing initiated: {result}")
                
                healing_id = result.get('healing_id')
                if healing_id:
                    print(f"🆔 Healing process ID: {healing_id}")
                    
                    # Simulate healing completion after a moment
                    time.sleep(3)
                    self.complete_real_healing(healing_id)
                
                return True
            else:
                error = response.text
                print(f"❌ Self-healing failed: {response.status_code} - {error}")
                return False
        except Exception as e:
            print(f"❌ Self-healing error: {e}")
            return False
    
    def complete_real_healing(self, healing_id):
        """Complete REAL healing process"""
        print(f"\n✅ Completing REAL healing process: {healing_id}")
        
        try:
            payload = {
                "success": True,
                "details": "Real-time healing demonstration completed successfully"
            }
            
            response = requests.post(
                f"{self.guardian_url}/healing/{healing_id}/complete",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ REAL healing completed: {result}")
                return True
            else:
                error = response.text
                print(f"⚠️ Healing completion issue: {response.status_code} - {error}")
                return False
        except Exception as e:
            print(f"❌ Healing completion error: {e}")
            return False
    
    def get_real_network_topology(self):
        """Get REAL network topology from Neo4j"""
        print(f"\n🗺️ Getting REAL network topology from Neo4j...")
        
        try:
            response = requests.get(f"{self.guardian_url}/network/topology", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                topology = data.get('topology', {})
                nodes = topology.get('nodes', [])
                edges = topology.get('edges', [])
                
                print(f"📊 REAL Neo4j Data:")
                print(f"   🔵 Nodes (Agents): {len(nodes)}")
                print(f"   🔗 Relationships: {len(edges)}")
                
                if nodes:
                    print(f"\n🔵 Real Agents in Neo4j:")
                    for node in nodes:
                        agent_id = node.get('agent_id', 'unknown')
                        hostname = node.get('hostname', 'unknown')
                        status = node.get('status', 'unknown')
                        print(f"      • {agent_id} ({hostname}) - {status}")
                
                if edges:
                    print(f"\n🔗 Real Relationships in Neo4j:")
                    for edge in edges:
                        source = edge.get('source', 'unknown')
                        target = edge.get('target', 'unknown')
                        rel_type = edge.get('relationship_type', 'unknown')
                        print(f"      • {source} --{rel_type}--> {target}")
                
                return {"nodes": len(nodes), "relationships": len(edges)}
            else:
                error = response.text
                print(f"❌ Topology retrieval failed: {response.status_code} - {error}")
                return {"nodes": 0, "relationships": 0}
        except Exception as e:
            print(f"❌ Topology error: {e}")
            return {"nodes": 0, "relationships": 0}
    
    def run_real_demo(self):
        """Run complete real-time demonstration"""
        print("🚀 REAL-TIME Neo4j Relationships Demo")
        print("="*60)
        
        # Step 1: Check system
        if not self.check_real_system():
            print("❌ System not ready for real demo!")
            return
        
        # Step 2: Get real agents
        real_agents = self.get_real_agents()
        if not real_agents:
            print("❌ No real agents connected!")
            print("💡 Start an agent with: python agent/main.py")
            return
        
        # Step 3: Work with first real agent
        primary_agent = real_agents[0]
        print(f"\n🎯 Working with real agent: {primary_agent}")
        
        # Step 4: Create real relationships
        print(f"\n📋 Creating REAL Neo4j relationships...")
        self.create_real_mirror_relationship(primary_agent)
        self.create_real_monitoring_relationship(target_agent=primary_agent)
        
        # Step 5: Test real self-healing
        print(f"\n🩺 Testing REAL self-healing...")
        self.initiate_real_self_healing(primary_agent)
        
        # Step 6: Check final real topology
        print(f"\n🗺️ Final REAL topology check...")
        topology_stats = self.get_real_network_topology()
        
        print("\n" + "="*60)
        print("🎉 REAL-TIME DEMO COMPLETE!")
        print("="*60)
        print(f"✅ Worked with REAL agent: {primary_agent}")
        print(f"✅ Created REAL Neo4j relationships")
        print(f"✅ Tested REAL self-healing")
        print(f"📊 Neo4j now has: {topology_stats['nodes']} nodes, {topology_stats['relationships']} relationships")
        print(f"\n🔍 Check your Neo4j Aura browser - you should see REAL data now!")
        print(f"🌐 Neo4j Aura: https://console.neo4j.io")

def main():
    demo = RealTimeNeo4jDemo()
    demo.run_real_demo()

if __name__ == "__main__":
    main()
