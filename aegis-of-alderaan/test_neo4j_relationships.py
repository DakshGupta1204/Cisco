#!/usr/bin/env python3
"""
Aegis of Alderaan - Neo4j Relationships and Self-Healing Test
Comprehensive testing of graph database relationships and self-healing capabilities
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jRelationshipTester:
    def __init__(self, guardian_url="http://localhost:3001"):
        self.guardian_url = guardian_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_guardian_health(self):
        """Test Guardian server health"""
        logger.info("🔍 Testing Guardian server health...")
        try:
            async with self.session.get(f"{self.guardian_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"✅ Guardian healthy: {health_data}")
                    return True
                else:
                    logger.error(f"❌ Guardian unhealthy: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Guardian connection failed: {e}")
            return False
    
    async def create_mirror_relationship(self, primary_agent: str, mirror_agent: str):
        """Test creating mirror relationship"""
        logger.info(f"🔗 Creating mirror relationship: {primary_agent} <-> {mirror_agent}")
        
        try:
            payload = {"mirror_agent": mirror_agent}
            async with self.session.post(
                f"{self.guardian_url}/agents/{primary_agent}/relationships/mirror",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Mirror relationship created: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Mirror relationship failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Mirror relationship error: {e}")
            return None
    
    async def create_monitoring_relationship(self, monitor_agent: str, target_agent: str):
        """Test creating monitoring relationship"""
        logger.info(f"👁️ Creating monitoring relationship: {monitor_agent} -> {target_agent}")
        
        try:
            payload = {"target_agent": target_agent}
            async with self.session.post(
                f"{self.guardian_url}/agents/{monitor_agent}/relationships/monitor",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Monitoring relationship created: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Monitoring relationship failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Monitoring relationship error: {e}")
            return None
    
    async def create_network_connection(self, agent1: str, agent2: str, connection_type: str = "CONNECTED_TO"):
        """Test creating network connection"""
        logger.info(f"🌐 Creating network connection: {agent1} <-> {agent2} ({connection_type})")
        
        try:
            payload = {
                "target_agent": agent2,
                "connection_type": connection_type
            }
            async with self.session.post(
                f"{self.guardian_url}/agents/{agent1}/relationships/connect",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Network connection created: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Network connection failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Network connection error: {e}")
            return None
    
    async def get_agent_mirrors(self, agent_id: str):
        """Test getting agent mirrors"""
        logger.info(f"🪞 Getting mirrors for agent: {agent_id}")
        
        try:
            async with self.session.get(f"{self.guardian_url}/agents/{agent_id}/mirrors") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Agent mirrors: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Get mirrors failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Get mirrors error: {e}")
            return None
    
    async def get_mirror_topology(self):
        """Test getting mirror topology"""
        logger.info("🗺️ Getting mirror topology...")
        
        try:
            async with self.session.get(f"{self.guardian_url}/network/mirror-topology") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Mirror topology: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Mirror topology failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Mirror topology error: {e}")
            return None
    
    async def setup_agent_mirroring(self, agent_id: str, mirrors: list):
        """Test setting up comprehensive agent mirroring"""
        logger.info(f"⚙️ Setting up mirroring for agent: {agent_id}")
        
        try:
            payload = {"mirrors": mirrors}
            async with self.session.post(
                f"{self.guardian_url}/agents/{agent_id}/mirror/setup",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Mirroring setup: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Mirroring setup failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Mirroring setup error: {e}")
            return None
    
    async def initiate_self_healing(self, agent_id: str, issue_config: dict = None):
        """Test initiating self-healing"""
        logger.info(f"🩺 Initiating self-healing for agent: {agent_id}")
        
        try:
            payload = issue_config or {
                "issue_type": "system_failure",
                "severity": "high",
                "details": {"description": "Test healing scenario"}
            }
            
            async with self.session.post(
                f"{self.guardian_url}/agents/{agent_id}/healing/initiate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Self-healing initiated: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Self-healing failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Self-healing error: {e}")
            return None
    
    async def get_active_healing_processes(self):
        """Test getting active healing processes"""
        logger.info("🔄 Getting active healing processes...")
        
        try:
            async with self.session.get(f"{self.guardian_url}/healing/active") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Active healing processes: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Get healing processes failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Get healing processes error: {e}")
            return None
    
    async def activate_mirror(self, primary_agent: str, mirror_agent: str):
        """Test activating a mirror agent"""
        logger.info(f"🔄 Activating mirror: {mirror_agent} for {primary_agent}")
        
        try:
            payload = {"mirror_agent": mirror_agent}
            async with self.session.post(
                f"{self.guardian_url}/agents/{primary_agent}/mirror/activate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Mirror activated: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Mirror activation failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Mirror activation error: {e}")
            return None
    
    async def get_network_topology(self):
        """Test getting network topology"""
        logger.info("🗺️ Getting network topology...")
        
        try:
            async with self.session.get(f"{self.guardian_url}/network/topology") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Network topology: {result}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"❌ Network topology failed: {error}")
                    return None
        except Exception as e:
            logger.error(f"❌ Network topology error: {e}")
            return None

async def run_comprehensive_test():
    """Run comprehensive Neo4j relationships and self-healing test"""
    logger.info("🚀 Starting Neo4j Relationships and Self-Healing Test Suite")
    
    async with Neo4jRelationshipTester() as tester:
        # Test Guardian health first
        if not await tester.test_guardian_health():
            logger.error("❌ Guardian server not healthy. Exiting.")
            return
        
        logger.info("\n" + "="*60)
        logger.info("TESTING AGENT RELATIONSHIPS")
        logger.info("="*60)
        
        # Define test agents
        agents = {
            "agent_001": "primary-server",
            "agent_002": "backup-server", 
            "agent_003": "monitor-server",
            "agent_004": "edge-server"
        }
        
        # Create mirror relationships
        await tester.create_mirror_relationship("agent_001", "agent_002")
        await tester.create_mirror_relationship("agent_003", "agent_004")
        
        # Create monitoring relationships
        await tester.create_monitoring_relationship("agent_003", "agent_001")
        await tester.create_monitoring_relationship("agent_003", "agent_002")
        
        # Create network connections
        await tester.create_network_connection("agent_001", "agent_003", "COMMUNICATES_WITH")
        await tester.create_network_connection("agent_002", "agent_004", "BACKUP_CONNECTION")
        
        # Get agent mirrors
        await tester.get_agent_mirrors("agent_001")
        await tester.get_agent_mirrors("agent_003")
        
        # Setup comprehensive mirroring
        mirror_configs = [
            {"agent_id": "agent_002", "type": "active", "priority": 1},
            {"agent_id": "agent_004", "type": "backup", "priority": 2}
        ]
        await tester.setup_agent_mirroring("agent_001", mirror_configs)
        
        # Get mirror topology
        await tester.get_mirror_topology()
        
        logger.info("\n" + "="*60)
        logger.info("TESTING SELF-HEALING")
        logger.info("="*60)
        
        # Initiate self-healing
        healing_result = await tester.initiate_self_healing("agent_001", {
            "issue_type": "high_cpu_usage",
            "severity": "critical",
            "details": {"cpu_percent": 95, "duration": 300}
        })
        
        # Get active healing processes
        await tester.get_active_healing_processes()
        
        # Wait a moment for healing to process
        await asyncio.sleep(2)
        
        # Activate mirror
        await tester.activate_mirror("agent_001", "agent_002")
        
        logger.info("\n" + "="*60)
        logger.info("TESTING TOPOLOGY VIEWS")
        logger.info("="*60)
        
        # Get network topology
        await tester.get_network_topology()
        
        # Get mirror topology again
        await tester.get_mirror_topology()
        
        logger.info("\n" + "="*60)
        logger.info("TEST SUITE COMPLETED")
        logger.info("="*60)
        
        logger.info("✅ All Neo4j relationship and self-healing tests completed!")
        logger.info("🎯 Key Features Tested:")
        logger.info("   • Mirror relationships (bidirectional)")
        logger.info("   • Monitoring relationships")
        logger.info("   • Network connections")
        logger.info("   • Comprehensive mirroring setup")
        logger.info("   • Self-healing initiation")
        logger.info("   • Mirror activation")
        logger.info("   • Topology visualization")

async def run_quick_demo():
    """Run a quick demonstration"""
    logger.info("🎬 Quick Demo: Neo4j Relationships & Self-Healing")
    
    async with Neo4jRelationshipTester() as tester:
        # Quick health check
        await tester.test_guardian_health()
        
        # Create one of each relationship type
        await tester.create_mirror_relationship("demo_primary", "demo_mirror")
        await tester.create_monitoring_relationship("demo_monitor", "demo_primary")
        await tester.create_network_connection("demo_primary", "demo_monitor")
        
        # Quick topology check
        await tester.get_network_topology()
        
        # Initiate healing
        await tester.initiate_self_healing("demo_primary")
        
        logger.info("🎯 Quick demo completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(run_quick_demo())
    else:
        asyncio.run(run_comprehensive_test())
