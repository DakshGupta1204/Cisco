#!/usr/bin/env python3
"""
Aegis Multi-Laptop Deployment Script
Sets up Guardian + 2 Peer agents with JWT authentication
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def get_local_ip():
    """Get local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def check_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
        return True
    except:
        return False

def setup_guardian_laptop():
    """Setup for Guardian laptop (Laptop 1)"""
    print("🛡️ Setting up Guardian Laptop...")
    
    local_ip = get_local_ip()
    print(f"📍 Local IP: {local_ip}")
    
    # Create .env file for Guardian
    env_content = f"""# Guardian Server Environment
GUARDIAN_SERVER_URL=ws://{local_ip}:3001/ws/agent
GUARDIAN_HTTP_URL=http://{local_ip}:3001
JWT_SECRET_KEY=aegis-distributed-secret-2024
HOSTNAME={socket.gethostname()}

# Database Configuration (Optional)
MONGODB_URI=mongodb://localhost:27017/aegis
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# AI Configuration (Optional)
GEMINI_API_KEY=your-gemini-api-key-here
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Environment configured")
    print(f"🌐 Guardian will be accessible at: http://{local_ip}:3001")
    print(f"🖥️ Admin Panel: http://{local_ip}:3000/admin")
    print("\n📋 Instructions for other laptops:")
    print(f"   - Set GUARDIAN_SERVER_URL=ws://{local_ip}:3001/ws/agent")
    print(f"   - Set GUARDIAN_HTTP_URL=http://{local_ip}:3001")
    print(f"   - Set JWT_SECRET_KEY=aegis-distributed-secret-2024")
    
    return local_ip

def setup_peer_laptop(guardian_ip, agent_id="agent-002"):
    """Setup for Peer laptop (Laptop 2 & 3)"""
    print(f"🤝 Setting up Peer Laptop - {agent_id}...")
    
    # Create .env file for Agent
    env_content = f"""# Peer Agent Environment
GUARDIAN_SERVER_URL=ws://{guardian_ip}:3001/ws/agent
GUARDIAN_HTTP_URL=http://{guardian_ip}:3001
JWT_SECRET_KEY=aegis-distributed-secret-2024
HOSTNAME={socket.gethostname()}
AGENT_ID={agent_id}
"""
    
    with open("agent/.env", "w") as f:
        f.write(env_content)
    
    # Update agent config
    agent_config = f"""# Agent Configuration for Aegis of Alderaan
agent:
  id: "{agent_id}"
  hostname: "{socket.gethostname()}"
  role: "peer"
  port: 8080

guardian:
  server_url: "ws://{guardian_ip}:3001/ws/agent"
  http_url: "http://{guardian_ip}:3001"
  reconnect_interval: 5
  heartbeat_interval: 30
  ssl_verify: false
  connection_timeout: 30

metrics:
  collection_interval: 10
  batch_size: 10
  retention_hours: 24

monitoring:
  cpu_threshold: 80
  memory_threshold: 85
  disk_threshold: 90
  network_threshold: 100

security:
  jwt_secret: "aegis-distributed-secret-2024"
  jwt_expiry: 3600

failover:
  mirror_agent_url: null
  health_check_interval: 15
  failover_timeout: 30

logging:
  level: "INFO"
  file: "agent.log"
"""
    
    with open("agent/config.yaml", "w") as f:
        f.write(agent_config)
    
    print("✅ Peer configuration updated")
    print(f"🔗 Will connect to Guardian at: {guardian_ip}:3001")
    
    return True

def start_guardian():
    """Start Guardian server and frontend"""
    print("\n🚀 Starting Guardian Server...")
    
    if not check_port_available(3001):
        print("❌ Port 3001 is already in use!")
        return False
    
    # Start Guardian server
    print("Starting Guardian server on port 3001...")
    guardian_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", "--port", "3001", "--reload"
    ], cwd="guardian-server")
    
    time.sleep(3)
    
    # Start frontend
    if check_port_available(3000):
        print("Starting Frontend on port 3000...")
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend")
        
        print("✅ Guardian system started!")
        print("🖥️ Admin Panel: http://localhost:3000/admin")
        print("📡 API Server: http://localhost:3001")
        print("📋 API Docs: http://localhost:3001/docs")
        
        return True
    else:
        print("⚠️ Port 3000 is busy, frontend not started")
        return False

def start_peer_agent():
    """Start peer agent"""
    print("\n🚀 Starting Peer Agent...")
    
    # Start agent
    agent_process = subprocess.Popen([
        sys.executable, "start_agent.py"
    ], cwd="agent")
    
    print("✅ Peer agent started!")
    print("🔗 Connecting to Guardian server...")
    
    return True

def main():
    """Main deployment function"""
    print("🛡️ Aegis of Alderaan - Multi-Laptop Deployment")
    print("=" * 50)
    
    # Check what type of setup to run
    if len(sys.argv) > 1:
        setup_type = sys.argv[1].lower()
    else:
        print("Select setup type:")
        print("1. Guardian (Laptop 1 - Admin/Control Center)")
        print("2. Peer (Laptop 2 & 3 - Agents)")
        choice = input("Enter choice (1 or 2): ").strip()
        setup_type = "guardian" if choice == "1" else "peer"
    
    if setup_type == "guardian":
        # Guardian laptop setup
        guardian_ip = setup_guardian_laptop()
        
        input("\n⏳ Press Enter to start Guardian server...")
        start_guardian()
        
        print("\n🎉 Guardian laptop is ready!")
        print("📝 Share this info with peer laptops:")
        print(f"   Guardian IP: {guardian_ip}")
        print("   JWT Secret: aegis-distributed-secret-2024")
        
        try:
            input("\nPress Enter to stop servers...")
        except KeyboardInterrupt:
            pass
        
    elif setup_type == "peer":
        # Peer laptop setup
        guardian_ip = input("Enter Guardian laptop IP address: ").strip()
        if not guardian_ip:
            guardian_ip = "192.168.1.100"  # Default
        
        agent_id = input("Enter agent ID (agent-002, agent-003, etc.): ").strip()
        if not agent_id:
            agent_id = f"agent-{int(time.time()) % 1000:03d}"
        
        setup_peer_laptop(guardian_ip, agent_id)
        
        input("\n⏳ Press Enter to start peer agent...")
        start_peer_agent()
        
        print(f"\n🎉 Peer laptop ({agent_id}) is ready!")
        print(f"🔗 Connected to Guardian at {guardian_ip}:3001")
        
        try:
            input("\nPress Enter to stop agent...")
        except KeyboardInterrupt:
            pass
    
    else:
        print("❌ Invalid setup type. Use 'guardian' or 'peer'")
        sys.exit(1)

if __name__ == "__main__":
    main()
