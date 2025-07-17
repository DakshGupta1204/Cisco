#!/usr/bin/env python3
"""
Aegis of Alderaan - Quick Launch Script
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def launch_guardian_server():
    """Launch the Guardian Server"""
    print("🛡️  Starting Guardian Server...")
    
    guardian_dir = Path(r"c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\guardian-server")
    
    if not guardian_dir.exists():
        print("❌ Guardian server directory not found!")
        return None
    
    try:
        # Change to guardian server directory and start
        process = subprocess.Popen([
            sys.executable, "start_server.py"
        ], cwd=guardian_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print(f"✅ Guardian Server started (PID: {process.pid})")
        print("🌐 Server will be available at: http://localhost:3001")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Guardian Server: {e}")
        return None

def launch_agent():
    """Launch an Agent"""
    print("🤖 Starting Agent...")
    
    agent_dir = Path(r"c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent")
    
    if not agent_dir.exists():
        print("❌ Agent directory not found!")
        return None
    
    try:
        # Change to agent directory and start
        process = subprocess.Popen([
            sys.executable, "start_agent.py"
        ], cwd=agent_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print(f"✅ Agent started (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Agent: {e}")
        return None

def main():
    print("=" * 60)
    print("🛡️  Aegis of Alderaan - Quick Launcher")
    print("=" * 60)
    
    print("\nWhat would you like to do?")
    print("1. Start Guardian Server only")
    print("2. Start Agent only")  
    print("3. Start Guardian Server + Agent")
    print("4. Start Guardian Server + 2 Agents")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        launch_guardian_server()
        
    elif choice == "2":
        launch_agent()
        
    elif choice == "3":
        guardian_process = launch_guardian_server()
        if guardian_process:
            print("\n⏳ Waiting 10 seconds for Guardian Server to start...")
            time.sleep(10)
            launch_agent()
            
    elif choice == "4":
        guardian_process = launch_guardian_server()
        if guardian_process:
            print("\n⏳ Waiting 10 seconds for Guardian Server to start...")
            time.sleep(10)
            print("\n🤖 Starting Agent 1...")
            launch_agent()
            time.sleep(2)
            print("\n🤖 Starting Agent 2...")
            # Set different agent ID for second agent
            os.environ["AGENT_ID"] = f"{os.getenv('HOSTNAME', 'UNKNOWN')}-agent-2"
            launch_agent()
            
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice!")
        
    print("\n" + "=" * 60)
    print("✅ Launch complete!")
    print("📖 Check the new console windows for detailed logs")
    print("🌐 Guardian Server: http://localhost:3001")
    print("📚 API Docs: http://localhost:3001/docs")
    print("🛑 Press Ctrl+C in each console to stop services")
    print("=" * 60)

if __name__ == "__main__":
    main()
