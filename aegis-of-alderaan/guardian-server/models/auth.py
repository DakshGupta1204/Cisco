"""
Aegis of Alderaan - Authentication Models
Pydantic models for authentication and authorization
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AuthModel(BaseModel):
    """Agent authentication model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    hostname: str = Field(..., description="Agent hostname")
    role: str = Field(default="endpoint", description="Agent role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "laptop-001-agent",
                "hostname": "laptop-001",
                "role": "endpoint"
            }
        }

class TokenResponse(BaseModel):
    """JWT token response model"""
    token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    agent_id: str = Field(..., description="Authenticated agent ID")

class TokenPayload(BaseModel):
    """JWT token payload model"""
    agent_id: str
    hostname: str
    role: str
    authenticated_at: str
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None
    iss: Optional[str] = None
