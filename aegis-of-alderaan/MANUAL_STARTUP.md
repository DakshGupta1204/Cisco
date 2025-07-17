# 🚀 Manual Docker Desktop Startup Guide

## Step 1: Start Docker Desktop Manually

Since automatic startup failed, please **manually start Docker Desktop**:

### Option A: Using Start Menu

1. Press `Windows Key`
2. Type "Docker Desktop"
3. Click on "Docker Desktop" application
4. Wait for the whale icon to turn green in the system tray

### Option B: Using File Explorer

1. Navigate to: `C:\Program Files\Docker\Docker\`
2. Double-click on `Docker Desktop.exe`
3. Wait for startup (30-60 seconds)

### Option C: Using Command Line

```powershell
# Open a new PowerShell window as Administrator
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

## Step 2: Verify Docker is Running

Wait until you see:

- ✅ Green whale icon in system tray
- ✅ Docker Desktop window shows "Engine running"

Then test in PowerShell:

```powershell
docker --version
docker ps
```

Both commands should work without errors.

## Step 3: Deploy Aegis System

Once Docker Desktop is running, deploy with:

```powershell
# Quick deployment
python deploy_complete.py
```

Or manual deployment:

```powershell
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 4: Access Your System

After successful deployment:

- **Guardian API**: http://localhost:3001/docs
- **System Health**: http://localhost:3001/health
- **Network Topology**: http://localhost:3001/network/topology
- **Connected Agents**: http://localhost:3001/agents

## Troubleshooting

### If Docker Desktop won't start:

```powershell
# Restart Docker service
Restart-Service -Name "com.docker.service" -Force

# Or restart Docker Desktop from system tray
# Right-click whale icon → Restart
```

### If still having issues:

```powershell
# Check Windows services
Get-Service -Name "*docker*"

# Manual Docker engine start
net start com.docker.service
```

### Alternative: Use Docker without Desktop

If Docker Desktop continues to fail:

```powershell
# Install Docker Engine directly
# Follow: https://docs.docker.com/engine/install/
```

---

## ⚡ Quick Commands Summary

```powershell
# 1. Start Docker Desktop (manually from Start menu)
# 2. Verify it's running
docker ps

# 3. Deploy everything
python deploy_complete.py

# 4. Check deployment
docker-compose ps
```

**🛡️ Your Aegis system will be ready in minutes!**
