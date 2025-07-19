"""
Aegis of Alderaan - JWT Authentication
Secure token generation and validation for agent authentication
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

class JWTAuth:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.logger = logging.getLogger(__name__)
    
    def generate_token(self, payload: Dict, expires_in: int = 3600) -> str:
        """Generate JWT token with expiration"""
        try:
            # Add standard claims
            now = datetime.utcnow()
            token_payload = {
                **payload,
                'iat': now,  # Issued at
                'exp': now + timedelta(seconds=expires_in),  # Expiration
                'iss': 'aegis-agent',  # Issuer
            }
            
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            self.logger.debug(f"Generated token for: {payload.get('agent_id', 'unknown')}")
            
            return token
            
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            self.logger.debug(f"Token validated for: {payload.get('agent_id', 'unknown')}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
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
        
        # Remove standard claims to avoid conflicts
        for claim in ['iat', 'exp', 'iss']:
            payload.pop(claim, None)
        
        return self.generate_token(payload, expires_in)
    
    def extract_agent_id(self, token: str) -> Optional[str]:
        """Extract agent ID from token"""
        payload = self.validate_token(token)
        return payload.get('agent_id') if payload else None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without validating signature"""
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get('exp')
            
            if exp:
                exp_datetime = datetime.fromtimestamp(exp)
                return datetime.utcnow() > exp_datetime
            
            return True  # No expiration claim means expired
            
        except Exception:
            return True  # Any error means treat as expired
