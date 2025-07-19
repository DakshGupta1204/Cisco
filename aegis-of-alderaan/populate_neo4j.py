#!/usr/bin/env python3
"""
Neo4j Database Population Script
Populate your Neo4j Aura database with sample relationships and test self-healing
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jPopulator:
    def __init__(self, guardian_url="http://localhost:3001"):
        self.guardian_url = guardian_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_guardian_health(self):
        """Check if Guardian is running"""
        try:
            async with self.session.get(f"{self.guardian_url}/health") as response:
                if response.status == 200:
                    health = await response.json()
                    logger.info(f"✅ Guardian healthy: Neo4j={health['services'].get('neo4j', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Guardian error: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to Guardian: {e}")
            return False
    
    async def create_sample_agents_and_relationships(self):
        """Create sample agents and all types of relationships"""
        logger.info("🎯 Creating sample network topology...")
        
        # Sample agents configuration
        agents = [
            {"id": "server-primary", "role": "primary_server"},
            {"id": "server-backup", "role": "backup_server"},
            {"id": "monitor-alpha", "role": "monitoring_node"},
            {"id": "monitor-beta", "role": "monitoring_node"},
            {"id": "edge-gateway", "role": "edge_node"},
            {"id": "load-balancer", "role": "load_balancer"}
        ]
        
        # Step 1: Create mirror relationships
        logger.info("🪞 Creating mirror relationships...")
        
        mirror_pairs = [
            ("server-primary", "server-backup"),
            ("monitor-alpha", "monitor-beta")
        ]
        
        for primary, mirror in mirror_pairs:
            try:
                payload = {"mirror_agent": mirror}
                async with self.session.post(
                    f"{self.guardian_url}/agents/{primary}/relationships/mirror",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Mirror: {primary} <-> {mirror}")
                    else:
                        error = await response.text()
                        logger.warning(f"⚠️ Mirror failed: {error}")
            except Exception as e:
                logger.error(f"❌ Mirror error: {e}")
        
        # Step 2: Create monitoring relationships
        logger.info("👁️ Creating monitoring relationships...")
        
        monitoring_pairs = [
            ("monitor-alpha", "server-primary"),
            ("monitor-alpha", "edge-gateway"),
            ("monitor-beta", "server-backup"),
            ("monitor-beta", "load-balancer"),
            ("load-balancer", "server-primary"),
            ("load-balancer", "server-backup")
        ]
        
        for monitor, target in monitoring_pairs:
            try:
                payload = {"target_agent": target}
                async with self.session.post(
                    f"{self.guardian_url}/agents/{monitor}/relationships/monitor",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Monitor: {monitor} -> {target}")
                    else:
                        error = await response.text()
                        logger.warning(f"⚠️ Monitor failed: {error}")
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
        
        # Step 3: Create network connections
        logger.info("🌐 Creating network connections...")
        
        network_connections = [
            ("server-primary", "load-balancer", "SERVES_TRAFFIC"),
            ("server-backup", "load-balancer", "BACKUP_ROUTE"),
            ("edge-gateway", "monitor-alpha", "REPORTS_TO"),
            ("edge-gateway", "server-primary", "CONNECTS_TO"),
            ("monitor-alpha", "monitor-beta", "COMMUNICATES_WITH"),
            ("load-balancer", "edge-gateway", "ROUTES_TO")
        ]
        
        for agent1, agent2, conn_type in network_connections:
            try:
                payload = {
                    "target_agent": agent2,
                    "connection_type": conn_type
                }
                async with self.session.post(
                    f"{self.guardian_url}/agents/{agent1}/relationships/connect",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Connection: {agent1} -{conn_type}-> {agent2}")
                    else:
                        error = await response.text()
                        logger.warning(f"⚠️ Connection failed: {error}")
            except Exception as e:
                logger.error(f"❌ Connection error: {e}")
        
        # Step 4: Setup comprehensive mirroring
        logger.info("⚙️ Setting up comprehensive mirroring...")
        
        try:
            mirror_configs = [
                {"agent_id": "server-backup", "type": "active", "priority": 1},
                {"agent_id": "monitor-beta", "type": "backup", "priority": 2}
            ]
            
            payload = {"mirrors": mirror_configs}
            async with self.session.post(
                f"{self.guardian_url}/agents/server-primary/mirror/setup",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Comprehensive mirroring setup for server-primary")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Mirroring setup failed: {error}")
        except Exception as e:
            logger.error(f"❌ Mirroring setup error: {e}")
    
    async def test_self_healing_scenarios(self):
        """Test various self-healing scenarios"""
        logger.info("\n🩺 Testing self-healing scenarios...")
        
        # Scenario 1: High CPU usage
        logger.info("Scenario 1: High CPU usage on server-primary")
        try:
            payload = {
                "issue_type": "high_cpu_usage",
                "severity": "critical",
                "details": {
                    "cpu_percent": 95,
                    "duration_seconds": 300,
                    "description": "CPU usage above 95% for 5 minutes"
                }
            }
            
            async with self.session.post(
                f"{self.guardian_url}/agents/server-primary/healing/initiate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Self-healing initiated: {result}")
                    healing_id = result.get('healing_id')
                    
                    # Wait a moment for healing to process
                    await asyncio.sleep(2)
                    
                    # Complete the healing process
                    if healing_id:
                        completion_payload = {
                            "success": True,
                            "details": "CPU usage normalized after mirror takeover"
                        }
                        async with self.session.post(
                            f"{self.guardian_url}/healing/{healing_id}/complete",
                            json=completion_payload
                        ) as comp_response:
                            if comp_response.status == 200:
                                logger.info("✅ Healing process completed successfully")
                            else:
                                logger.warning("⚠️ Healing completion failed")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Self-healing failed: {error}")
        except Exception as e:
            logger.error(f"❌ Self-healing error: {e}")
        
        # Scenario 2: Memory leak
        logger.info("\nScenario 2: Memory leak on edge-gateway")
        try:
            payload = {
                "issue_type": "memory_leak",
                "severity": "high",
                "details": {
                    "memory_percent": 87,
                    "trend": "increasing",
                    "description": "Memory usage steadily increasing"
                }
            }
            
            async with self.session.post(
                f"{self.guardian_url}/agents/edge-gateway/healing/initiate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Memory leak healing initiated: {result}")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Memory healing failed: {error}")
        except Exception as e:
            logger.error(f"❌ Memory healing error: {e}")
        
        # Scenario 3: Network connectivity issue
        logger.info("\nScenario 3: Network connectivity issue on monitor-alpha")
        try:
            payload = {
                "issue_type": "network_connectivity",
                "severity": "medium",
                "details": {
                    "packet_loss": 15,
                    "latency_ms": 500,
                    "description": "High packet loss and latency detected"
                }
            }
            
            async with self.session.post(
                f"{self.guardian_url}/agents/monitor-alpha/healing/initiate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Network healing initiated: {result}")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Network healing failed: {error}")
        except Exception as e:
            logger.error(f"❌ Network healing error: {e}")
    
    async def test_mirror_activation(self):
        """Test mirror activation"""
        logger.info("\n🔄 Testing mirror activation...")
        
        try:
            payload = {"mirror_agent": "server-backup"}
            async with self.session.post(
                f"{self.guardian_url}/agents/server-primary/mirror/activate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Mirror activated: {result}")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Mirror activation failed: {error}")
        except Exception as e:
            logger.error(f"❌ Mirror activation error: {e}")
    
    async def view_final_topology(self):
        """View the final network topology"""
        logger.info("\n🗺️ Viewing final network topology...")
        
        try:
            # Get network topology
            async with self.session.get(f"{self.guardian_url}/network/topology") as response:
                if response.status == 200:
                    topology = await response.json()
                    nodes = topology.get('topology', {}).get('nodes', [])
                    edges = topology.get('topology', {}).get('edges', [])
                    
                    logger.info(f"📊 Network Summary:")
                    logger.info(f"   Nodes (Agents): {len(nodes)}")
                    logger.info(f"   Edges (Relationships): {len(edges)}")
                    
                    if edges:
                        logger.info(f"   Relationship Types:")
                        rel_types = {}
                        for edge in edges:
                            rel_type = edge.get('relationship_type', 'UNKNOWN')
                            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                        
                        for rel_type, count in rel_types.items():
                            logger.info(f"     {rel_type}: {count}")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Topology retrieval failed: {error}")
        except Exception as e:
            logger.error(f"❌ Topology error: {e}")
        
        try:
            # Get mirror topology
            async with self.session.get(f"{self.guardian_url}/network/mirror-topology") as response:
                if response.status == 200:
                    mirror_topology = await response.json()
                    topology = mirror_topology.get('mirror_topology', {})
                    
                    logger.info(f"🪞 Mirror Summary:")
                    logger.info(f"   Primary agents with mirrors: {len(topology)}")
                    
                    for primary, data in topology.items():
                        mirrors = data.get('mirrors', [])
                        logger.info(f"   {primary}: {len(mirrors)} mirrors")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Mirror topology retrieval failed: {error}")
        except Exception as e:
            logger.error(f"❌ Mirror topology error: {e}")
        
        try:
            # Get active healing processes
            async with self.session.get(f"{self.guardian_url}/healing/active") as response:
                if response.status == 200:
                    healing = await response.json()
                    processes = healing.get('active_processes', [])
                    
                    logger.info(f"🩺 Active Healing:")
                    logger.info(f"   Active healing processes: {len(processes)}")
                    
                    for process in processes:
                        failed_agent = process.get('failed_agent', 'unknown')
                        healing_agent = process.get('healing_agent', 'unknown')
                        logger.info(f"   {healing_agent} healing {failed_agent}")
                else:
                    error = await response.text()
                    logger.warning(f"⚠️ Healing processes retrieval failed: {error}")
        except Exception as e:
            logger.error(f"❌ Healing processes error: {e}")

async def main():
    """Main function to populate Neo4j database"""
    logger.info("🚀 Neo4j Database Population Script")
    logger.info("="*60)
    
    async with Neo4jPopulator() as populator:
        # Check Guardian health
        if not await populator.check_guardian_health():
            logger.error("❌ Guardian not accessible. Make sure it's running!")
            return
        
        logger.info("\n" + "="*60)
        logger.info("PHASE 1: CREATING NETWORK TOPOLOGY")
        logger.info("="*60)
        
        # Create sample network
        await populator.create_sample_agents_and_relationships()
        
        logger.info("\n" + "="*60)
        logger.info("PHASE 2: TESTING SELF-HEALING")
        logger.info("="*60)
        
        # Test self-healing scenarios
        await populator.test_self_healing_scenarios()
        
        logger.info("\n" + "="*60)
        logger.info("PHASE 3: TESTING MIRROR ACTIVATION")
        logger.info("="*60)
        
        # Test mirror activation
        await populator.test_mirror_activation()
        
        logger.info("\n" + "="*60)
        logger.info("PHASE 4: FINAL TOPOLOGY REVIEW")
        logger.info("="*60)
        
        # View final topology
        await populator.view_final_topology()
        
        logger.info("\n" + "🎯 POPULATION COMPLETE!")
        logger.info("="*60)
        logger.info("✅ Your Neo4j Aura database should now show:")
        logger.info("   📊 Multiple nodes (agents)")
        logger.info("   🔗 Various relationship types")
        logger.info("   🪞 Mirror configurations")
        logger.info("   🩺 Healing processes")
        logger.info("\n🔍 Check your Neo4j Aura browser to see the graph!")
        logger.info("📈 You should see nodes and relationships instead of 0%")

if __name__ == "__main__":
    asyncio.run(main())
