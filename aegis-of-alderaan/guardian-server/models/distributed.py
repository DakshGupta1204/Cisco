from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class PeerMetricsModel(BaseModel):
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    active_connections: int
    threats_detected: int

class PeerRegistrationModel(BaseModel):
    node_id: str
    hostname: str
    ip_address: str
    port: int
    jwt_token: str
    capabilities: List[str]
    system_metrics: Dict

class PeerMetricsPayload(BaseModel):
    metrics: PeerMetricsModel
