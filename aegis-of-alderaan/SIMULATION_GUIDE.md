# 🛡️ Aegis of Alderaan - Complete Simulation Guide

## 📋 **Prerequisites**

### 1. **Verify Project Structure**

Open PowerShell and navigate to project:

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
dir
```

You should see:

- ✅ `guardian-server/` folder
- ✅ `agent/` folder
- ✅ `.env` file
- ✅ `.env.example` file

### 2. **Install Dependencies**

#### Guardian Server Dependencies:

```powershell
cd guardian-server
pip install -r requirements.txt
```

#### Agent Dependencies:

```powershell
cd ..\agent
pip install -r requirements.txt
```

### 3. **Verify Environment Variables**

Check your `.env` file contains:

- MongoDB Atlas connection string
- Neo4j Aura connection details
- JWT secret key

---

## 🎯 **Simulation Steps**

### **STEP 1: Start Guardian Server**

Open **Terminal 1** (PowerShell):

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\guardian-server
python start_server.py
```

**Expected Output:**

```
============================================================
🛡️  Aegis of Alderaan - Guardian Server Startup
============================================================
🔧 NEO4J_URI: neo4j+s://4b0b9e6e.databases.neo4j.io
🔧 MONGODB_URI: mongodb+srv://mohantyswastik7008:...
✅ FastAPI available
✅ Motor (MongoDB driver) available
✅ Neo4j driver available
✅ WebSockets available
✅ PyJWT available
INFO:db.mongo_handler:Connected to MongoDB Cloud successfully
INFO:db.neo4j_handler:Connected to Neo4j Cloud successfully
INFO:app:✅ Guardian Server started successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**🚨 If you see errors:**

- MongoDB connection failed → Check MongoDB Atlas connection string
- Neo4j connection failed → Check Neo4j Aura credentials
- Import errors → Install missing dependencies with pip

### **STEP 2: Verify Guardian Server Health**

Open **Terminal 2** (PowerShell):

```powershell
# Test server health endpoint
curl http://localhost:8000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T10:30:00Z",
  "services": {
    "database": "connected",
    "websocket": "running"
  }
}
```

### **STEP 3: Test Database Connections**

```powershell
curl http://localhost:8000/status
```

**Expected Response:**

```json
{
  "mongodb": "connected",
  "neo4j": "connected",
  "agents_count": 0,
  "uptime": "0:02:15"
}
```

### **STEP 4: Start First Agent**

Open **Terminal 3** (PowerShell):

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent
python start_agent.py
```

**Expected Output:**

```
============================================================
🤖 Aegis Agent Starting Up
============================================================
Agent ID: DESKTOP-ABC123-agent
Guardian Server: ws://localhost:8000/ws
🔐 Authenticating with Guardian...
✅ JWT token obtained
🌐 Connecting to Guardian Server...
✅ Connected to Guardian successfully
📊 Starting metrics collection...
🔍 Starting anomaly detection...
🛠️  Self-healing engine ready
⚡ Agent operational - monitoring endpoint
```

### **STEP 5: Monitor Agent Registration**

In **Terminal 1** (Guardian Server), you should see:

```
INFO:websocket_handler:New agent connected: DESKTOP-ABC123-agent
INFO:db.mongo_handler:Agent DESKTOP-ABC123-agent registered successfully
INFO:remediation_engine:Agent DESKTOP-ABC123-agent added to monitoring
```

### **STEP 6: Test Real-Time Metrics**

Wait 10-15 seconds for metrics collection, then check:

```powershell
# In Terminal 2
curl http://localhost:8000/api/agents
```

**Expected Response:**

```json
{
  "agents": [
    {
      "agent_id": "DESKTOP-ABC123-agent",
      "hostname": "DESKTOP-ABC123",
      "status": "online",
      "last_heartbeat": "2025-01-17T10:35:00Z",
      "role": "endpoint",
      "cpu_percent": 25.4,
      "memory_percent": 60.2,
      "disk_percent": 45.8
    }
  ],
  "total_agents": 1,
  "online_agents": 1
}
```

### **STEP 7: Test Metrics History**

```powershell
curl "http://localhost:8000/api/metrics/DESKTOP-ABC123-agent?limit=5"
```

**Expected Response:**

