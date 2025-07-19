"""
Aegis of Alderaan - Neo4j Handler
Neo4j interface for graph-based network topology and relationships
"""

import asyncio
import logging
from typing import Dict, List, Optional
from neo4j import AsyncGraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jHandler:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        # Support cloud Neo4j connections (Neo4j Aura)
        self.uri = uri or os.getenv('NEO4J_URI', 'neo4j+s://your-database-id.databases.neo4j.io')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'your-password')
        self.driver = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        """Connect to Neo4j Cloud (Aura) or hosted instance"""
        try:
            # Configure connection settings based on URI scheme
            driver_config = {
                "auth": (self.user, self.password),
                "connection_timeout": 15,  # 15 seconds timeout
                "max_connection_lifetime": 60 * 60,  # 1 hour
                "max_connection_pool_size": 50
            }
            
            # Only add encryption settings for bolt:// or neo4j:// schemes
            # neo4j+s:// and bolt+s:// schemes handle encryption automatically
            if self.uri.startswith(('bolt://', 'neo4j://')):
                driver_config["encrypted"] = True
            
            self.driver = AsyncGraphDatabase.driver(self.uri, **driver_config)
            
            # Test connection
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            
            self.logger.info("Connected to Neo4j Cloud successfully")
            
            # Create constraints and indexes
            await self.create_constraints()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j Cloud: {e}")
            self.logger.info("Please check your Neo4j connection string and credentials")
            self.logger.info("For Neo4j Aura, use format: neo4j+s://your-database-id.databases.neo4j.io")
            raise
    
    async def disconnect(self):
        """Disconnect from Neo4j"""
        if self.driver:
            await self.driver.close()
            self.logger.info("Disconnected from Neo4j")
    
    async def health_check(self) -> bool:
        """Check Neo4j health"""
        try:
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    async def create_constraints(self):
        """Create constraints and indexes"""
        try:
            async with self.driver.session() as session:
                # Create constraints
                constraints = [
                    "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE",
                    "CREATE INDEX agent_hostname IF NOT EXISTS FOR (a:Agent) ON (a.hostname)",
                    "CREATE INDEX agent_status IF NOT EXISTS FOR (a:Agent) ON (a.status)"
                ]
                
                for constraint in constraints:
                    try:
                        await session.run(constraint)
                    except Exception:
                        pass  # Constraint might already exist
                        
            self.logger.info("Neo4j constraints created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create constraints: {e}")
    
    async def create_or_update_agent_node(self, agent_id: str, agent_data: Dict):
        """Create or update agent node in the graph"""
        try:
            async with self.driver.session() as session:
                query = """
                MERGE (a:Agent {agent_id: $agent_id})
                SET a.hostname = $hostname,
                    a.role = $role,
                    a.status = $status,
                    a.last_updated = timestamp()
                RETURN a
                """
                
                await session.run(query,
                    agent_id=agent_id,
                    hostname=agent_data.get('hostname', 'unknown'),
                    role=agent_data.get('role', 'endpoint'),
                    status='active'
                )
                
            self.logger.debug(f"Agent node created/updated: {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create/update agent node {agent_id}: {e}")
    
    async def update_agent_status(self, agent_id: str, status: str):
        """Update agent status in the graph"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (a:Agent {agent_id: $agent_id})
                SET a.status = $status,
                    a.last_updated = timestamp()
                RETURN a
                """
                
                await session.run(query, agent_id=agent_id, status=status)
                
        except Exception as e:
            self.logger.error(f"Failed to update agent status {agent_id}: {e}")
    
    async def create_communication_relationship(self, from_agent: str, to_agent: str, relationship_type: str = "COMMUNICATES_WITH"):
        """Create communication relationship between agents"""
        try:
            async with self.driver.session() as session:
                query = f"""
                MATCH (a1:Agent {{agent_id: $from_agent}})
                MATCH (a2:Agent {{agent_id: $to_agent}})
                MERGE (a1)-[r:{relationship_type}]->(a2)
                SET r.created_at = timestamp(),
                    r.last_updated = timestamp()
                RETURN r
                """
                
                await session.run(query, from_agent=from_agent, to_agent=to_agent)
                
        except Exception as e:
            self.logger.error(f"Failed to create relationship {from_agent} -> {to_agent}: {e}")
    
    async def create_takeover_relationship(self, mirror_agent: str, failed_agent: str):
        """Create takeover relationship"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (m:Agent {agent_id: $mirror_agent})
                MATCH (f:Agent {agent_id: $failed_agent})
                MERGE (m)-[r:TOOK_OVER]->(f)
                SET r.timestamp = timestamp()
                RETURN r
                """
                
                await session.run(query, mirror_agent=mirror_agent, failed_agent=failed_agent)
                
        except Exception as e:
            self.logger.error(f"Failed to create takeover relationship: {e}")
    
    async def get_network_topology(self) -> Dict:
        """Get the complete network topology"""
        try:
            async with self.driver.session() as session:
                # Get all agents
                agents_query = """
                MATCH (a:Agent)
                RETURN a.agent_id as agent_id, 
                       a.hostname as hostname, 
                       a.role as role, 
                       a.status as status
                """
                
                agents_result = await session.run(agents_query)
                agents = [dict(record) async for record in agents_result]
                
                # Get all relationships
                relationships_query = """
                MATCH (a1:Agent)-[r]->(a2:Agent)
                RETURN a1.agent_id as source, 
                       a2.agent_id as target, 
                       type(r) as relationship_type,
                       r.timestamp as timestamp
                """
                
                rel_result = await session.run(relationships_query)
                relationships = [dict(record) async for record in rel_result]
                
                return {
                    'nodes': agents,
                    'edges': relationships,
                    'generated_at': 'timestamp()'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get network topology: {e}")
            return {'nodes': [], 'edges': []}
    
    async def get_agent_mirrors(self, agent_id: str) -> List[str]:
        """Get mirror agents for a specific agent"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (a:Agent {agent_id: $agent_id})-[:IS_MIRROR_OF|HAS_MIRROR]-(m:Agent)
                WHERE m.status = 'active'
                RETURN m.agent_id as mirror_id
                """
                
                result = await session.run(query, agent_id=agent_id)
                mirrors = [record['mirror_id'] async for record in result]
                
                return mirrors
                
        except Exception as e:
            self.logger.error(f"Failed to get mirrors for {agent_id}: {e}")
            return []
    
    async def find_shortest_path(self, from_agent: str, to_agent: str) -> List[str]:
        """Find shortest communication path between agents"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH path = shortestPath(
                    (a1:Agent {agent_id: $from_agent})-[*]-(a2:Agent {agent_id: $to_agent})
                )
                RETURN [node in nodes(path) | node.agent_id] as path
                """
                
                result = await session.run(query, from_agent=from_agent, to_agent=to_agent)
                record = await result.single()
                
                return record['path'] if record else []
                
        except Exception as e:
            self.logger.error(f"Failed to find path {from_agent} -> {to_agent}: {e}")
            return []
    
    async def get_agent_neighbors(self, agent_id: str) -> List[Dict]:
        """Get neighboring agents"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (a:Agent {agent_id: $agent_id})-[r]-(neighbor:Agent)
                RETURN neighbor.agent_id as neighbor_id,
                       neighbor.hostname as hostname,
                       neighbor.status as status,
                       type(r) as relationship_type
                """
                
                result = await session.run(query, agent_id=agent_id)
                neighbors = [dict(record) async for record in result]
                
                return neighbors
                
        except Exception as e:
            self.logger.error(f"Failed to get neighbors for {agent_id}: {e}")
            return []

    # === ENHANCED RELATIONSHIP MANAGEMENT ===
    
    async def create_mirror_relationship(self, primary_agent: str, mirror_agent: str):
        """Create bidirectional mirror relationship between agents"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (p:Agent {agent_id: $primary_agent})
                MATCH (m:Agent {agent_id: $mirror_agent})
                MERGE (p)-[r1:HAS_MIRROR]->(m)
                MERGE (m)-[r2:IS_MIRROR_OF]->(p)
                SET r1.created_at = timestamp(),
                    r1.last_updated = timestamp(),
                    r1.mirror_type = 'active',
                    r2.created_at = timestamp(),
                    r2.last_updated = timestamp(),
                    r2.mirror_type = 'active'
                RETURN r1, r2
                """
                
                await session.run(query, primary_agent=primary_agent, mirror_agent=mirror_agent)
                self.logger.info(f"Mirror relationship created: {primary_agent} <-> {mirror_agent}")
                
        except Exception as e:
            self.logger.error(f"Failed to create mirror relationship: {e}")
    
    async def create_monitoring_relationship(self, monitor_agent: str, target_agent: str):
        """Create monitoring relationship between agents"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (m:Agent {agent_id: $monitor_agent})
                MATCH (t:Agent {agent_id: $target_agent})
                MERGE (m)-[r:MONITORS]->(t)
                SET r.created_at = timestamp(),
                    r.last_updated = timestamp(),
                    r.monitor_type = 'health_check'
                RETURN r
                """
                
                await session.run(query, monitor_agent=monitor_agent, target_agent=target_agent)
                self.logger.debug(f"Monitoring relationship created: {monitor_agent} -> {target_agent}")
                
        except Exception as e:
            self.logger.error(f"Failed to create monitoring relationship: {e}")
    
    async def create_network_connection(self, agent1: str, agent2: str, connection_type: str = "CONNECTED_TO"):
        """Create network connection relationship between agents"""
        try:
            async with self.driver.session() as session:
                query = f"""
                MATCH (a1:Agent {{agent_id: $agent1}})
                MATCH (a2:Agent {{agent_id: $agent2}})
                MERGE (a1)-[r:{connection_type}]->(a2)
                MERGE (a2)-[r2:{connection_type}]->(a1)
                SET r.created_at = timestamp(),
                    r.last_updated = timestamp(),
                    r.connection_type = $connection_type,
                    r2.created_at = timestamp(),
                    r2.last_updated = timestamp(),
                    r2.connection_type = $connection_type
                RETURN r, r2
                """
                
                await session.run(query, agent1=agent1, agent2=agent2, connection_type=connection_type)
                self.logger.debug(f"Network connection created: {agent1} <-> {agent2} ({connection_type})")
                
        except Exception as e:
            self.logger.error(f"Failed to create network connection: {e}")
    
    # === SELF-HEALING COORDINATION ===
    
    async def register_health_issue(self, agent_id: str, issue_type: str, severity: str, details: Dict = None):
        """Register a health issue for an agent"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (a:Agent {agent_id: $agent_id})
                CREATE (h:HealthIssue {
                    issue_id: randomUUID(),
                    agent_id: $agent_id,
                    issue_type: $issue_type,
                    severity: $severity,
                    details: $details,
                    status: 'active',
                    created_at: timestamp(),
                    last_updated: timestamp()
                })
                CREATE (a)-[:HAS_ISSUE]->(h)
                RETURN h.issue_id as issue_id
                """
                
                result = await session.run(query, 
                    agent_id=agent_id,
                    issue_type=issue_type,
                    severity=severity,
                    details=str(details) if details else ""
                )
                
                record = await result.single()
                issue_id = record['issue_id'] if record else None
                
                self.logger.info(f"Health issue registered: {agent_id} - {issue_type} ({severity})")
                return issue_id
                
        except Exception as e:
            self.logger.error(f"Failed to register health issue: {e}")
            return None
    
    async def initiate_self_healing(self, agent_id: str) -> Dict:
        """Initiate self-healing process for an agent"""
        try:
            async with self.driver.session() as session:
                # Find available mirrors
                mirrors = await self.get_agent_mirrors(agent_id)
                
                if not mirrors:
                    self.logger.warning(f"No mirrors available for agent {agent_id}")
                    return {"status": "failed", "reason": "no_mirrors"}
                
                # Select best mirror (first active one for now)
                selected_mirror = mirrors[0]
                
                # Create healing relationship
                healing_query = """
                MATCH (f:Agent {agent_id: $failed_agent})
                MATCH (m:Agent {agent_id: $mirror_agent})
                CREATE (h:HealingProcess {
                    healing_id: randomUUID(),
                    failed_agent: $failed_agent,
                    healing_agent: $mirror_agent,
                    status: 'in_progress',
                    started_at: timestamp(),
                    last_updated: timestamp()
                })
                CREATE (m)-[:HEALING]->(f)
                CREATE (h)-[:INVOLVES_AGENT]->(f)
                CREATE (h)-[:INVOLVES_AGENT]->(m)
                RETURN h.healing_id as healing_id
                """
                
                result = await session.run(healing_query, 
                    failed_agent=agent_id,
                    mirror_agent=selected_mirror
                )
                
                record = await result.single()
                healing_id = record['healing_id'] if record else None
                
                self.logger.info(f"Self-healing initiated: {selected_mirror} healing {agent_id}")
                
                return {
                    "status": "initiated",
                    "healing_id": healing_id,
                    "healing_agent": selected_mirror,
                    "failed_agent": agent_id
                }
                
        except Exception as e:
            self.logger.error(f"Failed to initiate self-healing for {agent_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def complete_healing_process(self, healing_id: str, success: bool, details: str = ""):
        """Mark a healing process as complete"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (h:HealingProcess {healing_id: $healing_id})
                SET h.status = $status,
                    h.completed_at = timestamp(),
                    h.last_updated = timestamp(),
                    h.completion_details = $details
                RETURN h
                """
                
                status = "completed" if success else "failed"
                await session.run(query, 
                    healing_id=healing_id,
                    status=status,
                    details=details
                )
                
                self.logger.info(f"Healing process {healing_id} marked as {status}")
                
        except Exception as e:
            self.logger.error(f"Failed to complete healing process: {e}")
    
    async def get_active_healing_processes(self) -> List[Dict]:
        """Get all active healing processes"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (h:HealingProcess)
                WHERE h.status = 'in_progress'
                RETURN h.healing_id as healing_id,
                       h.failed_agent as failed_agent,
                       h.healing_agent as healing_agent,
                       h.started_at as started_at,
                       h.last_updated as last_updated
                ORDER BY h.started_at DESC
                """
                
                result = await session.run(query)
                processes = [dict(record) async for record in result]
                
                return processes
                
        except Exception as e:
            self.logger.error(f"Failed to get active healing processes: {e}")
            return []
    
    # === AGENT MIRRORING AND REDUNDANCY ===
    
    async def setup_agent_mirroring(self, primary_agent: str, mirror_configs: List[Dict]):
        """Setup comprehensive mirroring for an agent"""
        try:
            for mirror_config in mirror_configs:
                mirror_agent = mirror_config['agent_id']
                mirror_type = mirror_config.get('type', 'active')  # active, passive, backup
                priority = mirror_config.get('priority', 1)
                
                async with self.driver.session() as session:
                    query = """
                    MATCH (p:Agent {agent_id: $primary_agent})
                    MATCH (m:Agent {agent_id: $mirror_agent})
                    MERGE (p)-[r:HAS_MIRROR]->(m)
                    MERGE (m)-[r2:IS_MIRROR_OF]->(p)
                    SET r.mirror_type = $mirror_type,
                        r.priority = $priority,
                        r.created_at = timestamp(),
                        r.last_updated = timestamp(),
                        r2.mirror_type = $mirror_type,
                        r2.priority = $priority,
                        r2.created_at = timestamp(),
                        r2.last_updated = timestamp()
                    """
                    
                    await session.run(query,
                        primary_agent=primary_agent,
                        mirror_agent=mirror_agent,
                        mirror_type=mirror_type,
                        priority=priority
                    )
                
                self.logger.info(f"Mirror setup: {primary_agent} -> {mirror_agent} ({mirror_type}, priority: {priority})")
                
        except Exception as e:
            self.logger.error(f"Failed to setup agent mirroring: {e}")
    
    async def activate_mirror(self, primary_agent: str, mirror_agent: str):
        """Activate a mirror agent to take over from primary"""
        try:
            async with self.driver.session() as session:
                # Create takeover relationship
                await self.create_takeover_relationship(mirror_agent, primary_agent)
                
                # Update agent statuses
                update_query = """
                MATCH (p:Agent {agent_id: $primary_agent})
                MATCH (m:Agent {agent_id: $mirror_agent})
                SET p.status = 'inactive',
                    p.last_updated = timestamp(),
                    m.status = 'active_mirror',
                    m.last_updated = timestamp()
                """
                
                await session.run(update_query, 
                    primary_agent=primary_agent,
                    mirror_agent=mirror_agent
                )
                
                self.logger.info(f"Mirror activated: {mirror_agent} took over from {primary_agent}")
                
        except Exception as e:
            self.logger.error(f"Failed to activate mirror: {e}")
    
    async def get_mirror_topology(self) -> Dict:
        """Get comprehensive mirror topology information"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (p:Agent)-[r:HAS_MIRROR]->(m:Agent)
                RETURN p.agent_id as primary_agent,
                       p.hostname as primary_hostname,
                       p.status as primary_status,
                       m.agent_id as mirror_agent,
                       m.hostname as mirror_hostname,
                       m.status as mirror_status,
                       r.mirror_type as mirror_type,
                       r.priority as priority,
                       r.created_at as created_at
                ORDER BY p.agent_id, r.priority
                """
                
                result = await session.run(query)
                mirror_relationships = [dict(record) async for record in result]
                
                # Group by primary agent
                topology = {}
                for rel in mirror_relationships:
                    primary = rel['primary_agent']
                    if primary not in topology:
                        topology[primary] = {
                            'primary_info': {
                                'agent_id': primary,
                                'hostname': rel['primary_hostname'],
                                'status': rel['primary_status']
                            },
                            'mirrors': []
                        }
                    
                    topology[primary]['mirrors'].append({
                        'agent_id': rel['mirror_agent'],
                        'hostname': rel['mirror_hostname'],
                        'status': rel['mirror_status'],
                        'mirror_type': rel['mirror_type'],
                        'priority': rel['priority'],
                        'created_at': rel['created_at']
                    })
                
                return topology
                
        except Exception as e:
            self.logger.error(f"Failed to get mirror topology: {e}")
            return {}
    
    async def check_mirror_health(self, agent_id: str) -> Dict:
        """Check health status of an agent and its mirrors"""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (a:Agent {agent_id: $agent_id})
                OPTIONAL MATCH (a)-[:HAS_MIRROR]->(m:Agent)
                OPTIONAL MATCH (a)-[:HAS_ISSUE]->(h:HealthIssue)
                WHERE h.status = 'active'
                RETURN a.agent_id as agent_id,
                       a.hostname as hostname,
                       a.status as status,
                       collect(DISTINCT m.agent_id) as mirrors,
                       collect(DISTINCT {type: h.issue_type, severity: h.severity}) as health_issues
                """
                
                result = await session.run(query, agent_id=agent_id)
                record = await result.single()
                
                if record:
                    return {
                        'agent_id': record['agent_id'],
                        'hostname': record['hostname'],
                        'status': record['status'],
                        'mirrors': [m for m in record['mirrors'] if m],
                        'health_issues': [h for h in record['health_issues'] if h['type']],
                        'mirror_count': len([m for m in record['mirrors'] if m]),
                        'issue_count': len([h for h in record['health_issues'] if h['type']])
                    }
                else:
                    return {'error': f'Agent {agent_id} not found'}
                
        except Exception as e:
            self.logger.error(f"Failed to check mirror health for {agent_id}: {e}")
            return {'error': str(e)}
