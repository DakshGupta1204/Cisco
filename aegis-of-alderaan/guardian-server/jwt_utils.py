"""
Aegis of Alderaan - JWT Utilities
JWT token management for Guardian server
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

class JWTManager:
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256'):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET', 'aegis-guardian-secret-key')
        self.algorithm = algorithm
        self.logger = logging.getLogger(__name__)
        
    def generate_token(self, payload: Dict, expires_in: int = 3600) -> str:
        """Generate JWT token for agents"""
        try:
            now = datetime.utcnow()
            exp_time = now + timedelta(seconds=expires_in)
            
            token_payload = {
                **payload,
                'iat': int(now.timestamp()),
                'exp': int(exp_time.timestamp()),
                'iss': 'aegis-guardian',
                'type': 'agent_auth'
            }
            
            self.logger.debug(f"Generating token with expiry: {exp_time} (in {expires_in} seconds)")
            
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            self.logger.debug(f"Generated token for agent: {payload.get('agent_id', 'unknown')}")
            
            return token
            
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token"""
        try:
            # Decode with detailed error handling
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get('type') != 'agent_auth':
                self.logger.warning("Invalid token type")
                return None
            
            # Log token details for debugging
            now = datetime.utcnow()
            exp_timestamp = payload.get('exp', 0)
            exp_time = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            
            self.logger.debug(f"Token validation - Current time: {now}, Expires: {exp_time}")
            self.logger.debug(f"Token validated for agent: {payload.get('agent_id', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            # Get more details about the expiration
            try:
                # Decode without verification to see the claims
                unverified = jwt.decode(token, options={"verify_signature": False})
                exp_time = datetime.fromtimestamp(unverified.get('exp', 0))
                now = datetime.utcnow()
                self.logger.warning(f"Token has expired - Expired at: {exp_time}, Current time: {now}")
            except:
                self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return None
    
    def refresh_token(self, token: str, expires_in: int = 3600) -> Optional[str]:
        """Refresh an existing token"""
        payload = self.validate_token(token)
        if not payload:
            return None
        
        # Remove JWT claims to avoid conflicts
        for claim in ['iat', 'exp', 'iss', 'type']:
            payload.pop(claim, None)
        
        return self.generate_token(payload, expires_in)
    
    def extract_agent_info(self, token: str) -> Optional[Dict]:
        """Extract agent information from token"""
        payload = self.validate_token(token)
        if not payload:
            return None
        
        return {
            'agent_id': payload.get('agent_id'),
            'hostname': payload.get('hostname'),
            'role': payload.get('role'),
            'authenticated_at': payload.get('authenticated_at')
        }
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get('exp')
            
            if exp:
                exp_datetime = datetime.fromtimestamp(exp)
                return datetime.utcnow() > exp_datetime
            
            return True
            
        except Exception:
            return True
    
    def decode_token_unsafe(self, token: str) -> Optional[Dict]:
        """Decode token without signature verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            self.logger.error(f"Failed to decode token: {e}")
            return None
