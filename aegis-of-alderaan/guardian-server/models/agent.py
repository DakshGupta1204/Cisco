"""
Aegis of Alderaan - Agent Models
Pydantic models for agent data structures
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AgentModel(BaseModel):
    """Agent registration and status model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    hostname: str = Field(..., description="Agent hostname")
    role: str = Field(default="endpoint", description="Agent role")
    status: str = Field(default="active", description="Agent status")
    capabilities: List[str] = Field(default=[], description="Agent capabilities")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "laptop-001-agent",
                "hostname": "laptop-001",
                "role": "endpoint",
                "status": "active",
                "capabilities": ["metrics_collection", "anomaly_detection"],
                "last_heartbeat": "2025-07-17T10:30:00Z"
            }
        }

class AgentCommand(BaseModel):
    """Command to send to agent"""
    command: str = Field(..., description="Command to execute")
    parameters: Dict[str, Any] = Field(default={}, description="Command parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "command": "restart_service",
                "parameters": {
                    "service_name": "network",
                    "timeout": 30
                }
            }
        }

class AgentStatus(BaseModel):
    """Agent status response"""
    agent_id: str
    status: str
    timestamp: datetime
    health_metrics: Optional[Dict[str, Any]] = None

class AgentRegistration(BaseModel):
    """Agent registration data"""
    agent_id: str
    hostname: str
    role: str
    capabilities: List[str]
    system_info: Dict[str, Any]
