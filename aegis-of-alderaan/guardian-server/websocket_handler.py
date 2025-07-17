"""
Aegis of Alderaan - WebSocket Manager
Manages real-time agent and dashboard connections
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        # Active connections
        self.agent_connections: Dict[str, WebSocket] = {}  # agent_id -> websocket
        self.dashboard_connections: Set[WebSocket] = set()
        self.websocket_to_agent: Dict[WebSocket, str] = {}  # websocket -> agent_id
        
        self.logger = logging.getLogger(__name__)
        
    async def connect_agent(self, websocket: WebSocket):
        """Accept agent WebSocket connection with JWT validation"""
        try:
            # Get authorization header
            auth_header = websocket.headers.get('authorization', '')
            
            if not auth_header.startswith('Bearer '):
                self.logger.warning("WebSocket connection rejected: Missing or invalid authorization header")
                await websocket.close(code=1008, reason="Authentication required")
                return
            
            # Extract and validate JWT token
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Import JWT manager here to avoid circular imports
            from jwt_utils import JWTManager
            jwt_manager = JWTManager()
            
            payload = jwt_manager.validate_token(token)
            if not payload:
                self.logger.warning("WebSocket connection rejected: Invalid JWT token")
                await websocket.close(code=1008, reason="Invalid token")
                return
            
            # Accept the connection
            await websocket.accept()
            
            # Store agent info from JWT payload
            agent_id = payload.get('agent_id')
            if agent_id:
                await self.register_agent(websocket, agent_id)
            
            self.logger.info(f"Agent WebSocket connected: {agent_id}")
            
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            try:
                await websocket.close(code=1011, reason="Server error")
            except:
                pass
    
    async def disconnect_agent(self, websocket: WebSocket):
        """Handle agent disconnection"""
        agent_id = self.websocket_to_agent.get(websocket)
        
        if agent_id:
            # Remove from mappings
            self.agent_connections.pop(agent_id, None)
            self.websocket_to_agent.pop(websocket, None)
            
            self.logger.info(f"Agent {agent_id} disconnected")
            
            # Notify dashboards
            await self.broadcast_to_dashboards({
                "type": "agent_disconnected",
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            self.logger.info("Unregistered agent disconnected")
    
    async def register_agent(self, websocket: WebSocket, agent_id: str):
        """Register an agent with its WebSocket connection"""
        # Remove existing connection if any
        if agent_id in self.agent_connections:
            old_websocket = self.agent_connections[agent_id]
            self.websocket_to_agent.pop(old_websocket, None)
        
        # Register new connection
        self.agent_connections[agent_id] = websocket
        self.websocket_to_agent[websocket] = agent_id
        
        self.logger.info(f"Agent {agent_id} registered")
        
        # Notify dashboards
        await self.broadcast_to_dashboards({
            "type": "agent_connected",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Accept dashboard WebSocket connection"""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        self.logger.info(f"Dashboard connected. Total dashboards: {len(self.dashboard_connections)}")
        
        # Send current agent status
        await self.send_agent_status_to_dashboard(websocket)
    
    async def disconnect_dashboard(self, websocket: WebSocket):
        """Handle dashboard disconnection"""
        self.dashboard_connections.discard(websocket)
        self.logger.info(f"Dashboard disconnected. Total dashboards: {len(self.dashboard_connections)}")
    
    async def send_to_agent(self, agent_id: str, message: Dict) -> bool:
        """Send message to specific agent"""
        websocket = self.agent_connections.get(agent_id)
        
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
                self.logger.debug(f"Message sent to agent {agent_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to send message to agent {agent_id}: {e}")
                # Clean up disconnected agent
                await self.disconnect_agent(websocket)
                return False
        else:
            self.logger.warning(f"Agent {agent_id} not connected")
            return False
    
    async def broadcast_to_agents(self, message: Dict, exclude_agent: str = None):
        """Broadcast message to all connected agents"""
        disconnected_agents = []
        
        for agent_id, websocket in self.agent_connections.items():
            if exclude_agent and agent_id == exclude_agent:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Failed to broadcast to agent {agent_id}: {e}")
                disconnected_agents.append(websocket)
        
        # Clean up disconnected agents
        for websocket in disconnected_agents:
            await self.disconnect_agent(websocket)
    
    async def broadcast_to_dashboards(self, message: Dict):
        """Broadcast message to all connected dashboards"""
        disconnected_dashboards = []
        
        for websocket in self.dashboard_connections.copy():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Failed to broadcast to dashboard: {e}")
                disconnected_dashboards.append(websocket)
        
        # Clean up disconnected dashboards
        for websocket in disconnected_dashboards:
            await self.disconnect_dashboard(websocket)
    
    async def send_agent_status_to_dashboard(self, websocket: WebSocket):
        """Send current agent status to a specific dashboard"""
        try:
            agent_status = {
                "type": "agent_status",
                "data": {
                    "connected_agents": list(self.agent_connections.keys()),
                    "total_count": len(self.agent_connections),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await websocket.send_text(json.dumps(agent_status))
        except Exception as e:
            self.logger.error(f"Failed to send agent status to dashboard: {e}")
    
    def get_connected_agents(self) -> List[str]:
        """Get list of connected agent IDs"""
        return list(self.agent_connections.keys())
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get connection counts"""
        return {
            "agents": len(self.agent_connections),
            "dashboards": len(self.dashboard_connections)
        }
    
    def is_agent_connected(self, agent_id: str) -> bool:
        """Check if agent is connected"""
        return agent_id in self.agent_connections
    
    async def send_health_check_to_agent(self, agent_id: str) -> bool:
        """Send health check to specific agent"""
        message = {
            "type": "health_check",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.send_to_agent(agent_id, message)
    
    async def send_failover_command(self, agent_id: str, target_agent: str):
        """Send failover command to agent"""
        message = {
            "type": "failover",
            "target_agent": target_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.send_to_agent(agent_id, message)
    
    async def notify_anomaly_to_dashboards(self, anomaly_data: Dict):
        """Notify dashboards about detected anomaly"""
        message = {
            "type": "anomaly_alert",
            "data": anomaly_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_dashboards(message)
    
    async def notify_remediation_to_dashboards(self, remediation_data: Dict):
        """Notify dashboards about remediation action"""
        message = {
            "type": "remediation_action",
            "data": remediation_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_dashboards(message)
    
    async def send_topology_update(self, topology_data: Dict):
        """Send network topology update to dashboards"""
        message = {
            "type": "topology_update",
            "data": topology_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_dashboards(message)
