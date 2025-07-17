"""
Aegis of Alderaan - Peer Server
Peer node that connects to the Guardian server
"""

import os
import asyncio
import logging
import json
import socket
import uuid
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psutil
import uvicorn
import aiohttp
from distributed_manager import DistributedManager, PeerInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for peer
app = FastAPI(
    title="Aegis Peer Node",
    description="Distributed peer node for Aegis network",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize distributed manager as peer
distributed_manager = DistributedManager(node_role="peer")

# Connection state
connection_state = {
    "connected": False,
    "guardian_host": None,
    "guardian_port": None,
    "node_id": distributed_manager.my_node_id,
    "last_heartbeat": None,
    "health_status": "healthy"
}

# WebSocket connections
websocket_connections = []

@app.websocket("/ws/peer")
async def peer_websocket(websocket: WebSocket):
    """WebSocket endpoint for peer dashboard"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "connection_status",
            "status": connection_state
        }))
        
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)
            
            # Send metrics update
            metrics = get_system_metrics()
            await websocket.send_text(json.dumps({
                "type": "metrics_update", 
                "metrics": metrics
            }))
            
    except WebSocketDisconnect:
        logger.info("Peer WebSocket disconnected")
        websocket_connections.remove(websocket)

async def broadcast_to_websockets(message: Dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_text(json.dumps(message))
        except:
            disconnected.append(ws)
    
    # Remove disconnected websockets
    for ws in disconnected:
        websocket_connections.remove(ws)

def get_system_metrics() -> Dict:
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "network_io": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_io": {
                "bytes_sent": 0,
                "bytes_recv": 0
            }
        }

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

@app.get("/peer/status")
async def get_peer_status():
    """Get peer node status"""
    metrics = get_system_metrics()
    return {
        "connection": connection_state,
        "metrics": metrics,
        "hostname": socket.gethostname(),
        "ip_address": get_local_ip(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/peer/connect")
async def connect_to_guardian(request: Dict):
    """Connect this peer to a Guardian node"""
    guardian_host = request.get("guardian_host", "localhost")
    guardian_port = request.get("guardian_port", 3001)
    
    try:
        # Create peer info
        my_info = PeerInfo(
            node_id=distributed_manager.my_node_id,
            hostname=socket.gethostname(),
            ip_address=get_local_ip(),
            port=3002,  # This peer's port
            role="peer",
            capabilities=["metrics_collection", "self_healing", "mirror_support"],
            last_heartbeat=datetime.utcnow(),
            health_status="healthy"
        )
        
        # Connect to guardian
        success = await distributed_manager.connect_to_guardian(
            guardian_host, guardian_port, my_info
        )
        
        if success:
            connection_state.update({
                "connected": True,
                "guardian_host": guardian_host,
                "guardian_port": guardian_port,
                "last_heartbeat": datetime.utcnow().isoformat(),
                "health_status": "healthy"
            })
            
            # Start heartbeat task
            asyncio.create_task(heartbeat_task(guardian_host, guardian_port))
            
            # Broadcast status update
            await broadcast_to_websockets({
                "type": "connection_status",
                "status": connection_state
            })
            
            return {
                "success": True,
                "message": f"Connected to Guardian at {guardian_host}:{guardian_port}",
                "connection": connection_state
            }
        else:
            return {
                "success": False,
                "message": "Failed to connect to Guardian",
                "connection": connection_state
            }
            
    except Exception as e:
        logger.error(f"Error connecting to Guardian: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "connection": connection_state
        }

@app.post("/peer/disconnect")
async def disconnect_from_guardian():
    """Disconnect from Guardian node"""
    try:
        if connection_state["connected"]:
            # Update connection state
            connection_state.update({
                "connected": False,
                "guardian_host": None,
                "guardian_port": None,
                "last_heartbeat": None,
                "health_status": "disconnected"
            })
            
            # Broadcast status update
            await broadcast_to_websockets({
                "type": "connection_status",
                "status": connection_state
            })
            
            return {
                "success": True,
                "message": "Disconnected from Guardian",
                "connection": connection_state
            }
        else:
            return {
                "success": False,
                "message": "Not connected to any Guardian",
                "connection": connection_state
            }
            
    except Exception as e:
        logger.error(f"Error disconnecting from Guardian: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "connection": connection_state
        }

async def heartbeat_task(guardian_host: str, guardian_port: int):
    """Send periodic heartbeat to Guardian"""
    while connection_state["connected"]:
        try:
            metrics = get_system_metrics()
            
            async with aiohttp.ClientSession() as session:
                heartbeat_data = {
                    "node_id": distributed_manager.my_node_id,
                    "hostname": socket.gethostname(),
                    "health_status": "healthy",
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with session.post(
                    f"http://{guardian_host}:{guardian_port}/distributed/peers/heartbeat",
                    json=heartbeat_data
                ) as response:
                    if response.status == 200:
                        connection_state["last_heartbeat"] = datetime.utcnow().isoformat()
                        connection_state["health_status"] = "healthy"
                    else:
                        logger.warning(f"Heartbeat failed with status: {response.status}")
                        connection_state["health_status"] = "warning"
            
            # Broadcast metrics update
            await broadcast_to_websockets({
                "type": "metrics_update",
                "metrics": metrics
            })
            
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            connection_state["health_status"] = "error"
            await asyncio.sleep(10)  # Shorter interval on error

@app.get("/peer/metrics")
async def get_metrics():
    """Get current system metrics"""
    return {
        "node_id": distributed_manager.my_node_id,
        "metrics": get_system_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/peer/healing/execute")
async def execute_healing_strategy(request: Dict):
    """Execute a healing strategy received from Guardian"""
    try:
        strategy = request.get("strategy", {})
        logger.info(f"Executing healing strategy: {strategy.get('strategy_id', 'unknown')}")
        
        # Simulate healing execution
        phases = strategy.get("phases", [])
        for phase in phases:
            logger.info(f"Executing phase: {phase.get('phase', 'unknown')}")
            # Simulate phase execution time
            await asyncio.sleep(2)
        
        return {
            "success": True,
            "message": "Healing strategy executed successfully",
            "strategy_id": strategy.get("strategy_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing healing strategy: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node_id": distributed_manager.my_node_id,
        "role": "peer",
        "connected_to_guardian": connection_state["connected"],
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # Start peer server on port 3002
    uvicorn.run(
        "peer_server:app",
        host="0.0.0.0",
        port=3002,
        reload=True,
        log_level="info"
    )
