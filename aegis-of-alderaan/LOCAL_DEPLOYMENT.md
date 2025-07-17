# 🏠 Local Deployment Guide

## ⚡ Quick Start (ONE Command)

```bash
# Start everything locally
docker-compose up -d --build
```

This single command starts:

- 🛡️ **Guardian Server** → http://localhost:3001
- 🤖 **Agent 1** → Connects to Guardian
- 🤖 **Agent 2** → Connects to Guardian
- 🤖 **Agent 3** → Connects to Guardian
- 🔗 **Neo4j Relationships** → Automatic setup

## 📋 What Runs Locally

### Guardian Server

- **Port**: 3001
- **URL**: http://localhost:3001
- **APIs**: http://localhost:3001/docs
- **Status**: http://localhost:3001/health

### Agents

- **agent-001**: Primary monitoring
- **agent-002**: Backup monitoring
- **agent-003**: Edge monitoring
- All connect via WebSocket to Guardian

### Databases

- **MongoDB Atlas**: Cloud metrics storage
- **Neo4j Aura**: Cloud relationships

## 🎯 Local vs Cloud Comparison

| Feature     | Local Deployment     | Cloud Deployment      |
| ----------- | -------------------- | --------------------- |
| **Command** | `docker-compose up`  | Deploy to Render      |
| **URL**     | localhost:3001       | your-app.onrender.com |
| **Agents**  | 3 local agents       | 2 cloud agents        |
| **Access**  | Your network only    | Public internet       |
| **Cost**    | Free (your computer) | Free tier available   |

## 🔧 Management Commands

```bash
# Start everything
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop everything
docker-compose down

# Restart specific service
docker-compose restart aegis-guardian
```

## ✅ Verification

After `docker-compose up -d --build`:

1. **Check Guardian**: http://localhost:3001/health
2. **View Agents**: http://localhost:3001/agents
3. **API Docs**: http://localhost:3001/docs
4. **View Logs**: `docker-compose logs aegis-guardian`

## 🛠️ Troubleshooting

### If services don't start:

```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up -d --build
```

### If agents don't connect:

```bash
# Check agent logs
docker-compose logs aegis-agent-1

# Restart agents
docker-compose restart aegis-agent-1
```

---

**🎉 ONE command gives you the complete Aegis system locally!**
