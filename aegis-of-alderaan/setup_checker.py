#!/usr/bin/env python3
"""
Aegis of Alderaan - Pre-simulation Setup Checker
"""

import os
import sys
from pathlib import Path

def check_setup():
    print("🔍 Checking Aegis of Alderaan Setup...")
    print("=" * 50)
    
    # Check project structure
    project_root = Path(r"c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan")
    
    required_files = [
        ".env",
        "guardian-server/app.py",
        "guardian-server/start_server.py",
        "guardian-server/requirements.txt",
        "agent/main.py",
        "agent/start_agent.py",
        "agent/config.yaml",
        "agent/requirements.txt"
    ]
    
    print("📁 Project Structure:")
    for file_path in required_files:
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {status} {file_path}")
    
    # Check .env file contents
    env_file = project_root / ".env"
    if env_file.exists():
        print("\n🔧 Environment Configuration:")
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = [
            "MONGODB_URI",
            "NEO4J_URI", 
            "NEO4J_USER",
            "NEO4J_PASSWORD",
            "JWT_SECRET_KEY"
        ]
        
        for var in required_vars:
            if var in content and not content.split(f"{var}=")[1].split('\n')[0].strip().startswith('your-'):
                print(f"  ✅ {var} configured")
            else:
                print(f"  ❌ {var} needs configuration")
    
    # Check Python dependencies
    print("\n📦 Python Dependencies:")
    try:
        import fastapi
        print("  ✅ FastAPI available")
    except ImportError:
        print("  ❌ FastAPI missing - run: pip install fastapi")
    
    try:
        import uvicorn
        print("  ✅ Uvicorn available")
    except ImportError:
        print("  ❌ Uvicorn missing - run: pip install uvicorn")
    
    try:
        import motor
        print("  ✅ Motor (MongoDB) available")
    except ImportError:
        print("  ❌ Motor missing - run: pip install motor")
    
    try:
        import neo4j
        print("  ✅ Neo4j driver available")
    except ImportError:
        print("  ❌ Neo4j driver missing - run: pip install neo4j")
    
    try:
        import websockets
        print("  ✅ WebSockets available")
    except ImportError:
        print("  ❌ WebSockets missing - run: pip install websockets")
    
    try:
        import psutil
        print("  ✅ psutil available")
    except ImportError:
        print("  ❌ psutil missing - run: pip install psutil")
    
    print("\n" + "=" * 50)
    print("Setup check complete!")

if __name__ == "__main__":
    check_setup()
