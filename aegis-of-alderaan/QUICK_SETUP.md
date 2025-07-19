# 🚨 Quick Setup Before Deployment

## Docker Desktop Setup

**Docker Desktop is not running!** Please follow these steps:

### 1. Start Docker Desktop

- Open **Docker Desktop** application from Start menu
- Wait for it to fully start (green whale icon in system tray)
- Or run: `"C:\Program Files\Docker\Docker\Docker Desktop.exe"`

### 2. Verify Docker is Running

```powershell
docker --version
docker ps
```

### 3. Deploy Aegis System

```powershell
python deploy_complete.py
```

## Alternative: Direct Commands

If you prefer manual deployment:

```powershell
# Start Docker Desktop first, then:
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f aegis-guardian
```

## Environment Check

Make sure your `.env` file exists:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://your-user:your-pass@cluster.mongodb.net/aegis_db

# Neo4j Aura
NEO4J_URI=neo4j+s://your-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# JWT
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

---

**Once Docker Desktop is running, your deployment command will work perfectly!**

The deployment script will:

- ✅ Build all container images
- ✅ Start Guardian server (port 3001)
- ✅ Start 3 monitoring agents
- ✅ Setup Neo4j relationships
- ✅ Enable self-healing
- ✅ Provide health monitoring
