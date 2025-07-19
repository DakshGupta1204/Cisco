"""
Aegis of Alderaan - Guardian Server
Central orchestration server for the resilient network protection system
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn

from websocket_handler import WebSocketManager
from jwt_utils import JWTManager
from remediation_engine import RemediationEngine
from db.mongo_handler import MongoHandler
from db.neo4j_handler import Neo4jHandler
from gemini_ai_handler import GeminiAIHandler
from models.agent import AgentModel
from models.metrics import MetricsModel, SystemMetrics, AnomalyModel
from models.auth import AuthModel
from models.distributed import PeerRegistrationModel, PeerMetricsPayload

# Initialize FastAPI app
app = FastAPI(
    title="Aegis of Alderaan - Guardian Server",
    description="Central orchestration server for resilient network protection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
websocket_manager = WebSocketManager()
jwt_manager = JWTManager()

# Initialize database handlers with error handling
try:
    mongo_handler = MongoHandler()
except ImportError:
    print("Warning: MongoDB driver not available. Some features will be disabled.")
    mongo_handler = None

try:
    neo4j_handler = Neo4jHandler()
except ImportError:
    print("Warning: Neo4j driver not available. Graph features will be disabled.")
    neo4j_handler = None

# Initialize Gemini AI handler
gemini_ai = GeminiAIHandler()

try:
    remediation_engine = RemediationEngine(mongo_handler, neo4j_handler, websocket_manager)
except Exception:
    print("Warning: Remediation engine could not be initialized.")
    remediation_engine = None

# Initialize Distributed Node Manager
from distributed_manager import DistributedNodeManager
distributed_manager = DistributedNodeManager(jwt_manager)

# Security
security = HTTPBearer()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🛡️ Starting Aegis Guardian Server...")
    
    # Initialize database connections
    if mongo_handler:
        try:
            await mongo_handler.connect()
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
    
    if neo4j_handler:
        try:
            await neo4j_handler.connect()
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}")
    
    # Start remediation engine
    if remediation_engine:
        try:
            await remediation_engine.start()
        except Exception as e:
            logger.warning(f"Remediation engine start failed: {e}")
    
    logger.info("✅ Guardian Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Guardian Server...")
    
    if remediation_engine:
        await remediation_engine.stop()
    if mongo_handler:
        await mongo_handler.disconnect()
    if neo4j_handler:
        await neo4j_handler.disconnect()
    
    logger.info("✅ Guardian Server shutdown complete")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    services = {
        "websocket": websocket_manager.get_connection_count()
    }
    
    if mongo_handler:
        try:
            services["mongodb"] = await mongo_handler.health_check()
        except:
            services["mongodb"] = False
    else:
        services["mongodb"] = "not_available"
    
    if neo4j_handler:
        try:
            services["neo4j"] = await neo4j_handler.health_check()
        except:
            services["neo4j"] = False
    else:
        services["neo4j"] = "not_available"
    
    if remediation_engine:
        services["remediation"] = remediation_engine.is_running()
    else:
        services["remediation"] = "not_available"
    
    # Check Gemini AI health
    try:
        services["gemini_ai"] = await gemini_ai.health_check()
    except:
        services["gemini_ai"] = False
    
    # Check Distributed Manager health
    services["distributed_manager"] = distributed_manager.get_health_status()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": services
    }

# Authentication endpoints
@app.post("/auth/agent")
async def authenticate_agent(auth_data: AuthModel):
    """Authenticate an agent and return JWT token"""
    try:
        # Validate agent credentials
        agent_info = {
            "agent_id": auth_data.agent_id,
            "hostname": auth_data.hostname,
            "role": auth_data.role,
            "authenticated_at": datetime.utcnow().isoformat()
        }
        
        # Store agent info in database if available
        if mongo_handler:
            try:
                await mongo_handler.upsert_agent(agent_info)
            except Exception as e:
                logger.warning(f"Failed to store agent info: {e}")
        
        # Generate JWT token with only serializable data
        jwt_payload = {
            "agent_id": auth_data.agent_id,
            "hostname": auth_data.hostname,
            "role": auth_data.role
        }
        
        # Get token expiration from environment (hours -> seconds)
        token_expiry_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
        token_expiry_seconds = token_expiry_hours * 3600
        
        token = jwt_manager.generate_token(jwt_payload, expires_in=token_expiry_seconds)
        
        logger.info(f"Agent authenticated: {auth_data.agent_id}")
        
        return {
            "token": token,
            "expires_in": 3600,
            "agent_id": auth_data.agent_id
        }
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@app.get("/agents")
async def get_agents():
    """Get all registered agents"""
    try:
        agents = await mongo_handler.get_all_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent information"""
    try:
        agent = await mongo_handler.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str, limit: int = 100):
    """Get metrics for a specific agent"""
    try:
        metrics = await mongo_handler.get_agent_metrics(agent_id, limit)
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Error getting metrics for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/anomalies")
async def get_anomalies(limit: int = 50):
    """Get recent anomalies"""
    try:
        anomalies = await mongo_handler.get_anomalies(limit)
        return {"anomalies": anomalies}
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/agents/{agent_id}/command")
async def send_command(agent_id: str, command: Dict):
    """Send command to specific agent"""
    try:
        # Send command via WebSocket
        success = await websocket_manager.send_to_agent(agent_id, {
            "type": "command",
            "command": command.get("command"),
            "parameters": command.get("parameters", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if success:
            return {"status": "sent", "agent_id": agent_id}
        else:
            raise HTTPException(status_code=404, detail="Agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending command to {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/network/topology")
async def get_network_topology():
    """Get network topology from Neo4j"""
    try:
        topology = await neo4j_handler.get_network_topology()
        return {"topology": topology}
    except Exception as e:
        logger.error(f"Error getting network topology: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# === DISTRIBUTED SYSTEM ENDPOINTS ===

@app.post("/distributed/register")
async def register_peer_node(registration_data: PeerRegistrationModel):
    """Register a new peer node in the distributed network"""
    try:
        # The distributed_manager will handle the logic of registration
        registration_result = await distributed_manager.register_peer(registration_data.dict())
        return registration_result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Peer registration failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Peer registration failed")

@app.post("/distributed/heartbeat/{node_id}")
async def receive_heartbeat(node_id: str):
    """Receive heartbeat from a peer node"""
    try:
        await distributed_manager.update_node_heartbeat(node_id)
        return {"status": "heartbeat_received"}
    except Exception as e:
        logger.error(f"Heartbeat processing failed for {node_id}: {e}")
        raise HTTPException(status_code=500, detail="Heartbeat processing failed")

@app.post("/distributed/metrics/{node_id}")
async def receive_metrics(node_id: str, payload: PeerMetricsPayload):
    """Receive metrics from a peer node"""
    try:
        await distributed_manager.update_node_metrics(node_id, payload.metrics.dict())
        return {"status": "metrics_received"}
    except Exception as e:
        logger.error(f"Metrics processing failed for {node_id}: {e}")
        raise HTTPException(status_code=500, detail="Metrics processing failed")

@app.get("/distributed/network/status")
async def get_distributed_network_status():
    """Get the status of the entire distributed network"""
    try:
        status = await distributed_manager.get_network_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get network status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get network status")

@app.post("/distributed/healing/coordinate")
async def coordinate_healing(healing_request: Dict):
    """Coordinate a healing action for a specific node"""
    try:
        target_node = healing_request.get("target_node")
        strategy = healing_request.get("healing_strategy")
        if not target_node or not strategy:
            raise HTTPException(status_code=400, detail="target_node and healing_strategy are required")
        
        result = await distributed_manager.coordinate_healing_action(target_node, strategy)
        return result
    except Exception as e:
        logger.error(f"Healing coordination failed: {e}")
        raise HTTPException(status_code=500, detail="Healing coordination failed")

@app.post("/ai/healing/strategy/{agent_id}")
async def get_healing_strategy(agent_id: str):
    """Get AI-recommended healing strategy for an agent"""
    try:
        # Mock healing strategy for now - in real implementation would use AI
        strategy = {
            "strategy": "restart_service",
            "confidence": 0.85,
            "estimated_time_seconds": 30,
            "details": f"Recommended action for {agent_id}: Restart the agent service to resolve connectivity issues."
        }
        return strategy
    except Exception as e:
        logger.error(f"Failed to get healing strategy: {e}")
        raise HTTPException(status_code=500, detail="Failed to get healing strategy")

@app.post("/ai/analyze/health/{agent_id}")
async def analyze_agent_health(agent_id: str):
    """Analyze agent health using AI"""
    try:
        # Mock AI analysis for now - in real implementation would use Gemini AI
        analysis = {
            "agent_id": agent_id,
            "status": "analysis_started",
            "details": f"AI health analysis initiated for agent {agent_id}. This will analyze system metrics, performance patterns, and potential issues."
        }
        return analysis
    except Exception as e:
        logger.error(f"AI health analysis failed: {e}")
        raise HTTPException(status_code=500, detail="AI health analysis failed")

@app.post("/simulate/attack/{attack_type}")
async def simulate_distributed_attack(attack_type: str, attack_params: Dict):
    """Simulate an attack on a target agent in the distributed network"""
    try:
        result = await distributed_manager.simulate_attack(attack_type, attack_params)
        return result
    except Exception as e:
        logger.error(f"Attack simulation failed: {e}")
        raise HTTPException(status_code=500, detail="Attack simulation failed")

# === END DISTRIBUTED SYSTEM ENDPOINTS ===

# === ATTACK SIMULATION ENDPOINTS FOR FRONTEND ===

@app.post("/simulate/attack")
async def simulate_attack(attack_config: Dict):
    """Simulate an attack for testing (Frontend triggered)"""
    try:
        attack_type = attack_config.get("type")
        target_agent = attack_config.get("target_agent")
        duration = attack_config.get("duration", 30)  # seconds
        intensity = attack_config.get("intensity", "medium")
        
        if not attack_type:
            raise HTTPException(status_code=400, detail="Attack type is required")
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        logger.info(f"🚨 Frontend triggered {attack_type} attack on {target_agent}")
        
        # Prepare attack simulation command
        attack_command = {
            "type": "simulate_attack",
            "attack_type": attack_type,
            "duration": duration,
            "intensity": intensity,
            "parameters": attack_config.get("parameters", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "simulation_id": f"sim_{attack_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Send attack simulation command to target agent
        success = await websocket_manager.send_to_agent(target_agent, attack_command)
        
        if success:
            # Log attack simulation start
            if mongo_handler:
                try:
                    await mongo_handler.log_attack_simulation({
                        "simulation_id": attack_command["simulation_id"],
                        "attack_type": attack_type,
                        "target_agent": target_agent,
                        "duration": duration,
                        "intensity": intensity,
                        "status": "started",
                        "started_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Failed to log attack simulation: {e}")
            
            return {
                "status": "attack_initiated",
                "simulation_id": attack_command["simulation_id"],
                "attack_type": attack_type,
                "target_agent": target_agent,
                "duration": duration,
                "intensity": intensity,
                "started_at": attack_command["timestamp"]
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/simulate/attack/cpu")
async def simulate_cpu_attack(attack_config: Dict):
    """Simulate CPU spike attack"""
    try:
        target_agent = attack_config.get("target_agent")
        cpu_percentage = attack_config.get("cpu_percentage", 80)
        duration = attack_config.get("duration", 30)
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        attack_command = {
            "type": "simulate_attack",
            "attack_type": "cpu_spike",
            "cpu_percentage": cpu_percentage,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(target_agent, attack_command)
        
        if success:
            logger.info(f"🔥 CPU attack simulated on {target_agent}: {cpu_percentage}% for {duration}s")
            return {
                "status": "cpu_attack_initiated",
                "target_agent": target_agent,
                "cpu_percentage": cpu_percentage,
                "duration": duration
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating CPU attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/simulate/attack/memory")
async def simulate_memory_attack(attack_config: Dict):
    """Simulate memory exhaustion attack"""
    try:
        target_agent = attack_config.get("target_agent")
        memory_mb = attack_config.get("memory_mb", 500)
        duration = attack_config.get("duration", 30)
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        attack_command = {
            "type": "simulate_attack",
            "attack_type": "memory_exhaustion",
            "memory_mb": memory_mb,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(target_agent, attack_command)
        
        if success:
            logger.info(f"💾 Memory attack simulated on {target_agent}: {memory_mb}MB for {duration}s")
            return {
                "status": "memory_attack_initiated",
                "target_agent": target_agent,
                "memory_mb": memory_mb,
                "duration": duration
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating memory attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/simulate/attack/network")
async def simulate_network_attack(attack_config: Dict):
    """Simulate network flooding attack"""
    try:
        target_agent = attack_config.get("target_agent")
        packet_rate = attack_config.get("packet_rate", 1000)  # packets per second
        duration = attack_config.get("duration", 30)
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        attack_command = {
            "type": "simulate_attack",
            "attack_type": "network_flood",
            "packet_rate": packet_rate,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(target_agent, attack_command)
        
        if success:
            logger.info(f"🌊 Network attack simulated on {target_agent}: {packet_rate} pps for {duration}s")
            return {
                "status": "network_attack_initiated",
                "target_agent": target_agent,
                "packet_rate": packet_rate,
                "duration": duration
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating network attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/simulate/attack/ddos")
async def simulate_ddos_attack(attack_config: Dict):
    """Simulate DDoS attack"""
    try:
        target_agent = attack_config.get("target_agent")
        request_rate = attack_config.get("request_rate", 500)  # requests per second
        duration = attack_config.get("duration", 30)
        attack_vector = attack_config.get("vector", "http_flood")  # http_flood, syn_flood, udp_flood
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        attack_command = {
            "type": "simulate_attack",
            "attack_type": "ddos",
            "vector": attack_vector,
            "request_rate": request_rate,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(target_agent, attack_command)
        
        if success:
            logger.info(f"⚡ DDoS attack simulated on {target_agent}: {attack_vector} at {request_rate} rps for {duration}s")
            return {
                "status": "ddos_attack_initiated",
                "target_agent": target_agent,
                "vector": attack_vector,
                "request_rate": request_rate,
                "duration": duration
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating DDoS attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/simulate/attack/types")
async def get_attack_types():
    """Get available attack simulation types for frontend"""
    return {
        "attack_types": [
            {
                "id": "cpu_spike",
                "name": "CPU Spike Attack",
                "description": "Simulate high CPU usage",
                "parameters": [
                    {"name": "cpu_percentage", "type": "number", "default": 80, "min": 10, "max": 100},
                    {"name": "duration", "type": "number", "default": 30, "min": 5, "max": 300}
                ]
            },
            {
                "id": "memory_exhaustion",
                "name": "Memory Exhaustion",
                "description": "Simulate memory overflow",
                "parameters": [
                    {"name": "memory_mb", "type": "number", "default": 500, "min": 100, "max": 2000},
                    {"name": "duration", "type": "number", "default": 30, "min": 5, "max": 300}
                ]
            },
            {
                "id": "network_flood",
                "name": "Network Flooding",
                "description": "Simulate network traffic overload",
                "parameters": [
                    {"name": "packet_rate", "type": "number", "default": 1000, "min": 100, "max": 10000},
                    {"name": "duration", "type": "number", "default": 30, "min": 5, "max": 300}
                ]
            },
            {
                "id": "ddos",
                "name": "DDoS Attack",
                "description": "Simulate distributed denial of service",
                "parameters": [
                    {"name": "request_rate", "type": "number", "default": 500, "min": 100, "max": 5000},
                    {"name": "vector", "type": "select", "options": ["http_flood", "syn_flood", "udp_flood"], "default": "http_flood"},
                    {"name": "duration", "type": "number", "default": 30, "min": 5, "max": 300}
                ]
            }
        ]
    }

@app.get("/simulate/attack/history")
async def get_attack_simulation_history(limit: int = 20):
    """Get history of attack simulations"""
    try:
        if mongo_handler:
            history = await mongo_handler.get_attack_simulation_history(limit)
            return {"simulations": history}
        else:
            return {"simulations": []}
    except Exception as e:
        logger.error(f"Error getting attack simulation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/simulate/attack/stop")
async def stop_attack_simulation(stop_config: Dict):
    """Stop an ongoing attack simulation"""
    try:
        target_agent = stop_config.get("target_agent")
        simulation_id = stop_config.get("simulation_id")
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required")
        
        stop_command = {
            "type": "stop_attack_simulation",
            "simulation_id": simulation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(target_agent, stop_command)
        
        if success:
            logger.info(f"🛑 Attack simulation stopped on {target_agent}")
            return {
                "status": "simulation_stopped",
                "target_agent": target_agent,
                "simulation_id": simulation_id,
                "stopped_at": stop_command["timestamp"]
            }
        else:
            raise HTTPException(status_code=404, detail="Target agent not connected")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping attack simulation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# === ENHANCED NEO4J RELATIONSHIP ENDPOINTS ===

@app.post("/agents/{agent_id}/relationships/mirror")
async def create_mirror_relationship(agent_id: str, mirror_config: Dict):
    """Create mirror relationship between agents"""
    try:
        mirror_agent = mirror_config.get("mirror_agent")
        if not mirror_agent:
            raise HTTPException(status_code=400, detail="mirror_agent is required")
        
        await neo4j_handler.create_mirror_relationship(agent_id, mirror_agent)
        
        logger.info(f"Mirror relationship created: {agent_id} <-> {mirror_agent}")
        return {
            "status": "created",
            "primary_agent": agent_id,
            "mirror_agent": mirror_agent,
            "relationship_type": "mirror"
        }
        
    except Exception as e:
        logger.error(f"Error creating mirror relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/relationships/monitor")
async def create_monitoring_relationship(agent_id: str, monitor_config: Dict):
    """Create monitoring relationship between agents"""
    try:
        target_agent = monitor_config.get("target_agent")
        if not target_agent:
            raise HTTPException(status_code=400, detail="target_agent is required")
        
        await neo4j_handler.create_monitoring_relationship(agent_id, target_agent)
        
        logger.info(f"Monitoring relationship created: {agent_id} -> {target_agent}")
        return {
            "status": "created",
            "monitor_agent": agent_id,
            "target_agent": target_agent,
            "relationship_type": "monitors"
        }
        
    except Exception as e:
        logger.error(f"Error creating monitoring relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/relationships/connect")
async def create_network_connection(agent_id: str, connection_config: Dict):
    """Create network connection between agents"""
    try:
        target_agent = connection_config.get("target_agent")
        connection_type = connection_config.get("connection_type", "CONNECTED_TO")
        
        if not target_agent:
            raise HTTPException(status_code=400, detail="target_agent is required")
        
        await neo4j_handler.create_network_connection(agent_id, target_agent, connection_type)
        
        logger.info(f"Network connection created: {agent_id} <-> {target_agent} ({connection_type})")
        return {
            "status": "created",
            "agent1": agent_id,
            "agent2": target_agent,
            "connection_type": connection_type
        }
        
    except Exception as e:
        logger.error(f"Error creating network connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/mirrors")
async def get_agent_mirrors(agent_id: str):
    """Get all mirror agents for a specific agent"""
    try:
        mirrors = await neo4j_handler.get_agent_mirrors(agent_id)
        mirror_health = await neo4j_handler.check_mirror_health(agent_id)
        
        return {
            "agent_id": agent_id,
            "mirrors": mirrors,
            "health_status": mirror_health,
            "mirror_count": len(mirrors)
        }
        
    except Exception as e:
        logger.error(f"Error getting mirrors for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network/mirror-topology")
async def get_mirror_topology():
    """Get comprehensive mirror topology"""
    try:
        topology = await neo4j_handler.get_mirror_topology()
        return {
            "mirror_topology": topology,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting mirror topology: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === SELF-HEALING ENDPOINTS ===

@app.post("/agents/{agent_id}/healing/initiate")
async def initiate_self_healing(agent_id: str, healing_config: Dict = None):
    """Initiate self-healing process for an agent"""
    try:
        # Register health issue first if provided
        if healing_config:
            issue_type = healing_config.get("issue_type", "unknown")
            severity = healing_config.get("severity", "medium")
            details = healing_config.get("details", {})
            
            await neo4j_handler.register_health_issue(agent_id, issue_type, severity, details)
        
        # Initiate healing process
        healing_result = await neo4j_handler.initiate_self_healing(agent_id)
        
        if healing_result["status"] == "initiated":
            # Notify the healing agent via WebSocket
            healing_agent = healing_result["healing_agent"]
            await websocket_manager.send_to_agent(healing_agent, {
                "type": "healing_request",
                "failed_agent": agent_id,
                "healing_id": healing_result["healing_id"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Self-healing initiated for {agent_id} by {healing_agent}")
        
        return healing_result
        
    except Exception as e:
        logger.error(f"Error initiating self-healing for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/healing/{healing_id}/complete")
async def complete_healing_process(healing_id: str, completion_data: Dict):
    """Mark a healing process as complete"""
    try:
        success = completion_data.get("success", False)
        details = completion_data.get("details", "")
        
        await neo4j_handler.complete_healing_process(healing_id, success, details)
        
        logger.info(f"Healing process {healing_id} completed: {'success' if success else 'failed'}")
        return {
            "status": "updated",
            "healing_id": healing_id,
            "success": success,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error completing healing process {healing_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healing/active")
async def get_active_healing_processes():
    """Get all active healing processes"""
    try:
        processes = await neo4j_handler.get_active_healing_processes()
        return {
            "active_processes": processes,
            "count": len(processes),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting active healing processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/mirror/setup")
async def setup_agent_mirroring(agent_id: str, mirror_setup: Dict):
    """Setup comprehensive mirroring for an agent"""
    try:
        mirror_configs = mirror_setup.get("mirrors", [])
        if not mirror_configs:
            raise HTTPException(status_code=400, detail="mirrors configuration is required")
        
        await neo4j_handler.setup_agent_mirroring(agent_id, mirror_configs)
        
        # Notify all mirror agents
        for mirror_config in mirror_configs:
            mirror_agent = mirror_config["agent_id"]
            await websocket_manager.send_to_agent(mirror_agent, {
                "type": "mirror_setup",
                "primary_agent": agent_id,
                "mirror_config": mirror_config,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Mirroring setup completed for {agent_id} with {len(mirror_configs)} mirrors")
        return {
            "status": "setup_complete",
            "primary_agent": agent_id,
            "mirror_count": len(mirror_configs),
            "mirrors": [m["agent_id"] for m in mirror_configs]
        }
        
    except Exception as e:
        logger.error(f"Error setting up mirroring for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/mirror/activate")
async def activate_mirror_agent(agent_id: str, activation_config: Dict):
    """Activate a mirror agent to take over from primary"""
    try:
        mirror_agent = activation_config.get("mirror_agent")
        if not mirror_agent:
            raise HTTPException(status_code=400, detail="mirror_agent is required")
        
        await neo4j_handler.activate_mirror(agent_id, mirror_agent)
        
        # Notify the mirror agent to take over
        await websocket_manager.send_to_agent(mirror_agent, {
            "type": "mirror_activation",
            "primary_agent": agent_id,
            "role": "active_mirror",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Notify the primary agent (if still connected)
        await websocket_manager.send_to_agent(agent_id, {
            "type": "mirror_takeover",
            "mirror_agent": mirror_agent,
            "status": "inactive",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Mirror activation: {mirror_agent} took over from {agent_id}")
        return {
            "status": "activated",
            "primary_agent": agent_id,
            "active_mirror": mirror_agent,
            "activated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error activating mirror for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating attack: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket endpoint for agents
@app.websocket("/ws/agent")
async def websocket_agent_endpoint(websocket: WebSocket):
    """WebSocket endpoint for agent connections"""
    await websocket_manager.connect_agent(websocket)
    
    try:
        while True:
            # Receive data from agent
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_agent_message(websocket, message)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect_agent(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect_agent(websocket)

# WebSocket endpoint for dashboard
@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """WebSocket endpoint for dashboard connections"""
    await websocket_manager.connect_dashboard(websocket)
    
    try:
        while True:
            # Keep connection alive and handle dashboard messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle dashboard requests
            await handle_dashboard_message(websocket, message)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect_dashboard(websocket)
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        await websocket_manager.disconnect_dashboard(websocket)

async def handle_agent_message(websocket: WebSocket, message: Dict):
    """Handle messages from agents"""
    message_type = message.get("type")
    agent_id = message.get("agent_id")
    
    logger.debug(f"Received {message_type} from {agent_id}")
    
    if message_type == "register":
        await websocket_manager.register_agent(websocket, agent_id)
        await neo4j_handler.create_or_update_agent_node(agent_id, message)
        
    elif message_type == "metrics":
        # Store metrics in MongoDB
        await mongo_handler.store_metrics(message["data"])
        
        # Analyze metrics for anomalies
        await remediation_engine.analyze_metrics(message["data"])
        
        # Broadcast to dashboard
        await websocket_manager.broadcast_to_dashboards({
            "type": "metrics_update",
            "agent_id": agent_id,
            "data": message["data"]
        })
        
    elif message_type == "anomaly":
        # Store anomaly
        await mongo_handler.store_anomaly(message["data"])
        
        # Trigger remediation
        await remediation_engine.handle_anomaly(message["data"])
        
        # Broadcast to dashboard
        await websocket_manager.broadcast_to_dashboards({
            "type": "anomaly_detected",
            "agent_id": agent_id,
            "data": message["data"]
        })
        
    elif message_type == "heartbeat":
        # Update agent status
        await mongo_handler.update_agent_heartbeat(agent_id)
        await neo4j_handler.update_agent_status(agent_id, "active")

async def handle_dashboard_message(websocket: WebSocket, message: Dict):
    """Handle messages from dashboard"""
    message_type = message.get("type")
    
    if message_type == "request_topology":
        topology = await neo4j_handler.get_network_topology()
        await websocket.send_text(json.dumps({
            "type": "topology_update",
            "data": topology
        }))
    
    elif message_type == "request_agents":
        agents = await mongo_handler.get_all_agents()
        await websocket.send_text(json.dumps({
            "type": "agents_update",
            "data": agents
        }))

# === AI-POWERED SELF-HEALING ENDPOINTS ===

@app.post("/ai/analyze/health/{agent_id}")
async def ai_analyze_health(agent_id: str):
    """Use Gemini AI to analyze agent health and recommend healing actions"""
    try:
        if not neo4j_handler:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        if not mongo_handler:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        # Get agent data from MongoDB
        agent_data = await mongo_handler.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get health issues from Neo4j
        mirror_health = await neo4j_handler.check_mirror_health(agent_id)
        
        # Combine data for AI analysis
        node_data = {
            **agent_data,
            'health_issues': mirror_health.get('health_issues', []),
            'mirrors': mirror_health.get('mirrors', [])
        }
        
        # Use Gemini AI to analyze health
        health_analysis = await gemini_ai.analyze_node_health(node_data)
        
        return {
            "agent_id": agent_id,
            "analysis": health_analysis.__dict__,
            "timestamp": datetime.utcnow().isoformat(),
            "ai_enabled": gemini_ai.enabled
        }
        
    except Exception as e:
        logger.error(f"AI health analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/mirror/recommend/{agent_id}")
async def ai_mirror_recommendation(agent_id: str):
    """Get AI recommendation for mirror activation"""
    try:
        if not neo4j_handler:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        
        # Get agent mirror health data
        mirror_health = await neo4j_handler.check_mirror_health(agent_id)
        
        # Get available mirrors
        available_mirrors = []
        for mirror_id in mirror_health.get('mirrors', []):
            mirror_data = await mongo_handler.get_agent(mirror_id) if mongo_handler else {}
            if mirror_data:
                available_mirrors.append(mirror_data)
        
        # Get AI recommendation
        recommendation = await gemini_ai.get_mirror_recommendation(mirror_health, available_mirrors)
        
        return {
            "agent_id": agent_id,
            "recommendation": recommendation.__dict__,
            "available_mirrors": available_mirrors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI mirror recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/healing/strategy/{agent_id}")
async def ai_healing_strategy(agent_id: str):
    """Generate AI-powered healing strategy"""
    try:
        if not neo4j_handler or not mongo_handler:
            raise HTTPException(status_code=503, detail="Database services not available")
        
        # Get comprehensive agent data
        agent_data = await mongo_handler.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        mirror_health = await neo4j_handler.check_mirror_health(agent_id)
        
        # Combine data
        node_data = {
            **agent_data,
            'health_issues': mirror_health.get('health_issues', []),
            'mirrors': mirror_health.get('mirrors', [])
        }
        
        # First get health analysis
        health_analysis = await gemini_ai.analyze_node_health(node_data)
        
        # Then generate healing strategy
        strategy = await gemini_ai.generate_healing_strategy(node_data, health_analysis)
        
        return {
            "agent_id": agent_id,
            "health_analysis": health_analysis.__dict__,
            "healing_strategy": strategy,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI healing strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/mirror/activate/{agent_id}")
async def ai_activate_mirror(agent_id: str):
    """Activate mirror based on AI recommendation"""
    try:
        if not neo4j_handler or not mongo_handler:
            raise HTTPException(status_code=503, detail="Database services not available")
        
        # Get AI mirror recommendation
        mirror_health = await neo4j_handler.check_mirror_health(agent_id)
        available_mirrors = []
        for mirror_id in mirror_health.get('mirrors', []):
            mirror_data = await mongo_handler.get_agent(mirror_id)
            if mirror_data:
                available_mirrors.append(mirror_data)
        
        recommendation = await gemini_ai.get_mirror_recommendation(mirror_health, available_mirrors)
        
        if not recommendation.should_activate_mirror:
            return {
                "agent_id": agent_id,
                "action": "no_activation_needed",
                "reason": "AI recommends not to activate mirror",
                "recommendation": recommendation.__dict__
            }
        
        if not recommendation.mirror_node_id:
            raise HTTPException(status_code=400, detail="No suitable mirror found")
        
        # Activate the recommended mirror
        await neo4j_handler.activate_mirror(agent_id, recommendation.mirror_node_id)
        
        # Update agent status
        await mongo_handler.update_agent_status(agent_id, "inactive")
        await mongo_handler.update_agent_status(recommendation.mirror_node_id, "active_mirror")
        
        # Notify via WebSocket
        await websocket_manager.broadcast({
            "type": "mirror_activated",
            "data": {
                "primary_agent": agent_id,
                "mirror_agent": recommendation.mirror_node_id,
                "strategy": recommendation.transition_strategy,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return {
            "agent_id": agent_id,
            "action": "mirror_activated",
            "mirror_agent": recommendation.mirror_node_id,
            "strategy": recommendation.transition_strategy,
            "ai_recommendation": recommendation.__dict__,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI mirror activation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/healing/processes")
async def get_ai_healing_processes():
    """Get all active AI-initiated healing processes"""
    try:
        if not neo4j_handler:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        
        processes = await neo4j_handler.get_active_healing_processes()
        
        return {
            "active_processes": processes,
            "count": len(processes),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get healing processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/predict/failure/{agent_id}")
async def ai_predict_failure(agent_id: str):
    """Use AI to predict potential failures"""
    try:
        if not mongo_handler:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        # Get agent data and historical metrics
        agent_data = await mongo_handler.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get historical data (last 100 records)
        historical_data = await mongo_handler.get_agent_metrics_history(agent_id, limit=100)
        
        # Use AI to predict failure risk
        prediction = await gemini_ai.predict_failure_risk(agent_data, historical_data)
        
        return {
            "agent_id": agent_id,
            "prediction": prediction,
            "historical_data_points": len(historical_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI failure prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/mirror/topology")
async def get_ai_mirror_topology():
    """Get comprehensive mirror topology with AI analysis"""
    try:
        if not neo4j_handler:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        
        # Get mirror topology from Neo4j
        topology = await neo4j_handler.get_mirror_topology()
        
        # Add AI analysis for each primary node
        ai_enhanced_topology = {}
        for primary_agent, data in topology.items():
            try:
                # Get current health analysis
                agent_data = await mongo_handler.get_agent(primary_agent) if mongo_handler else {}
                mirror_health = await neo4j_handler.check_mirror_health(primary_agent)
                
                node_data = {
                    **agent_data,
                    'health_issues': mirror_health.get('health_issues', []),
                    'mirrors': mirror_health.get('mirrors', [])
                }
                
                health_analysis = await gemini_ai.analyze_node_health(node_data)
                
                ai_enhanced_topology[primary_agent] = {
                    **data,
                    'ai_health_analysis': health_analysis.__dict__,
                    'ai_enabled': gemini_ai.enabled
                }
                
            except Exception as e:
                logger.warning(f"Failed to get AI analysis for {primary_agent}: {e}")
                ai_enhanced_topology[primary_agent] = {
                    **data,
                    'ai_health_analysis': None,
                    'ai_enabled': False
                }
        
        return {
            "mirror_topology": ai_enhanced_topology,
            "total_primary_nodes": len(ai_enhanced_topology),
            "ai_analysis_enabled": gemini_ai.enabled,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI mirror topology: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# DISTRIBUTED SYSTEM ENDPOINTS
# ========================================

@app.post("/distributed/register")
async def register_peer_node(peer_info: dict, token: str = Depends(security)):
    """Register a new peer node in the distributed system"""
    try:
        # Validate JWT token
        credentials = token.credentials
        token_payload = jwt_manager.validate_token(credentials)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Register the peer
        registration_result = await distributed_manager.register_peer(peer_info)
        
        return {
            "status": "success",
            "message": "Peer registered successfully",
            "data": registration_result
        }
        
    except Exception as e:
        logger.error(f"Peer registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/distributed/topology")
async def get_distributed_topology(token: str = Depends(security)):
    """Get complete distributed network topology"""
    try:
        # Validate JWT token
        credentials = token.credentials
        token_payload = jwt_manager.validate_token(credentials)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        topology = await distributed_manager.get_distributed_status()
        
        return {
            "status": "success",
            "data": topology,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get distributed topology: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/distributed/network/status")
async def get_network_status():
    """Get network status for frontend dashboard"""
    try:
        # Get all connected agents/peers
        connected_agents = websocket_manager.get_connected_agents()
        
        # Get distributed system status
        distributed_status = await distributed_manager.get_distributed_status()
        
        # Transform data for frontend
        peers = {}
        connected_peers = 0
        healthy_peers = 0
        
        # Add connected agents as peers
        for agent_id, agent_info in connected_agents.items():
            peers[agent_id] = {
                "node_id": agent_id,
                "hostname": agent_info.get("hostname", f"agent-{agent_id}"),
                "ip_address": agent_info.get("ip_address", "unknown"),
                "role": agent_info.get("role", "agent"),
                "health_status": agent_info.get("health_status", "healthy"),
                "last_heartbeat": agent_info.get("last_heartbeat", datetime.utcnow().isoformat()),
                "capabilities": ["metrics_collection", "self_healing", "mirror_support"],
                "metrics": agent_info.get("latest_metrics", {
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "disk_usage": 0.0,
                    "network_io": {
                        "bytes_sent": 0,
                        "bytes_recv": 0
                    }
                })
            }
            connected_peers += 1
            if agent_info.get("health_status", "healthy") == "healthy":
                healthy_peers += 1
        
        # Add distributed peers if any
        if hasattr(distributed_manager, 'peers'):
            for peer_id, peer_info in distributed_manager.peers.items():
                if peer_id not in peers:  # Avoid duplicates
                    peers[peer_id] = {
                        "node_id": peer_id,
                        "hostname": getattr(peer_info, 'hostname', f"peer-{peer_id}"),
                        "ip_address": getattr(peer_info, 'ip_address', "unknown"),
                        "role": getattr(peer_info, 'role', "peer"),
                        "health_status": getattr(peer_info, 'health_status', "healthy"),
                        "last_heartbeat": getattr(peer_info, 'last_heartbeat', datetime.utcnow()).isoformat(),
                        "capabilities": getattr(peer_info, 'capabilities', ["metrics_collection"]),
                        "metrics": getattr(peer_info, 'metrics', {
                            "cpu_usage": 0.0,
                            "memory_usage": 0.0,
                            "disk_usage": 0.0,
                            "network_io": {
                                "bytes_sent": 0,
                                "bytes_recv": 0
                            }
                        })
                    }
                    connected_peers += 1
                    if getattr(peer_info, 'health_status', "healthy") == "healthy":
                        healthy_peers += 1
        
        return {
            "node_id": distributed_manager.my_node_id if hasattr(distributed_manager, 'my_node_id') else "guardian-001",
            "role": "guardian",
            "connected_peers": connected_peers,
            "healthy_peers": healthy_peers,
            "last_updated": datetime.utcnow().isoformat(),
            "peers": peers
        }
        
    except Exception as e:
        logger.error(f"Failed to get network status: {e}")
        # Return empty status on error
        return {
            "node_id": "guardian-001",
            "role": "guardian", 
            "connected_peers": 0,
            "healthy_peers": 0,
            "last_updated": datetime.utcnow().isoformat(),
            "peers": {}
        }

@app.post("/distributed/connect-guardian")
async def connect_to_guardian(guardian_info: dict):
    """Connect this node to a guardian (for peer nodes)"""
    try:
        guardian_endpoint = guardian_info.get("endpoint")
        if not guardian_endpoint:
            raise ValueError("Guardian endpoint required")
        
        connection_result = await distributed_manager.connect_to_guardian(guardian_endpoint)
        
        return {
            "status": "success", 
            "message": "Connected to guardian successfully",
            "data": connection_result
        }
        
    except Exception as e:
        logger.error(f"Guardian connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/distributed/peer-connect")
async def connect_to_peer(peer_info: dict, token: str = Depends(security)):
    """Establish peer-to-peer connection"""
    try:
        # Validate JWT token
        credentials = token.credentials
        token_payload = jwt_manager.validate_token(credentials)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        peer_endpoint = peer_info.get("endpoint")
        peer_id = peer_info.get("peer_id")
        
        if not peer_endpoint or not peer_id:
            raise ValueError("Peer endpoint and ID required")
        
        success = await distributed_manager.connect_to_peer(peer_endpoint, peer_id)
        
        return {
            "status": "success" if success else "failed",
            "message": "Peer connection established" if success else "Peer connection failed",
            "peer_id": peer_id
        }
        
    except Exception as e:
        logger.error(f"Peer connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/distributed/nodes")
async def get_connected_nodes(token: str = Depends(security)):
    """Get list of all connected nodes"""
    try:
        # Validate JWT token
        credentials = token.credentials
        token_payload = jwt_manager.validate_token(credentials)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        nodes_info = {
            "local_node": distributed_manager.my_node_info.to_dict(),
            "connected_peers": [
                {
                    "node_id": node_id,
                    "node_info": node.to_dict(),
                    "connection_status": "connected" if node_id in distributed_manager.peer_connections else "registered"
                }
                for node_id, node in distributed_manager.nodes.items()
            ],
            "total_nodes": len(distributed_manager.nodes) + 1,
            "network_health": await distributed_manager._assess_distributed_health()
        }
        
        return {
            "status": "success",
            "data": nodes_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get connected nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/distributed/healing/coordinate")
async def coordinate_healing(request: dict):
    """Coordinate healing process across the distributed network"""
    try:
        target_node = request.get("target_node")
        healing_strategy = request.get("healing_strategy")
        
        if not target_node or not healing_strategy:
            raise ValueError("target_node and healing_strategy are required")
        
        # Send healing command to target agent via WebSocket
        if target_node in websocket_manager.connections:
            healing_message = {
                "type": "healing_command",
                "strategy": healing_strategy,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket_manager.send_to_agent(target_node, healing_message)
            
            # Broadcast healing notification to other agents
            notification = {
                "type": "healing_started",
                "target_node": target_node,
                "strategy_id": healing_strategy.get("strategy_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for agent_id in websocket_manager.connections:
                if agent_id != target_node:
                    await websocket_manager.send_to_agent(agent_id, notification)
            
            return {
                "status": "healing_initiated",
                "target_node": target_node,
                "strategy_id": healing_strategy.get("strategy_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # If using distributed manager for peers
            if hasattr(distributed_manager, 'coordinate_healing'):
                result = await distributed_manager.coordinate_healing(target_node, healing_strategy)
                return result
            else:
                raise ValueError(f"Target node {target_node} not connected")
            
    except Exception as e:
        logger.error(f"Error coordinating healing for {target_node}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/distributed/broadcast")
async def broadcast_message(message_data: dict, token: str = Depends(security)):
    """Broadcast message to all connected peers"""
    try:
        # Validate JWT token
        credentials = token.credentials
        token_payload = jwt_manager.validate_token(credentials)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Add sender information
        message_data["sender_id"] = distributed_manager.my_node_id
        message_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Broadcast to all peers
        await distributed_manager.broadcast_to_peers(message_data)
        
        return {
            "status": "success",
            "message": "Message broadcasted to all peers",
            "recipients": len(distributed_manager.peer_connections)
        }
        
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/distributed/health")
async def get_distributed_health():
    """Get health status of the distributed system"""
    try:
        health_status = await distributed_manager.get_distributed_status()
        
        return {
            "status": "success",
            "data": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get distributed health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/distributed/node-token") 
async def generate_node_token(node_info: dict):
    """Generate JWT token for a new node"""
    try:
        required_fields = ["node_id", "hostname", "ip_address"]
        for field in required_fields:
            if field not in node_info:
                raise ValueError(f"Missing required field: {field}")
        
        # Generate token payload
        payload = {
            "node_id": node_info["node_id"],
            "hostname": node_info["hostname"], 
            "ip_address": node_info["ip_address"],
            "node_type": node_info.get("node_type", "peer"),
            "capabilities": node_info.get("capabilities", [])
        }
        
        # Generate long-lived token (24 hours)
        token = jwt_manager.generate_token(payload, expires_in=86400)
        
        return {
            "status": "success",
            "node_id": node_info["node_id"],
            "token": token,
            "expires_in": 86400,
            "message": "Node token generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# WebSocket endpoint for distributed communication
@app.websocket("/distributed/guardian-connect")
async def guardian_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for peer-to-guardian communication"""
    try:
        await websocket.accept()
        
        # Wait for authentication message
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # Validate token from WebSocket headers or message
        token = auth_data.get("token") or websocket.headers.get("Authorization", "").replace("Bearer ", "")
        token_payload = jwt_manager.validate_token(token)
        
        if not token_payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        node_id = token_payload.get("node_id")
        logger.info(f"Guardian WebSocket connected: {node_id}")
        
        # Handle WebSocket communication
        try:
            while True:
                message = await websocket.receive_text()
                message_data = json.loads(message)
                
                # Handle message based on type
                await distributed_manager.handle_peer_message(node_id, message_data)
                
        except WebSocketDisconnect:
            logger.info(f"Guardian WebSocket disconnected: {node_id}")
        
    except Exception as e:
        logger.error(f"Guardian WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass

@app.websocket("/distributed/peer-connect")
async def peer_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for peer-to-peer communication"""
    try:
        await websocket.accept()
        
        # Wait for authentication message
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # Validate token
        token = auth_data.get("token") or websocket.headers.get("Authorization", "").replace("Bearer ", "")
        token_payload = jwt_manager.validate_token(token)
        
        if not token_payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        node_id = token_payload.get("node_id")
        logger.info(f"Peer WebSocket connected: {node_id}")
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "status": "connected",
            "node_id": distributed_manager.my_node_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Handle WebSocket communication
        try:
            while True:
                message = await websocket.receive_text()
                message_data = json.loads(message)
                
                # Handle peer message
                await distributed_manager.handle_peer_message(node_id, message_data)
                
        except WebSocketDisconnect:
            logger.info(f"Peer WebSocket disconnected: {node_id}")
            # Clean up connection
            if node_id in distributed_manager.peer_connections:
                del distributed_manager.peer_connections[node_id]
        
    except Exception as e:
        logger.error(f"Peer WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )
