"""
Aegis of Alderaan - Remediation Engine
Triggers automated healing actions and manages system recovery
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class RemediationEngine:
    def __init__(self, mongo_handler, neo4j_handler, websocket_manager):
        self.mongo_handler = mongo_handler
        self.neo4j_handler = neo4j_handler
        self.websocket_manager = websocket_manager
        self.logger = logging.getLogger(__name__)
        
        self.running = False
        self.remediation_strategies = {
            'cpu_high': self.handle_high_cpu,
            'memory_high': self.handle_high_memory,
            'disk_high': self.handle_high_disk,
            'network_anomaly': self.handle_network_anomaly,
            'agent_offline': self.handle_agent_offline,
            'security_threat': self.handle_security_threat
        }
        
        # Remediation thresholds
        self.thresholds = {
            'cpu_critical': 95,
            'memory_critical': 95,
            'disk_critical': 95,
            'response_timeout': 30,
            'max_retries': 3
        }
        
        # Track ongoing remediations
        self.active_remediations = {}
        
    async def start(self):
        """Start the remediation engine"""
        self.logger.info("Starting Remediation Engine")
        self.running = True
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_agent_health())
        asyncio.create_task(self.process_remediation_queue())
        
    async def stop(self):
        """Stop the remediation engine"""
        self.logger.info("Stopping Remediation Engine")
        self.running = False
        
    def is_running(self) -> bool:
        """Check if remediation engine is running"""
        return self.running
    
    async def analyze_metrics(self, metrics_data: Dict):
        """Analyze metrics and trigger remediation if needed"""
        agent_id = metrics_data.get('agent_id')
        
        # Check CPU usage
        cpu_percent = metrics_data.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.thresholds['cpu_critical']:
            await self.trigger_remediation(agent_id, 'cpu_high', {
                'current_value': cpu_percent,
                'threshold': self.thresholds['cpu_critical'],
                'metrics': metrics_data
            })
        
        # Check memory usage
        memory_percent = metrics_data.get('memory', {}).get('percent', 0)
        if memory_percent > self.thresholds['memory_critical']:
            await self.trigger_remediation(agent_id, 'memory_high', {
                'current_value': memory_percent,
                'threshold': self.thresholds['memory_critical'],
                'metrics': metrics_data
            })
        
        # Check disk usage
        disk_percent = metrics_data.get('disk', {}).get('percent', 0)
        if disk_percent > self.thresholds['disk_critical']:
            await self.trigger_remediation(agent_id, 'disk_high', {
                'current_value': disk_percent,
                'threshold': self.thresholds['disk_critical'],
                'metrics': metrics_data
            })
    
    async def handle_anomaly(self, anomaly_data: Dict):
        """Handle detected anomaly"""
        agent_id = anomaly_data.get('agent_id')
        anomaly_type = anomaly_data.get('type')
        severity = anomaly_data.get('severity', 'info')
        
        self.logger.warning(f"Anomaly detected: {anomaly_type} on {agent_id} (severity: {severity})")
        
        # Map anomaly types to remediation strategies
        if anomaly_type.startswith('cpu'):
            await self.trigger_remediation(agent_id, 'cpu_high', anomaly_data)
        elif anomaly_type.startswith('memory'):
            await self.trigger_remediation(agent_id, 'memory_high', anomaly_data)
        elif anomaly_type.startswith('network'):
            await self.trigger_remediation(agent_id, 'network_anomaly', anomaly_data)
        elif 'security' in anomaly_type or 'attack' in anomaly_type:
            await self.trigger_remediation(agent_id, 'security_threat', anomaly_data)
        
        # Notify dashboards
        await self.websocket_manager.notify_anomaly_to_dashboards(anomaly_data)
    
    async def trigger_remediation(self, agent_id: str, strategy: str, context: Dict):
        """Trigger a remediation strategy"""
        remediation_id = f"{agent_id}_{strategy}_{datetime.utcnow().timestamp()}"
        
        remediation_info = {
            'id': remediation_id,
            'agent_id': agent_id,
            'strategy': strategy,
            'context': context,
            'status': 'initiated',
            'started_at': datetime.utcnow().isoformat(),
            'retries': 0
        }
        
        # Store remediation record
        await self.mongo_handler.store_remediation(remediation_info)
        
        # Track active remediation
        self.active_remediations[remediation_id] = remediation_info
        
        # Execute remediation strategy
        if strategy in self.remediation_strategies:
            asyncio.create_task(self.execute_remediation(remediation_id))
        else:
            self.logger.error(f"Unknown remediation strategy: {strategy}")
    
    async def execute_remediation(self, remediation_id: str):
        """Execute a specific remediation"""
        remediation = self.active_remediations.get(remediation_id)
        if not remediation:
            return
        
        strategy = remediation['strategy']
        agent_id = remediation['agent_id']
        context = remediation['context']
        
        try:
            self.logger.info(f"Executing remediation {strategy} for agent {agent_id}")
            
            # Execute the strategy
            success = await self.remediation_strategies[strategy](agent_id, context)
            
            # Update remediation status
            if success:
                remediation['status'] = 'completed'
                remediation['completed_at'] = datetime.utcnow().isoformat()
                self.logger.info(f"Remediation {remediation_id} completed successfully")
            else:
                await self.handle_remediation_failure(remediation_id)
                
        except Exception as e:
            self.logger.error(f"Remediation {remediation_id} failed: {e}")
            remediation['status'] = 'failed'
            remediation['error'] = str(e)
            
        # Update database
        await self.mongo_handler.update_remediation(remediation_id, remediation)
        
        # Notify dashboards
        await self.websocket_manager.notify_remediation_to_dashboards(remediation)
        
        # Clean up
        self.active_remediations.pop(remediation_id, None)
    
    async def handle_remediation_failure(self, remediation_id: str):
        """Handle failed remediation"""
        remediation = self.active_remediations.get(remediation_id)
        if not remediation:
            return
        
        remediation['retries'] += 1
        
        if remediation['retries'] < self.thresholds['max_retries']:
            self.logger.info(f"Retrying remediation {remediation_id} (attempt {remediation['retries']})")
            # Retry after delay
            await asyncio.sleep(10)
            await self.execute_remediation(remediation_id)
        else:
            self.logger.error(f"Remediation {remediation_id} failed after {remediation['retries']} attempts")
            remediation['status'] = 'failed'
            
            # Escalate to human intervention
            await self.escalate_to_human(remediation)
    
    async def escalate_to_human(self, remediation: Dict):
        """Escalate failed remediation to human intervention"""
        escalation = {
            'type': 'escalation',
            'remediation_id': remediation['id'],
            'agent_id': remediation['agent_id'],
            'strategy': remediation['strategy'],
            'reason': 'automatic_remediation_failed',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store escalation
        await self.mongo_handler.store_escalation(escalation)
        
        # Notify dashboards
        await self.websocket_manager.broadcast_to_dashboards({
            'type': 'escalation_required',
            'data': escalation
        })
    
    # Remediation strategy implementations
    async def handle_high_cpu(self, agent_id: str, context: Dict) -> bool:
        """Handle high CPU usage"""
        self.logger.info(f"Handling high CPU for agent {agent_id}")
        
        # Send command to agent to kill high CPU processes
        command = {
            'type': 'remediation',
            'action': 'kill_high_cpu_processes',
            'threshold': 50  # Kill processes using >50% CPU
        }
        
        success = await self.websocket_manager.send_to_agent(agent_id, command)
        
        if success:
            # Wait and verify improvement
            await asyncio.sleep(30)
            return await self.verify_cpu_improvement(agent_id)
        
        return False
    
    async def handle_high_memory(self, agent_id: str, context: Dict) -> bool:
        """Handle high memory usage"""
        self.logger.info(f"Handling high memory for agent {agent_id}")
        
        command = {
            'type': 'remediation',
            'action': 'clear_memory',
            'methods': ['garbage_collection', 'cache_clear']
        }
        
        success = await self.websocket_manager.send_to_agent(agent_id, command)
        
        if success:
            await asyncio.sleep(20)
            return await self.verify_memory_improvement(agent_id)
        
        return False
    
    async def handle_high_disk(self, agent_id: str, context: Dict) -> bool:
        """Handle high disk usage"""
        self.logger.info(f"Handling high disk usage for agent {agent_id}")
        
        command = {
            'type': 'remediation',
            'action': 'cleanup_disk',
            'targets': ['temp_files', 'logs', 'cache']
        }
        
        success = await self.websocket_manager.send_to_agent(agent_id, command)
        
        if success:
            await asyncio.sleep(30)
            return await self.verify_disk_improvement(agent_id)
        
        return False
    
    async def handle_network_anomaly(self, agent_id: str, context: Dict) -> bool:
        """Handle network anomaly"""
        self.logger.info(f"Handling network anomaly for agent {agent_id}")
        
        # Check if it's a DDoS-like attack
        if 'ddos' in context.get('type', '').lower():
            # Temporarily isolate the agent
            await self.isolate_agent(agent_id)
            return True
        
        # For other network issues, try to restart network
        command = {
            'type': 'remediation',
            'action': 'restart_network'
        }
        
        return await self.websocket_manager.send_to_agent(agent_id, command)
    
    async def handle_agent_offline(self, agent_id: str, context: Dict) -> bool:
        """Handle offline agent"""
        self.logger.warning(f"Handling offline agent {agent_id}")
        
        # Find mirror/backup agent
        mirror_agent = await self.find_mirror_agent(agent_id)
        
        if mirror_agent:
            # Transfer responsibilities to mirror
            await self.transfer_to_mirror(agent_id, mirror_agent)
            return True
        
        # No mirror available, mark for manual intervention
        return False
    
    async def handle_security_threat(self, agent_id: str, context: Dict) -> bool:
        """Handle security threat"""
        self.logger.critical(f"Handling security threat for agent {agent_id}")
        
        # Immediately isolate the agent
        await self.isolate_agent(agent_id)
        
        # Create security incident
        incident = {
            'agent_id': agent_id,
            'threat_type': context.get('type'),
            'severity': 'high',
            'timestamp': datetime.utcnow().isoformat(),
            'context': context
        }
        
        await self.mongo_handler.store_security_incident(incident)
        
        return True
    
    # Utility methods
    async def isolate_agent(self, agent_id: str):
        """Isolate agent from network"""
        self.logger.warning(f"Isolating agent {agent_id}")
        
        # Update agent status in Neo4j
        await self.neo4j_handler.update_agent_status(agent_id, "isolated")
        
        # Send isolation command
        command = {
            'type': 'isolation',
            'action': 'isolate',
            'reason': 'security_threat'
        }
        
        await self.websocket_manager.send_to_agent(agent_id, command)
        
        # Notify other agents to avoid this agent
        await self.websocket_manager.broadcast_to_agents({
            'type': 'agent_isolated',
            'isolated_agent': agent_id
        }, exclude_agent=agent_id)
    
    async def find_mirror_agent(self, agent_id: str) -> Optional[str]:
        """Find mirror agent for failover"""
        # Query Neo4j for mirror relationships
        mirrors = await self.neo4j_handler.get_agent_mirrors(agent_id)
        
        # Return first available mirror
        for mirror_id in mirrors:
            if self.websocket_manager.is_agent_connected(mirror_id):
                return mirror_id
        
        return None
    
    async def transfer_to_mirror(self, failed_agent: str, mirror_agent: str):
        """Transfer responsibilities to mirror agent"""
        self.logger.info(f"Transferring from {failed_agent} to {mirror_agent}")
        
        # Send takeover command to mirror
        command = {
            'type': 'takeover',
            'failed_agent': failed_agent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.send_to_agent(mirror_agent, command)
        
        # Update relationships in Neo4j
        await self.neo4j_handler.create_takeover_relationship(mirror_agent, failed_agent)
    
    async def verify_cpu_improvement(self, agent_id: str) -> bool:
        """Verify CPU usage has improved"""
        # This would check recent metrics
        # For now, return True as placeholder
        return True
    
    async def verify_memory_improvement(self, agent_id: str) -> bool:
        """Verify memory usage has improved"""
        return True
    
    async def verify_disk_improvement(self, agent_id: str) -> bool:
        """Verify disk usage has improved"""
        return True
    
    async def monitor_agent_health(self):
        """Monitor agent health and trigger remediations"""
        while self.running:
            try:
                # Check for agents that haven't sent heartbeat recently
                offline_agents = await self.mongo_handler.get_offline_agents(minutes=5)
                
                for agent_id in offline_agents:
                    if not self.websocket_manager.is_agent_connected(agent_id):
                        await self.trigger_remediation(agent_id, 'agent_offline', {
                            'reason': 'no_heartbeat',
                            'last_seen': datetime.utcnow().isoformat()
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in agent health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def process_remediation_queue(self):
        """Process pending remediations"""
        while self.running:
            try:
                # Check for stuck remediations
                for remediation_id, remediation in list(self.active_remediations.items()):
                    started_at = datetime.fromisoformat(remediation['started_at'])
                    if datetime.utcnow() - started_at > timedelta(minutes=10):
                        self.logger.warning(f"Remediation {remediation_id} appears stuck, cleaning up")
                        self.active_remediations.pop(remediation_id, None)
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in remediation queue processing: {e}")
                await asyncio.sleep(30)
