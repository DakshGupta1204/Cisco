"""
Aegis of Alderaan - Distributed Node Manager
Manages multi-laptop distributed system with JWT authentication
"""

import asyncio
import json
import logging
import socket
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import requests
from jwt_utils import JWTManager

class NodeType(Enum):
    GUARDIAN = "guardian"
    PEER = "peer"
    
class NodeStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"

@dataclass
class NodeInfo:
    node_id: str
    node_type: NodeType
    hostname: str
    ip_address: str
    port: int
    status: NodeStatus
    jwt_token: str
    last_seen: datetime
    capabilities: List[str]
    system_metrics: Dict
    connections: Set[str]  # Connected node IDs
    
    def to_dict(self):
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "status": self.status.value,
            "jwt_token": self.jwt_token,
            "last_seen": self.last_seen.isoformat(),
            "capabilities": self.capabilities,
            "system_metrics": self.system_metrics,
            "connections": list(self.connections)
        }

@dataclass
class PeerConnection:
    peer_id: str
    websocket: Optional[object]
    last_ping: datetime
    is_authenticated: bool
    connection_quality: float
    latency_ms: int

class DistributedNodeManager:
    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
        self.logger = logging.getLogger(__name__)
        
        # Node registry
        self.nodes: Dict[str, NodeInfo] = {}
        self.peer_connections: Dict[str, PeerConnection] = {}
        
        # Guardian-specific
        self.is_guardian = False
        self.guardian_node_id = None
        self.guardian_endpoint = None
        
        # Peer-specific
        self.my_node_id = None
        self.my_node_info = None
        
        # WebSocket connections
        self.websocket_connections: Dict[str, object] = {}
        
        # Distributed locks and coordination
        self.coordination_lock = asyncio.Lock()
        
        # Initialize node
        self._initialize_node()
        
    def _initialize_node(self):
        """Initialize current node"""
        try:
            # Generate unique node ID
            self.my_node_id = f"node-{uuid.uuid4().hex[:8]}"
            
            # Get system information
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            # Determine node type from environment or config
            node_type = NodeType.GUARDIAN if self._is_guardian_node() else NodeType.PEER
            self.is_guardian = (node_type == NodeType.GUARDIAN)
            
            # Create node info
            self.my_node_info = NodeInfo(
                node_id=self.my_node_id,
                node_type=node_type,
                hostname=hostname,
                ip_address=ip_address,
                port=3001 if self.is_guardian else 3002,
                status=NodeStatus.ONLINE,
                jwt_token="",  # Will be generated
                last_seen=datetime.utcnow(),
                capabilities=self._get_node_capabilities(),
                system_metrics={},
                connections=set()
            )
            
            # Generate JWT token for this node
            self.my_node_info.jwt_token = self._generate_node_token()
            
            self.logger.info(f"Initialized {node_type.value} node: {self.my_node_id} on {ip_address}:{self.my_node_info.port}")
            
        except Exception as e:
            self.logger.error(f"Node initialization failed: {e}")
            raise
            
    def _is_guardian_node(self) -> bool:
        """Determine if this node should be the guardian"""
        # Check environment variable or configuration
        import os
        return os.getenv('NODE_TYPE', 'peer').lower() == 'guardian'
        
    def _get_node_capabilities(self) -> List[str]:
        """Get capabilities of this node"""
        capabilities = [
            "metrics_collection",
            "health_monitoring", 
            "peer_communication"
        ]
        
        if self.is_guardian:
            capabilities.extend([
                "ai_analysis",
                "mirror_coordination",
                "attack_simulation",
                "central_management"
            ])
        else:
            capabilities.extend([
                "mirror_hosting",
                "load_balancing",
                "distributed_processing"
            ])
            
        return capabilities
        
    def _generate_node_token(self) -> str:
        """Generate JWT token for this node"""
        payload = {
            "node_id": self.my_node_id,
            "node_type": self.my_node_info.node_type.value,
            "hostname": self.my_node_info.hostname,
            "ip_address": self.my_node_info.ip_address,
            "capabilities": self.my_node_info.capabilities
        }
        
        # Long-lived token for node-to-node communication (24 hours)
        return self.jwt_manager.generate_token(payload, expires_in=86400)
        
    async def register_peer(self, peer_info: Dict) -> Dict:
        """Register a new peer node"""
        try:
            # Validate peer information
            required_fields = ["node_id", "hostname", "ip_address", "port", "jwt_token"]
            for field in required_fields:
                if field not in peer_info:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate JWT token
            token_payload = self.jwt_manager.validate_token(peer_info["jwt_token"])
            if not token_payload:
                raise ValueError("Invalid JWT token")
                
            # Create node info
            node_info = NodeInfo(
                node_id=peer_info["node_id"],
                node_type=NodeType.PEER,
                hostname=peer_info["hostname"],
                ip_address=peer_info["ip_address"],
                port=peer_info["port"],
                status=NodeStatus.CONNECTING,
                jwt_token=peer_info["jwt_token"],
                last_seen=datetime.utcnow(),
                capabilities=peer_info.get("capabilities", []),
                system_metrics=peer_info.get("system_metrics", {}),
                connections=set()
            )
            
            # Register the node
            async with self.coordination_lock:
                self.nodes[node_info.node_id] = node_info
                
            self.logger.info(f"Registered peer: {node_info.node_id} from {node_info.ip_address}")
            
            # Return registration response
            return {
                "status": "registered",
                "node_id": node_info.node_id,
                "guardian_id": self.my_node_id,
                "network_topology": self._get_network_topology(),
                "assigned_capabilities": self._assign_peer_capabilities(node_info),
                "connection_endpoints": self._get_connection_endpoints()
            }
            
        except Exception as e:
            self.logger.error(f"Peer registration failed: {e}")
            raise
            
    async def connect_to_guardian(self, guardian_endpoint: str) -> Dict:
        """Connect to guardian node (for peer nodes)"""
        try:
            self.guardian_endpoint = guardian_endpoint
            
            # Prepare registration data
            registration_data = {
                "node_id": self.my_node_id,
                "hostname": self.my_node_info.hostname,
                "ip_address": self.my_node_info.ip_address,
                "port": self.my_node_info.port,
                "jwt_token": self.my_node_info.jwt_token,
                "capabilities": self.my_node_info.capabilities,
                "system_metrics": await self._collect_system_metrics()
            }
            
            # Send registration request
            response = requests.post(
                f"{guardian_endpoint}/distributed/register",
                json=registration_data,
                headers={"Authorization": f"Bearer {self.my_node_info.jwt_token}"}
            )
            
            if response.status_code == 200:
                registration_result = response.json()
                self.guardian_node_id = registration_result["guardian_id"]
                
                # Establish WebSocket connection
                await self._establish_guardian_websocket()
                
                self.logger.info(f"Successfully connected to guardian: {self.guardian_node_id}")
                return registration_result
            else:
                raise Exception(f"Registration failed: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Guardian connection failed: {e}")
            raise
            
    async def connect_to_peer(self, peer_endpoint: str, peer_id: str) -> bool:
        """Connect to another peer node"""
        try:
            # Establish WebSocket connection to peer
            websocket_url = f"ws://{peer_endpoint}/distributed/peer-connect"
            
            websocket = await websockets.connect(
                websocket_url,
                extra_headers={"Authorization": f"Bearer {self.my_node_info.jwt_token}"}
            )
            
            # Send connection handshake
            handshake = {
                "type": "peer_connect",
                "node_id": self.my_node_id,
                "node_info": self.my_node_info.to_dict()
            }
            
            await websocket.send(json.dumps(handshake))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("status") == "connected":
                # Store connection
                self.peer_connections[peer_id] = PeerConnection(
                    peer_id=peer_id,
                    websocket=websocket,
                    last_ping=datetime.utcnow(),
                    is_authenticated=True,
                    connection_quality=1.0,
                    latency_ms=0
                )
                
                self.my_node_info.connections.add(peer_id)
                
                self.logger.info(f"Connected to peer: {peer_id}")
                return True
            else:
                await websocket.close()
                return False
                
        except Exception as e:
            self.logger.error(f"Peer connection failed: {e}")
            return False
            
    async def broadcast_to_peers(self, message: Dict, exclude_nodes: Set[str] = None):
        """Broadcast message to all connected peers"""
        exclude_nodes = exclude_nodes or set()
        
        for peer_id, connection in self.peer_connections.items():
            if peer_id in exclude_nodes:
                continue
                
            try:
                if connection.websocket and connection.is_authenticated:
                    await connection.websocket.send(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Failed to broadcast to {peer_id}: {e}")
                # Mark connection as failed
                connection.is_authenticated = False
                
    async def handle_peer_message(self, peer_id: str, message: Dict):
        """Handle incoming message from peer"""
        try:
            message_type = message.get("type")
            
            if message_type == "metrics_update":
                await self._handle_metrics_update(peer_id, message["data"])
            elif message_type == "health_status":
                await self._handle_health_status(peer_id, message["data"])
            elif message_type == "mirror_request":
                await self._handle_mirror_request(peer_id, message["data"])
            elif message_type == "attack_alert":
                await self._handle_attack_alert(peer_id, message["data"])
            elif message_type == "ping":
                await self._handle_ping(peer_id, message)
            else:
                self.logger.warning(f"Unknown message type from {peer_id}: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message from {peer_id}: {e}")
            
    async def _collect_system_metrics(self) -> Dict:
        """Collect current system metrics"""
        import psutil
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return {}
            
    def _get_network_topology(self) -> Dict:
        """Get current network topology"""
        return {
            "guardian": self.my_node_info.to_dict() if self.is_guardian else None,
            "peers": [node.to_dict() for node in self.nodes.values() if node.node_type == NodeType.PEER],
            "connections": self._get_connection_matrix(),
            "total_nodes": len(self.nodes) + 1
        }
        
    def _get_connection_matrix(self) -> Dict:
        """Get connection matrix between nodes"""
        matrix = {}
        
        # Add this node's connections
        matrix[self.my_node_id] = list(self.my_node_info.connections)
        
        # Add other nodes' connections
        for node in self.nodes.values():
            matrix[node.node_id] = list(node.connections)
            
        return matrix
        
    def _assign_peer_capabilities(self, peer_node: NodeInfo) -> List[str]:
        """Assign specific capabilities to peer based on network needs"""
        assigned = []
        
        # Basic capabilities for all peers
        assigned.extend(["metrics_collection", "health_monitoring"])
        
        # Assign mirror hosting based on node resources
        if len([n for n in self.nodes.values() if "mirror_hosting" in n.capabilities]) < 2:
            assigned.append("mirror_hosting")
            
        # Assign load balancing to capable nodes
        if peer_node.system_metrics.get("cpu_percent", 0) < 50:
            assigned.append("load_balancing")
            
        return assigned
        
    def _get_connection_endpoints(self) -> Dict:
        """Get connection endpoints for peer-to-peer communication"""
        return {
            "guardian_websocket": f"ws://{self.my_node_info.ip_address}:{self.my_node_info.port}/distributed/guardian-connect",
            "peer_websocket": f"ws://{self.my_node_info.ip_address}:{self.my_node_info.port}/distributed/peer-connect",
            "metrics_endpoint": f"http://{self.my_node_info.ip_address}:{self.my_node_info.port}/distributed/metrics",
            "health_endpoint": f"http://{self.my_node_info.ip_address}:{self.my_node_info.port}/distributed/health"
        }
        
    async def _establish_guardian_websocket(self):
        """Establish WebSocket connection to guardian"""
        try:
            guardian_ws_url = f"ws://{self.guardian_endpoint.replace('http://', '').replace('https://', '')}/distributed/guardian-connect"
            
            websocket = await websockets.connect(
                guardian_ws_url,
                extra_headers={"Authorization": f"Bearer {self.my_node_info.jwt_token}"}
            )
            
            self.websocket_connections["guardian"] = websocket
            
            # Start listening for guardian messages
            asyncio.create_task(self._listen_to_guardian(websocket))
            
        except Exception as e:
            self.logger.error(f"Guardian WebSocket connection failed: {e}")
            
    async def _listen_to_guardian(self, websocket):
        """Listen for messages from guardian"""
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_peer_message("guardian", data)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Guardian connection closed")
        except Exception as e:
            self.logger.error(f"Guardian listening error: {e}")
            
    async def _handle_metrics_update(self, peer_id: str, metrics_data: Dict):
        """Handle metrics update from peer"""
        if peer_id in self.nodes:
            self.nodes[peer_id].system_metrics = metrics_data
            self.nodes[peer_id].last_seen = datetime.utcnow()
            
    async def _handle_health_status(self, peer_id: str, health_data: Dict):
        """Handle health status update from peer"""
        if peer_id in self.nodes:
            status = NodeStatus(health_data.get("status", "online"))
            self.nodes[peer_id].status = status
            
    async def _handle_mirror_request(self, peer_id: str, mirror_data: Dict):
        """Handle mirror request from peer"""
        # Implement mirror coordination logic
        pass
        
    async def _handle_attack_alert(self, peer_id: str, attack_data: Dict):
        """Handle attack alert from peer"""
        # Implement distributed attack response
        pass
        
    async def _handle_ping(self, peer_id: str, ping_data: Dict):
        """Handle ping from peer"""
        if peer_id in self.peer_connections:
            self.peer_connections[peer_id].last_ping = datetime.utcnow()
            
        # Send pong response
        pong = {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": self.my_node_id
        }
        
        if peer_id in self.peer_connections:
            try:
                await self.peer_connections[peer_id].websocket.send(json.dumps(pong))
            except:
                pass
                
    async def get_distributed_status(self) -> Dict:
        """Get comprehensive distributed system status"""
        return {
            "local_node": self.my_node_info.to_dict(),
            "connected_peers": len(self.peer_connections),
            "network_topology": self._get_network_topology(),
            "system_health": await self._assess_distributed_health(),
            "coordination_status": self._get_coordination_status()
        }
        
    async def _assess_distributed_health(self) -> Dict:
        """Assess overall distributed system health"""
        online_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.ONLINE) + 1
        total_nodes = len(self.nodes) + 1
        
        health_score = online_nodes / total_nodes if total_nodes > 0 else 0
        
        return {
            "overall_health": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.5 else "critical",
            "health_score": health_score,
            "online_nodes": online_nodes,
            "total_nodes": total_nodes,
            "network_partitions": self._detect_network_partitions()
        }
        
    def _detect_network_partitions(self) -> List[str]:
        """Detect network partitions in the distributed system"""
        # Simple partition detection logic
        partitions = []
        
        # Check if any nodes haven't been seen recently
        for node in self.nodes.values():
            if (datetime.utcnow() - node.last_seen).seconds > 60:
                partitions.append(f"Node {node.node_id} may be partitioned")
                
        return partitions
        
    def _get_coordination_status(self) -> Dict:
        """Get coordination and consensus status"""
        return {
            "guardian_online": self.guardian_node_id is not None,
            "peer_connections_healthy": len([c for c in self.peer_connections.values() if c.is_authenticated]),
            "coordination_lock_held": self.coordination_lock.locked(),
            "last_coordination": datetime.utcnow().isoformat()
        }

    async def get_network_status(self) -> Dict:
        """Get the status of the distributed network for frontend"""
        try:
            # Get basic network info
            topology = self._get_network_topology()
            
            # Convert to frontend-compatible format
            peers = {}
            for node in self.nodes.values():
                peers[node.node_id] = {
                    "node_id": node.node_id,
                    "address": f"{node.ip_address}:{node.port}",
                    "status": "healthy" if node.status == NodeStatus.ONLINE else "unhealthy",
                    "last_heartbeat": node.last_seen.isoformat(),
                    "metrics": {
                        "cpu_usage": node.system_metrics.get("cpu_percent", 0),
                        "memory_usage": node.system_metrics.get("memory_percent", 0),
                        "network_io": {
                            "bytes_sent": 0,
                            "bytes_recv": 0
                        },
                        "disk_io": {
                            "read_bytes": 0,
                            "write_bytes": 0
                        },
                        "active_connections": node.system_metrics.get("network_connections", 0),
                        "threats_detected": 0
                    },
                    "role": "peer"
                }
            
            return {
                "node_id": self.my_node_id,
                "role": "guardian",
                "connected_peers": len(self.nodes),
                "healthy_peers": len([n for n in self.nodes.values() if n.status == NodeStatus.ONLINE]),
                "last_updated": datetime.utcnow().isoformat(),
                "peers": peers
            }
        except Exception as e:
            self.logger.error(f"Failed to get network status: {e}")
            return {
                "node_id": self.my_node_id,
                "role": "guardian", 
                "connected_peers": 0,
                "healthy_peers": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "peers": {}
            }

    async def update_node_heartbeat(self, node_id: str):
        """Update heartbeat for a node"""
        if node_id in self.nodes:
            self.nodes[node_id].last_seen = datetime.utcnow()
            self.nodes[node_id].status = NodeStatus.ONLINE
            self.logger.debug(f"Heartbeat updated for {node_id}")

    async def update_node_metrics(self, node_id: str, metrics: Dict):
        """Update metrics for a node"""
        if node_id in self.nodes:
            self.nodes[node_id].system_metrics = metrics
            self.nodes[node_id].last_seen = datetime.utcnow()
            self.logger.debug(f"Metrics updated for {node_id}")

    async def coordinate_healing_action(self, target_node: str, strategy: Dict) -> Dict:
        """Coordinate a healing action for a specific node"""
        try:
            if target_node not in self.nodes:
                raise ValueError(f"Node {target_node} not found")
            
            # Send healing command to target node
            healing_command = {
                "type": "healing_action",
                "strategy": strategy,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, this would send via WebSocket
            self.logger.info(f"Coordinating healing for {target_node} with strategy: {strategy.get('strategy')}")
            
            return {
                "status": "healing_coordinated",
                "target_node": target_node,
                "strategy": strategy,
                "coordinated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Healing coordination failed: {e}")
            raise

    async def simulate_attack(self, attack_type: str, attack_params: Dict) -> Dict:
        """Simulate an attack on a target agent"""
        try:
            target_agent = attack_params.get("target_agent")
            if not target_agent:
                raise ValueError("target_agent is required")
            
            if target_agent not in self.nodes:
                raise ValueError(f"Target agent {target_agent} not found")
            
            # Prepare attack simulation
            simulation_id = f"sim_{attack_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            attack_command = {
                "type": "simulate_attack",
                "attack_type": attack_type,
                "simulation_id": simulation_id,
                "parameters": attack_params,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, this would send via WebSocket
            self.logger.info(f"Simulating {attack_type} attack on {target_agent}")
            
            return {
                "status": "attack_simulated",
                "simulation_id": simulation_id,
                "attack_type": attack_type,
                "target_agent": target_agent,
                "started_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Attack simulation failed: {e}")
            raise

    def get_health_status(self) -> Dict:
        """Get health status of the distributed manager"""
        return {
            "status": "healthy" if self.my_node_info else "unhealthy",
            "node_id": self.my_node_id,
            "is_guardian": self.is_guardian,
            "connected_peers": len(self.nodes),
            "active_connections": len(self.peer_connections)
        }
