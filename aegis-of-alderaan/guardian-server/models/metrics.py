"""
Aegis of Alderaan - Metrics Models
Pydantic models for system metrics and monitoring data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CPUMetrics(BaseModel):
    """CPU metrics model"""
    percent: float = Field(..., description="CPU usage percentage")
    count: int = Field(..., description="Number of CPU cores")
    load_avg: List[float] = Field(default=[], description="Load averages")

class MemoryMetrics(BaseModel):
    """Memory metrics model"""
    total: int = Field(..., description="Total memory in bytes")
    available: int = Field(..., description="Available memory in bytes")
    percent: float = Field(..., description="Memory usage percentage")
    used: int = Field(..., description="Used memory in bytes")
    free: int = Field(..., description="Free memory in bytes")

class DiskMetrics(BaseModel):
    """Disk metrics model"""
    total: int = Field(..., description="Total disk space in bytes")
    used: int = Field(..., description="Used disk space in bytes")
    free: int = Field(..., description="Free disk space in bytes")
    percent: float = Field(..., description="Disk usage percentage")

class NetworkMetrics(BaseModel):
    """Network metrics model"""
    bytes_sent: int = Field(..., description="Bytes sent")
    bytes_recv: int = Field(..., description="Bytes received")
    packets_sent: int = Field(..., description="Packets sent")
    packets_recv: int = Field(..., description="Packets received")
    speed_mbps: float = Field(..., description="Network speed in Mbps")

class SystemMetrics(BaseModel):
    """Complete system metrics model"""
    agent_id: str = Field(..., description="Agent identifier")
    hostname: str = Field(..., description="System hostname")
    timestamp: str = Field(..., description="Metrics timestamp")
    cpu: CPUMetrics = Field(..., description="CPU metrics")
    memory: MemoryMetrics = Field(..., description="Memory metrics")
    disk: DiskMetrics = Field(..., description="Disk metrics")
    network: NetworkMetrics = Field(..., description="Network metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "laptop-001-agent",
                "hostname": "laptop-001",
                "timestamp": "2025-07-17T10:30:00Z",
                "cpu": {
                    "percent": 45.2,
                    "count": 8,
                    "load_avg": [1.2, 1.5, 1.8]
                },
                "memory": {
                    "total": 17179869184,
                    "available": 8589934592,
                    "percent": 50.0,
                    "used": 8589934592,
                    "free": 8589934592
                },
                "disk": {
                    "total": 1000000000000,
                    "used": 500000000000,
                    "free": 500000000000,
                    "percent": 50.0
                },
                "network": {
                    "bytes_sent": 1024000,
                    "bytes_recv": 2048000,
                    "packets_sent": 1000,
                    "packets_recv": 1500,
                    "speed_mbps": 25.5
                }
            }
        }

# Alias for backward compatibility
MetricsModel = SystemMetrics

class AnomalyModel(BaseModel):
    """Anomaly detection result model"""
    agent_id: str = Field(..., description="Agent identifier")
    type: str = Field(..., description="Anomaly type")
    severity: str = Field(..., description="Anomaly severity")
    description: str = Field(..., description="Anomaly description")
    timestamp: str = Field(..., description="Detection timestamp")
    current_value: Optional[float] = Field(None, description="Current metric value")
    threshold: Optional[float] = Field(None, description="Threshold value")
    context: Dict[str, Any] = Field(default={}, description="Additional context")

class MetricsSummary(BaseModel):
    """Metrics summary for dashboard"""
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Number of active agents")
    avg_cpu_usage: float = Field(..., description="Average CPU usage across all agents")
    avg_memory_usage: float = Field(..., description="Average memory usage")
    avg_disk_usage: float = Field(..., description="Average disk usage")
    total_anomalies: int = Field(..., description="Total anomalies detected")
    critical_alerts: int = Field(..., description="Number of critical alerts")
