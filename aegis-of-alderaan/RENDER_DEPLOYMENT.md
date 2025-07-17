# 🚀 Complete Render Deployment: Guardian + Agents

## 📋 What You're Deploying

Your Render deployment will include:

### 🛡️ **Guardian Server** (Web Service)

- **URL**: `https://aegis-guardian.onrender.com`
- **Endpoints**:
  - 📚 API Docs: `/docs`
  - 💓 Health Check: `/health`
  - 🤖 Connected Agents: `/agents`
  - 🌐 Network Topology: `/network/topology`
  - 🔌 WebSocket: `/ws`

### 🤖 **Cloud Agents** (Background Workers)

- **Agent 1**: `cloud-agent-001` (Background worker)
- **Agent 2**: `cloud-agent-002` (Background worker)
- Both connect automatically to Guardian
- Monitor cloud environment metrics
- Participate in Neo4j relationships

---

## 🚀 **Deployment Steps**

### Step 1: Push Code to GitHub

```bash
# Make sure your code is on GitHub
git add .
git commit -m "Complete Aegis deployment with Guardian + Agents"
git push origin main
```

### Step 2: Deploy to Render

1. Go to **[render.com](https://render.com)** and sign up/login
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Set your environment variables (see below)
6. Click **"Apply"**

### Step 3: Set Environment Variables

In Render dashboard, add these secrets:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/aegis_db
NEO4J_URI=neo4j+s://your-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
JWT_SECRET_KEY=your-super-secret-key-here
```

---

## 🎯 **What You'll Get**

### **Public Guardian API**

```
🌐 https://aegis-guardian.onrender.com
├── GET  /health              # System health
├── GET  /agents              # Connected agents
├── GET  /docs                # API documentation
├── GET  /network/topology    # Network map
├── POST /agents/{id}/heal    # Trigger healing
└── WS   /ws                  # WebSocket connection
```

### **Connected Agents**

```json
{
  "connected_agents": [
    {
      "id": "cloud-agent-001",
      "status": "active",
      "location": "render-cloud",
      "metrics": {...}
    },
    {
      "id": "cloud-agent-002",
      "status": "active",
      "location": "render-cloud",
      "metrics": {...}
    }
  ]
}
```

### **Neo4j Relationships**

- 🔗 Agent mirroring relationships
- 📊 Monitoring connections
- 🌐 Network topology mapping
- 🔄 Self-healing coordination

---

## 🔧 **render.yaml Configuration**

Your `render.yaml` includes:

```yaml
services:
  # Guardian Server - Main API
  - type: web
    name: aegis-guardian
    startCommand: python guardian-server/app.py

  # Agent 1 - Background Worker
  - type: worker
    name: aegis-agent-1
    startCommand: python -c "import os; os.environ['AGENT_ID']='cloud-agent-001'; exec(open('agent/main.py').read())"

  # Agent 2 - Background Worker
  - type: worker
    name: aegis-agent-2
    startCommand: python -c "import os; os.environ['AGENT_ID']='cloud-agent-002'; exec(open('agent/main.py').read())"
```

---

## ✅ **Verification Steps**

After deployment:

1. **Check Guardian Health**:

   ```bash
   curl https://aegis-guardian.onrender.com/health
   ```

2. **View Connected Agents**:

   ```bash
   curl https://aegis-guardian.onrender.com/agents
   ```

3. **Open API Documentation**:

   ```
   https://aegis-guardian.onrender.com/docs
   ```

4. **Check Render Dashboard**:
   - All 3 services should show "Live" status
   - Guardian service has public URL
   - Agent workers show "Running"

---

## 🛠️ **Troubleshooting**

### If agents don't connect:

- Check Render logs for each service
- Verify environment variables are set
- Ensure Guardian is running before agents start

### If Guardian fails to start:

- Check database connection strings
- Verify all secrets are properly set
- Review Render build logs

### View Logs:

```bash
# In Render dashboard
- Go to each service
- Click "Logs" tab
- Check for connection errors
```

---

## 🎉 **Success Metrics**

You'll know it's working when:

✅ Guardian shows "Live" status  
✅ Both agents show "Running" status  
✅ `/agents` endpoint shows 2 connected agents  
✅ `/health` returns healthy status  
✅ Neo4j relationships are created  
✅ Metrics are being collected

**🛡️ Your complete Aegis of Alderaan system will be live in the cloud!**
