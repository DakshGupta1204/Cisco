#!/usr/bin/env python3
"""
Aegis of Alderaan Agent - Startup Script
Quick start script for the agent
"""

import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
    else:
        print("requirements.txt not found")

def main():
    """Main startup function"""
    print("=" * 50)
    print("🛡️  Aegis of Alderaan - Agent Startup")
    print("=" * 50)
    
    # Check if dependencies need to be installed
    try:
        import psutil
        import aiohttp
        import websockets
        import jwt
        import numpy
        import yaml
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing dependencies...")
        install_dependencies()
    
    # Start the agent
    try:
        from main import main as agent_main
        import asyncio
        
        print("🚀 Starting Aegis Agent...")
        asyncio.run(agent_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
