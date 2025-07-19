#!/usr/bin/env python3
"""
Quick startup script for Aegis AI Guardian Server
Use this to start the server for Postman testing
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to guardian-server directory
    guardian_dir = Path(__file__).parent / "guardian-server"
    
    if not guardian_dir.exists():
        print("❌ Guardian server directory not found!")
        sys.exit(1)
    
    os.chdir(guardian_dir)
    
    print("🚀 Starting Aegis AI Guardian Server...")
    print("📍 Server will be available at: http://localhost:3001")
    print("📚 API Documentation: http://localhost:3001/docs")
    print("🧪 Ready for Postman testing!")
    print("-" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "3001", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
