#!/usr/bin/env python3
"""
Test JWT token generation fix
"""

import sys
import os
from datetime import datetime

# Add guardian-server to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'guardian-server'))

from jwt_utils import JWTManager

def test_jwt_generation():
    print("Testing JWT token generation...")
    
    jwt_manager = JWTManager()
    
    # Test payload that caused the error
    test_payload = {
        "agent_id": "test-agent",
        "hostname": "test-host",
        "role": "endpoint"
    }
    
    try:
        token = jwt_manager.generate_token(test_payload)
        print(f"✅ JWT generation successful!")
        print(f"Token: {token[:50]}...")
        
        # Test validation
        decoded = jwt_manager.validate_token(token)
        if decoded:
            print(f"✅ JWT validation successful!")
            print(f"Decoded agent_id: {decoded.get('agent_id')}")
        else:
            print("❌ JWT validation failed")
            
    except Exception as e:
        print(f"❌ JWT generation failed: {e}")

if __name__ == "__main__":
    test_jwt_generation()
