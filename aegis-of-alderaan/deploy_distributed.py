#!/usr/bin/env python3
"""
Aegis of Alderaan - Distributed System Deployment
Sets up multi-laptop distributed system with JWT authentication
"""

import os
import sys
import socket
import uuid
import json
import subprocess
import platform
from pathlib import Path
import shutil

class DistributedDeployment:
    def __init__(self):
        self.system_info = self._get_system_info()
        self.deployment_config = {}
        
    def _get_system_info(self):
        """Get current system information"""
        return {
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version()
        }
    
    def setup_guardian_node(self):
        """Setup this computer as the Guardian (central coordinator)"""
        print("🛡️  Setting up Guardian Node...")
        
        # Create environment configuration
        env_config = {
            "NODE_TYPE": "guardian",
            "NODE_ID": f"guardian-{uuid.uuid4().hex[:8]}",
            "JWT_SECRET_KEY": self._generate_jwt_secret(),
            "GUARDIAN_PORT": "3001",
            "FRONTEND_PORT": "3000",
            "WEBSOCKET_ENABLED": "true"
        }
        
        # Update .env file
        self._update_env_file(env_config)
        
        # Install dependencies
        self._install_dependencies()
        
        # Setup frontend for admin panel
        self._setup_frontend()
        
        # Create startup scripts
        self._create_guardian_startup_scripts()
        
        print("✅ Guardian node setup complete!")
        print(f"📍 Guardian IP: {self.system_info['ip_address']}")
        print(f"🎛️  Admin Panel: http://{self.system_info['ip_address']}:3000/admin")
        print(f"🔗 Guardian API: http://{self.system_info['ip_address']}:3001")
        
        return {
            "node_type": "guardian",
            "node_id": env_config["NODE_ID"],
            "ip_address": self.system_info["ip_address"],
            "admin_url": f"http://{self.system_info['ip_address']}:3000/admin",
            "api_url": f"http://{self.system_info['ip_address']}:3001"
        }
    
    def setup_peer_node(self, guardian_ip=None):
        """Setup this computer as a Peer node"""
        print("💻 Setting up Peer Node...")
        
        # Get guardian IP if not provided
        if not guardian_ip:
            guardian_ip = input("Enter Guardian IP address: ").strip()
        
        # Create environment configuration
        env_config = {
            "NODE_TYPE": "peer",
            "NODE_ID": f"peer-{uuid.uuid4().hex[:8]}",
            "PEER_PORT": "3002",
            "GUARDIAN_IP": guardian_ip,
            "GUARDIAN_PORT": "3001",
            "FRONTEND_PORT": "3000",
            "WEBSOCKET_ENABLED": "true"
        }
        
        # Update .env file
        self._update_env_file(env_config)
        
        # Install dependencies
        self._install_dependencies()
        
        # Setup frontend for peer panel
        self._setup_frontend()
        
        # Create startup scripts
        self._create_peer_startup_scripts()
        
        print("✅ Peer node setup complete!")
        print(f"📍 Peer IP: {self.system_info['ip_address']}")
        print(f"🎛️  Peer Panel: http://{self.system_info['ip_address']}:3000/peer")
        print(f"🔗 Guardian: http://{guardian_ip}:3001")
        print("⚠️  You'll need a JWT token from the Guardian to connect")
        
        return {
            "node_type": "peer",
            "node_id": env_config["NODE_ID"],
            "ip_address": self.system_info["ip_address"],
            "peer_url": f"http://{self.system_info['ip_address']}:3000/peer",
            "guardian_ip": guardian_ip
        }
    
    def _generate_jwt_secret(self):
        """Generate secure JWT secret key"""
        return f"aegis-{uuid.uuid4().hex}"
    
    def _update_env_file(self, config):
        """Update .env file with configuration"""
        env_path = Path(".env")
        
        # Read existing .env if it exists
        existing_config = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing_config[key] = value
        
        # Merge configurations
        existing_config.update(config)
        
        # Write updated .env
        with open(env_path, 'w') as f:
            f.write("# Aegis of Alderaan - Distributed System Configuration\n")
            f.write(f"# Generated on {self.system_info['hostname']} at {socket.gethostname()}\n\n")
            
            for key, value in existing_config.items():
                f.write(f"{key}={value}\n")
        
        print(f"📝 Updated .env file with {len(config)} new settings")
    
    def _install_dependencies(self):
        """Install required Python packages"""
        print("📦 Installing Python dependencies...")
        
        requirements = [
            "fastapi",
            "uvicorn[standard]",
            "websockets",
            "python-jose[cryptography]",
            "python-multipart",
            "python-dotenv",
            "psutil",
            "requests",
            "motor",  # MongoDB async driver
            "neo4j",  # Neo4j driver
            "google-generativeai",  # Gemini AI
            "asyncio-mqtt"
        ]
        
        for package in requirements:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install {package}")
    
    def _setup_frontend(self):
        """Setup Next.js frontend"""
        print("🎨 Setting up frontend...")
        
        frontend_path = Path("frontend")
        if frontend_path.exists():
            os.chdir(frontend_path)
            
            # Install npm dependencies
            try:
                subprocess.check_call(["npm", "install"])
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to install frontend dependencies")
            except FileNotFoundError:
                print("⚠️  npm not found. Please install Node.js")
            
            os.chdir("..")
        else:
            print("⚠️  Frontend directory not found")
    
    def _create_guardian_startup_scripts(self):
        """Create startup scripts for Guardian node"""
        
        # Windows batch script
        batch_script = """@echo off
echo Starting Aegis Guardian Node...
echo.

echo Starting Guardian Server...
cd guardian-server
start "Guardian Server" python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload
cd ..

timeout /t 3 /nobreak > nul

echo Starting Admin Frontend...
cd frontend
start "Admin Frontend" npm run dev
cd ..

echo.
echo ✅ Guardian Node started!
echo 🎛️  Admin Panel: http://localhost:3000/admin
echo 🔗 Guardian API: http://localhost:3001
echo.
pause
"""
        
        # PowerShell script
        ps_script = """# Aegis Guardian Node Startup
Write-Host "🛡️  Starting Aegis Guardian Node..." -ForegroundColor Green

# Start Guardian Server
Write-Host "Starting Guardian Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd guardian-server; python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload"

# Wait a bit
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Admin Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "✅ Guardian Node started!" -ForegroundColor Green
Write-Host "🎛️  Admin Panel: http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host "🔗 Guardian API: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"""
        
        # Bash script for Linux/Mac
        bash_script = """#!/bin/bash
echo "🛡️  Starting Aegis Guardian Node..."
echo

echo "Starting Guardian Server..."
cd guardian-server
python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload &
GUARDIAN_PID=$!
cd ..

sleep 3

echo "Starting Admin Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "✅ Guardian Node started!"
echo "🎛️  Admin Panel: http://localhost:3000/admin"
echo "🔗 Guardian API: http://localhost:3001"
echo
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'kill $GUARDIAN_PID $FRONTEND_PID' INT
wait
"""
        
        # Write scripts
        with open("start_guardian.bat", "w") as f:
            f.write(batch_script)
        
        with open("start_guardian.ps1", "w") as f:
            f.write(ps_script)
        
        with open("start_guardian.sh", "w") as f:
            f.write(bash_script)
        os.chmod("start_guardian.sh", 0o755)
        
        print("📄 Created startup scripts: start_guardian.bat, start_guardian.ps1, start_guardian.sh")
    
    def _create_peer_startup_scripts(self):
        """Create startup scripts for Peer node"""
        
        # Windows batch script
        batch_script = """@echo off
echo Starting Aegis Peer Node...
echo.

echo Starting Peer Server...
cd guardian-server
start "Peer Server" python -m uvicorn app:app --host 0.0.0.0 --port 3002 --reload
cd ..

timeout /t 3 /nobreak > nul

echo Starting Peer Frontend...
cd frontend
start "Peer Frontend" npm run dev
cd ..

echo.
echo ✅ Peer Node started!
echo 🎛️  Peer Panel: http://localhost:3000/peer
echo 🔗 Peer API: http://localhost:3002
echo.
pause
"""
        
        # PowerShell script
        ps_script = """# Aegis Peer Node Startup
Write-Host "💻 Starting Aegis Peer Node..." -ForegroundColor Green

# Start Peer Server
Write-Host "Starting Peer Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd guardian-server; python -m uvicorn app:app --host 0.0.0.0 --port 3002 --reload"

# Wait a bit
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Peer Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "✅ Peer Node started!" -ForegroundColor Green
Write-Host "🎛️  Peer Panel: http://localhost:3000/peer" -ForegroundColor Cyan
Write-Host "🔗 Peer API: http://localhost:3002" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"""
        
        # Bash script
        bash_script = """#!/bin/bash
echo "💻 Starting Aegis Peer Node..."
echo

echo "Starting Peer Server..."
cd guardian-server
python -m uvicorn app:app --host 0.0.0.0 --port 3002 --reload &
PEER_PID=$!
cd ..

sleep 3

echo "Starting Peer Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "✅ Peer Node started!"
echo "🎛️  Peer Panel: http://localhost:3000/peer"
echo "🔗 Peer API: http://localhost:3002"
echo
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'kill $PEER_PID $FRONTEND_PID' INT
wait
"""
        
        # Write scripts
        with open("start_peer.bat", "w") as f:
            f.write(batch_script)
        
        with open("start_peer.ps1", "w") as f:
            f.write(ps_script)
        
        with open("start_peer.sh", "w") as f:
            f.write(bash_script)
        os.chmod("start_peer.sh", 0o755)
        
        print("📄 Created startup scripts: start_peer.bat, start_peer.ps1, start_peer.sh")
    
    def create_deployment_guide(self):
        """Create comprehensive deployment guide"""
        guide = f"""# 🛡️ Aegis of Alderaan - Multi-Laptop Deployment Guide

## 🎯 Overview
This guide helps you set up a distributed AI-powered network protection system across multiple computers using JWT authentication.

## 🖥️ System Requirements
- **Python 3.8+** installed on all computers
- **Node.js 16+** for the frontend interface
- **Network connectivity** between all computers
- **Windows, Linux, or macOS** support

## 🏗️ Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Computer 1    │    │   Computer 2    │    │   Computer 3    │
│   (Guardian)    │◄──►│    (Peer)      │◄──►│    (Peer)      │
│                 │    │                 │    │                 │
│ • AI Analysis   │    │ • Metrics      │    │ • Mirror Host  │
│ • Coordination  │    │ • Monitoring   │    │ • Load Balance │
│ • Admin Panel   │    │ • Peer Panel   │    │ • Peer Panel   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Setup

### 1. Guardian Computer (Computer 1)
```bash
# Run the deployment script
python deploy_distributed.py

# Choose option 1: Setup Guardian Node
# Follow the prompts

# Start the system
./start_guardian.bat    # Windows
./start_guardian.sh     # Linux/Mac
```

**Guardian URLs:**
- Admin Panel: http://[GUARDIAN_IP]:3000/admin
- API Server: http://[GUARDIAN_IP]:3001

### 2. Peer Computers (Computer 2 & 3)
```bash
# Run the deployment script
python deploy_distributed.py

# Choose option 2: Setup Peer Node
# Enter Guardian IP when prompted

# Start the system
./start_peer.bat        # Windows
./start_peer.sh         # Linux/Mac
```

**Peer URLs:**
- Peer Panel: http://[PEER_IP]:3000/peer
- API Server: http://[PEER_IP]:3002

## 🔐 JWT Authentication Flow

### 1. Generate Tokens (Guardian)
1. Open Guardian Admin Panel: http://[GUARDIAN_IP]:3000/admin
2. Go to "Add Peer" tab
3. Enter peer computer details (hostname, IP)
4. Click "Generate Peer Token"
5. Copy the JWT token

### 2. Connect Peers (Peer Computers)
1. Open Peer Panel: http://[PEER_IP]:3000/peer
2. Enter Guardian IP address
3. Paste the JWT token from Guardian
4. Click "Connect to Guardian"

## 🎛️ Admin Panel Features (Guardian)

### Overview Tab
- System health monitoring
- Connected node status
- Real-time metrics
- Network topology view

### Connected Nodes Tab
- List of all peer computers
- Individual peer metrics
- Connection status
- Capability management

### Add Peer Tab
- Generate JWT tokens for new peers
- Connection instructions
- Network configuration

### Monitoring Tab
- Broadcast controls
- Health check commands
- Network diagnostics
- Performance monitoring

## 💻 Peer Panel Features

### Connection Status
- Guardian connection health
- Authentication status
- Network quality metrics
- Auto-reconnection

### System Metrics
- Real-time CPU, Memory, Disk usage
- Network connection monitoring
- Automatic metrics reporting
- Performance visualization

### Quick Actions
- Manual metrics updates
- Connection diagnostics
- Network status checks

## 🔄 System Capabilities

### Guardian Node Capabilities
- **AI Analysis**: Gemini-powered health analysis
- **Mirror Coordination**: Intelligent mirror management
- **Attack Simulation**: Security testing
- **Central Management**: Distributed system coordination
- **Network Topology**: Graph database relationships

### Peer Node Capabilities
- **Metrics Collection**: Real-time system monitoring
- **Health Monitoring**: Local health assessment
- **Mirror Hosting**: Backup service hosting
- **Load Balancing**: Distributed processing
- **Peer Communication**: Direct peer-to-peer messaging

## 🛡️ Security Features

### JWT Authentication
- Unique node identification
- Secure token-based authentication
- Long-lived tokens (24 hours)
- Automatic token validation

### Network Security
- WebSocket secure connections
- IP-based access control
- Connection quality monitoring
- Automatic failure detection

## 🔧 Advanced Configuration

### Environment Variables (.env)
```bash
# Guardian Configuration
NODE_TYPE=guardian
NODE_ID=guardian-12345678
JWT_SECRET_KEY=aegis-secret-key
GUARDIAN_PORT=3001
FRONTEND_PORT=3000

# Peer Configuration
NODE_TYPE=peer
NODE_ID=peer-87654321
PEER_PORT=3002
GUARDIAN_IP=192.168.1.10
GUARDIAN_PORT=3001
```

### Custom Capabilities
Modify node capabilities in the deployment script:
- `metrics_collection`
- `health_monitoring`
- `mirror_hosting`
- `load_balancing`
- `ai_analysis`
- `attack_simulation`

## 📊 Monitoring & Alerts

### Health Monitoring
- Overall system health score
- Individual node status
- Network partition detection
- Connection quality metrics

### Real-time Metrics
- CPU, Memory, Disk usage
- Network connections
- Service availability
- Performance trends

### Alert System
- Node disconnections
- High resource usage
- Network partitions
- Security incidents

## 🚨 Troubleshooting

### Common Issues

**Peer Cannot Connect to Guardian**
- Check Guardian IP address
- Verify JWT token is valid
- Ensure ports 3001 and 3002 are open
- Check network connectivity

**Frontend Not Loading**
- Ensure Node.js is installed
- Run `npm install` in frontend directory
- Check port 3000 is available
- Verify frontend dependencies

**Missing Dependencies**
- Run: `pip install -r requirements.txt`
- For specific packages: `pip install fastapi uvicorn websockets`

**Database Connection Issues**
- MongoDB: Check MONGODB_URI in .env
- Neo4j: Verify NEO4J_URI credentials
- AI Services: Validate GEMINI_API_KEY

### Debug Commands
```bash
# Check node status
curl http://localhost:3001/distributed/health

# Test JWT token
curl -H "Authorization: Bearer YOUR_TOKEN" http://[GUARDIAN_IP]:3001/distributed/nodes

# Monitor logs
tail -f guardian-server/logs/app.log
```

## 🎉 Success Verification

✅ **Guardian Setup Complete When:**
- Admin panel loads at http://[IP]:3000/admin
- API responds at http://[IP]:3001/health
- System shows "Guardian" node type

✅ **Peer Setup Complete When:**
- Peer panel loads at http://[IP]:3000/peer
- Can connect to Guardian successfully
- Metrics are being sent automatically

✅ **Network Setup Complete When:**
- All nodes show "Connected" status
- Health scores are > 80%
- No network partitions detected
- Real-time metrics flowing

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files in `logs/` directory
3. Verify network connectivity between computers
4. Ensure all dependencies are installed

---

**Generated on {self.system_info['hostname']} - {self.system_info['ip_address']}**
**Platform: {self.system_info['platform']} {self.system_info['architecture']}**
"""
        
        with open("DISTRIBUTED_DEPLOYMENT_GUIDE.md", "w") as f:
            f.write(guide)
        
        print("📚 Created comprehensive deployment guide: DISTRIBUTED_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment interface"""
    deployment = DistributedDeployment()
    
    print("🛡️  Aegis of Alderaan - Distributed System Deployment")
    print("=" * 60)
    print(f"💻 Current System: {deployment.system_info['hostname']} ({deployment.system_info['ip_address']})")
    print(f"🖥️  Platform: {deployment.system_info['platform']} {deployment.system_info['architecture']}")
    print()
    
    print("Choose deployment type:")
    print("1. 🛡️  Setup Guardian Node (Central Coordinator)")
    print("2. 💻 Setup Peer Node (Connected Computer)")
    print("3. 📚 Create Deployment Guide Only")
    print("4. ❌ Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        result = deployment.setup_guardian_node()
        deployment.create_deployment_guide()
        print("\n🎉 Guardian node setup complete!")
        print("Next steps:")
        print("1. Start the system using the startup scripts")
        print("2. Open the admin panel to manage the network")
        print("3. Generate tokens for peer computers")
        
    elif choice == "2":
        result = deployment.setup_peer_node()
        print("\n🎉 Peer node setup complete!")
        print("Next steps:")
        print("1. Start the system using the startup scripts")
        print("2. Get a JWT token from the Guardian")
        print("3. Connect to the Guardian using the peer panel")
        
    elif choice == "3":
        deployment.create_deployment_guide()
        print("\n📚 Deployment guide created!")
        
    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