```json
{
  "agent_id": "DESKTOP-ABC123-agent",
  "metrics": [
    {
      "timestamp": "2025-01-17T10:35:00Z",
      "cpu_percent": 25.4,
      "memory_percent": 60.2,
      "disk_percent": 45.8,
      "network_bytes_sent": 1024000,
      "network_bytes_recv": 2048000
    }
  ],
  "count": 5
}
```

### **STEP 8: Simulate High CPU Load (Anomaly Detection)**

In **Terminal 4**, create artificial load:

```powershell
# Start a CPU-intensive task
python -c "while True: pass"
```

**In Agent Terminal (Terminal 3), you should see:**

```
⚠️  ANOMALY DETECTED: High CPU usage: 95.2%
🛠️  SELF-HEALING: Attempting to reduce CPU load
📤 Reporting anomaly to Guardian Server
```

**In Guardian Server Terminal (Terminal 1):**

```
WARNING:remediation_engine:Anomaly detected on DESKTOP-ABC123-agent: high_cpu
INFO:remediation_engine:Initiating remediation for DESKTOP-ABC123-agent
```

**Stop the CPU load (Ctrl+C in Terminal 4)**

### **STEP 9: Start Second Agent (Multi-Agent Simulation)**

Open **Terminal 5**:

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent
# Set different agent ID
set AGENT_ID=DESKTOP-ABC123-agent-2
python start_agent.py
```

**Expected:** Second agent registers and starts monitoring.

### **STEP 10: Test WebSocket Real-Time Updates**

```powershell
# In Terminal 2, test WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:8000/ws/dashboard
```

### **STEP 11: View Network Topology**

```powershell
curl http://localhost:8000/api/topology
```

**Expected Response:**

```json
{
  "nodes": [
    {
      "id": "DESKTOP-ABC123-agent",
      "type": "agent",
      "status": "online",
      "hostname": "DESKTOP-ABC123"
    },
    {
      "id": "DESKTOP-ABC123-agent-2",
      "type": "agent",
      "status": "online",
      "hostname": "DESKTOP-ABC123"
    }
  ],
  "relationships": [
    {
      "from": "DESKTOP-ABC123-agent",
      "to": "guardian-server",
      "type": "reports_to"
    }
  ]
}
```

---

## 🧪 **Advanced Testing Scenarios**

### **Scenario A: Agent Failure Simulation**

1. Stop one agent (Ctrl+C in Terminal 3)
2. Wait 2 minutes
3. Check offline agents: `curl http://localhost:8000/api/agents/offline`

### **Scenario B: Network Disconnection**

1. Disconnect from internet briefly
2. Observe agent reconnection attempts
3. Verify data sync when connection restored

### **Scenario C: Database Failure Handling**

1. Temporarily block MongoDB Atlas IP
2. Observe graceful degradation
3. Restore connection and verify recovery

---

## ✅ **Success Indicators**

**Your simulation is successful if you see:**

1. ✅ **Guardian Server**: Starts without errors, connects to databases
2. ✅ **Agent Registration**: Agents connect and authenticate successfully
3. ✅ **Real-Time Metrics**: Data flows from agents to Guardian continuously
4. ✅ **Anomaly Detection**: System detects and responds to threats
5. ✅ **Self-Healing**: Agents attempt automatic remediation
6. ✅ **API Responses**: All endpoints return proper JSON data
7. ✅ **Multi-Agent**: Multiple agents can run simultaneously
8. ✅ **Persistence**: Data stored in MongoDB and Neo4j clouds

---

## 🛑 **Stopping the Simulation**

**Graceful Shutdown:**

1. Stop agents first (Ctrl+C in agent terminals)
2. Stop Guardian Server (Ctrl+C in server terminal)
3. Verify all connections closed properly

**Data Cleanup (Optional):**

```powershell
# Clear test data from databases if needed
curl -X DELETE http://localhost:8000/api/cleanup/test-data
```

---

## 📊 **What You Should See Working**

- **Real-time monitoring** of system metrics
- **Automatic threat detection** and alerting
- **Self-healing** capabilities on endpoints
- **Centralized orchestration** from Guardian Server
- **Cloud database storage** with MongoDB Atlas and Neo4j Aura
- **WebSocket communication** between agents and server
- **RESTful API** for management and monitoring
- **JWT authentication** for secure communications
- **Network topology mapping** and visualization data

This simulation demonstrates a complete **resilient network protection system** with distributed agents, centralized intelligence, and cloud-based persistence! 🚀
