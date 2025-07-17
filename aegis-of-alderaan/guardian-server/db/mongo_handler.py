"""
Aegis of Alderaan - MongoDB Handler
MongoDB interface for storing metrics, anomalies, and agent information
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoHandler:
    def __init__(self, connection_string: str = None):
        # Use cloud MongoDB by default (MongoDB Atlas)
        # Check for both MONGODB_URI and MONGODB_URL for compatibility
        self.connection_string = (
            connection_string or 
            os.getenv('MONGODB_URI') or 
            os.getenv('MONGODB_URL', 
                'mongodb+srv://<username>:<password>@<cluster>.mongodb.net/aegis_guardian?retryWrites=true&w=majority'
            )
        )
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        
        # Collection names
        self.collections = {
            'agents': 'agents',
            'metrics': 'metrics',
            'anomalies': 'anomalies',
            'remediations': 'remediations',
            'escalations': 'escalations',
            'security_incidents': 'security_incidents'
        }
    
    async def connect(self):
        """Connect to MongoDB Cloud"""
        try:
            # Configure for cloud connection with SSL and timeouts
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=10000,  # 10 seconds timeout
                connectTimeoutMS=10000,
                maxPoolSize=50,
                retryWrites=True
            )
            self.db = self.client.aegis_guardian
            
            # Test connection
            await self.client.admin.command('ping')
            self.logger.info("Connected to MongoDB Cloud successfully")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB Cloud: {e}")
            self.logger.info("Please check your MongoDB connection string and credentials")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> bool:
        """Check MongoDB health"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Agents collection indexes
            await self.db[self.collections['agents']].create_index("agent_id", unique=True)
            await self.db[self.collections['agents']].create_index("hostname")
            await self.db[self.collections['agents']].create_index("last_heartbeat")
            
            # Metrics collection indexes
            await self.db[self.collections['metrics']].create_index([
                ("agent_id", 1),
                ("timestamp", -1)
            ])
            await self.db[self.collections['metrics']].create_index("timestamp")
            
            # Anomalies collection indexes
            await self.db[self.collections['anomalies']].create_index([
                ("agent_id", 1),
                ("timestamp", -1)
            ])
            await self.db[self.collections['anomalies']].create_index("severity")
            
            # Remediations collection indexes
            await self.db[self.collections['remediations']].create_index("agent_id")
            await self.db[self.collections['remediations']].create_index("status")
            await self.db[self.collections['remediations']].create_index("started_at")
            
            self.logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
    
    def _check_connection(self) -> bool:
        """Check if database connection is available"""
        if self.db is None:
            self.logger.warning("Database not connected")
            return False
        return True
    
    # Agent operations
    async def upsert_agent(self, agent_info: Dict):
        """Insert or update agent information"""
        try:
            if not self._check_connection():
                return
                
            agent_info['updated_at'] = datetime.utcnow()
            
            await self.db[self.collections['agents']].update_one(
                {'agent_id': agent_info['agent_id']},
                {'$set': agent_info},
                upsert=True
            )
            
            self.logger.debug(f"Agent {agent_info['agent_id']} upserted")
            
        except Exception as e:
            self.logger.error(f"Failed to upsert agent: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        try:
            if not self._check_connection():
                return None
                
            agent = await self.db[self.collections['agents']].find_one(
                {'agent_id': agent_id},
                {'_id': 0}
            )
            return agent
        except Exception as e:
            self.logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    async def get_all_agents(self) -> List[Dict]:
        """Get all registered agents"""
        try:
            if not self._check_connection():
                return []
                
            cursor = self.db[self.collections['agents']].find({}, {'_id': 0})
            agents = await cursor.to_list(length=None)
            return agents
        except Exception as e:
            self.logger.error(f"Failed to get all agents: {e}")
            return []
    
    async def update_agent_heartbeat(self, agent_id: str):
        """Update agent's last heartbeat timestamp"""
        try:
            if not self._check_connection():
                return
                
            await self.db[self.collections['agents']].update_one(
                {'agent_id': agent_id},
                {'$set': {
                    'last_heartbeat': datetime.utcnow(),
                    'status': 'active'
                }}
            )
        except Exception as e:
            self.logger.error(f"Failed to update heartbeat for {agent_id}: {e}")
    
    async def get_offline_agents(self, minutes: int = 5) -> List[str]:
        """Get agents that haven't sent heartbeat recently"""
        try:
            # Check if database connection exists
            if self.db is None:
                self.logger.warning("Database not connected, cannot get offline agents")
                return []
                
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            cursor = self.db[self.collections['agents']].find(
                {
                    '$or': [
                        {'last_heartbeat': {'$lt': cutoff_time}},
                        {'last_heartbeat': {'$exists': False}}
                    ]
                },
                {'agent_id': 1, '_id': 0}
            )
            
            offline_agents = [doc['agent_id'] async for doc in cursor]
            return offline_agents
            
        except Exception as e:
            self.logger.error(f"Failed to get offline agents: {e}")
            return []
    
    # Metrics operations
    async def store_metrics(self, metrics_data: Dict):
        """Store metrics data"""
        try:
            metrics_data['stored_at'] = datetime.utcnow()
            
            await self.db[self.collections['metrics']].insert_one(metrics_data)
            self.logger.debug(f"Metrics stored for agent {metrics_data.get('agent_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")
            raise
    
    async def get_agent_metrics(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Get recent metrics for an agent"""
        try:
            cursor = self.db[self.collections['metrics']].find(
                {'agent_id': agent_id},
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit)
            
            metrics = await cursor.to_list(length=limit)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics for {agent_id}: {e}")
            return []
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for dashboard"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            pipeline = [
                {'$match': {'timestamp': {'$gte': cutoff_time.isoformat()}}},
                {
                    '$group': {
                        '_id': '$agent_id',
                        'latest_metrics': {'$last': '$$ROOT'},
                        'avg_cpu': {'$avg': '$cpu.percent'},
                        'avg_memory': {'$avg': '$memory.percent'},
                        'avg_disk': {'$avg': '$disk.percent'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            cursor = self.db[self.collections['metrics']].aggregate(pipeline)
            summary = await cursor.to_list(length=None)
            
            return {'summary': summary}
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {'summary': []}
    
    # Anomaly operations
    async def store_anomaly(self, anomaly_data: Dict):
        """Store anomaly data"""
        try:
            anomaly_data['stored_at'] = datetime.utcnow()
            
            await self.db[self.collections['anomalies']].insert_one(anomaly_data)
            self.logger.info(f"Anomaly stored: {anomaly_data.get('type')} for {anomaly_data.get('agent_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store anomaly: {e}")
            raise
    
    async def get_anomalies(self, limit: int = 50, agent_id: str = None) -> List[Dict]:
        """Get recent anomalies"""
        try:
            query = {}
            if agent_id:
                query['agent_id'] = agent_id
            
            cursor = self.db[self.collections['anomalies']].find(
                query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit)
            
            anomalies = await cursor.to_list(length=limit)
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Failed to get anomalies: {e}")
            return []
    
    # Remediation operations
    async def store_remediation(self, remediation_data: Dict):
        """Store remediation record"""
        try:
            await self.db[self.collections['remediations']].insert_one(remediation_data)
            self.logger.info(f"Remediation stored: {remediation_data.get('id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store remediation: {e}")
            raise
    
    async def update_remediation(self, remediation_id: str, remediation_data: Dict):
        """Update remediation record"""
        try:
            remediation_data['updated_at'] = datetime.utcnow()
            
            await self.db[self.collections['remediations']].update_one(
                {'id': remediation_id},
                {'$set': remediation_data}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update remediation {remediation_id}: {e}")
    
    async def get_remediations(self, limit: int = 50) -> List[Dict]:
        """Get recent remediations"""
        try:
            cursor = self.db[self.collections['remediations']].find(
                {},
                {'_id': 0}
            ).sort('started_at', -1).limit(limit)
            
            remediations = await cursor.to_list(length=limit)
            return remediations
            
        except Exception as e:
            self.logger.error(f"Failed to get remediations: {e}")
            return []
    
    # Security operations
    async def store_security_incident(self, incident_data: Dict):
        """Store security incident"""
        try:
            incident_data['stored_at'] = datetime.utcnow()
            
            await self.db[self.collections['security_incidents']].insert_one(incident_data)
            self.logger.critical(f"Security incident stored for agent {incident_data.get('agent_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store security incident: {e}")
            raise
    
    async def store_escalation(self, escalation_data: Dict):
        """Store escalation record"""
        try:
            await self.db[self.collections['escalations']].insert_one(escalation_data)
            self.logger.warning(f"Escalation stored: {escalation_data.get('remediation_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store escalation: {e}")
            raise
    
    # Attack Simulation Methods
    async def log_attack_simulation(self, simulation_data: Dict):
        """Log attack simulation for tracking and analysis"""
        try:
            simulation_data['logged_at'] = datetime.utcnow().isoformat()
            await self.db['attack_simulations'].insert_one(simulation_data)
            self.logger.info(f"Attack simulation logged: {simulation_data.get('simulation_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to log attack simulation: {e}")
            raise
    
    async def get_attack_simulation_history(self, limit: int = 20):
        """Get history of attack simulations"""
        try:
            cursor = self.db['attack_simulations'].find().sort('logged_at', -1).limit(limit)
            simulations = []
            
            async for simulation in cursor:
                simulation['_id'] = str(simulation['_id'])  # Convert ObjectId to string
                simulations.append(simulation)
            
            return simulations
            
        except Exception as e:
            self.logger.error(f"Failed to get attack simulation history: {e}")
            return []
    
    async def update_attack_simulation_status(self, simulation_id: str, status: str, details: Dict = None):
        """Update the status of an attack simulation"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if details:
                update_data['details'] = details
            
            await self.db['attack_simulations'].update_one(
                {'simulation_id': simulation_id},
                {'$set': update_data}
            )
            
            self.logger.info(f"Attack simulation {simulation_id} status updated to {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to update attack simulation status: {e}")
            raise
    
    # Cleanup operations
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Clean old metrics
            result = await self.db[self.collections['metrics']].delete_many({
                'timestamp': {'$lt': cutoff_time.isoformat()}
            })
            
            self.logger.info(f"Cleaned up {result.deleted_count} old metrics records")
            
            # Clean old attack simulations
            attack_result = await self.db['attack_simulations'].delete_many({
                'logged_at': {'$lt': cutoff_time.isoformat()}
            })
            
            self.logger.info(f"Cleaned up {attack_result.deleted_count} old attack simulation records")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
