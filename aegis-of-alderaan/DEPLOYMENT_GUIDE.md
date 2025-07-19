# 🚀 Complete Aegis Deployment Guide

## Quick Deploy (One Command)

```bash
# Deploy everything at once
python deploy_complete.py
```

This will deploy:

- **Guardian Server** (port 3001)
- **3 Monitoring Agents** (agent-001, agent-002, agent-003)
- **Neo4j Relationships** (automatic setup)
- **Self-healing capabilities**

## Manual Docker Deployment

```bash
# Build and deploy
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## What Gets Deployed

### 🛡️ Guardian Server

- **Container**: `aegis-guardian-server`
- **Port**: 3001
- **APIs**: http://localhost:3001/docs
- **Health**: http://localhost:3001/health

### 🤖 Agents

- **agent-001**: Primary monitoring agent
- **agent-002**: Backup monitoring agent
- **agent-003**: Edge monitoring agent

### 🔗 Neo4j Features

- **Mirror relationships** between agents
- **Monitoring relationships**
- **Network connections**
- **Self-healing coordination**

## Environment Variables

Make sure your `.env` file contains:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Neo4j Aura
NEO4J_URI=neo4j+s://your-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## Management Commands

```bash
# Deploy complete system
python deploy_complete.py

# View all logs
python deploy_complete.py logs

# View specific service logs
python deploy_complete.py logs aegis-guardian

# Check status
python deploy_complete.py status

# Stop system
python deploy_complete.py down
```

## Verification

After deployment, check:

1. **Guardian Health**: http://localhost:3001/health
2. **Connected Agents**: http://localhost:3001/agents
3. **Network Topology**: http://localhost:3001/network/topology
4. **API Docs**: http://localhost:3001/docs

## Scaling

```bash
# Scale to more agents
docker-compose up -d --scale aegis-agent-1=5

# Add custom agent
docker-compose run --rm -e AGENT_ID=custom-001 aegis-agent-1
```

## Production Deployment

For production, consider:

### Cloud Platforms

#### **AWS ECS/Fargate**

```bash
# Use AWS CLI to deploy
aws ecs create-cluster --cluster-name aegis-cluster
```

#### **Azure Container Instances**

```bash
# Deploy to Azure
az container create --resource-group aegis-rg --file docker-compose.yml
```

#### **Google Cloud Run**

```bash
# Deploy to Cloud Run
gcloud run deploy aegis-guardian --source .
```

#### **Kubernetes**

```yaml
# Convert to Kubernetes
kompose convert -f docker-compose.yml
```

### Environment-Specific Files

#### **Production (.env.prod)**

```env
# Production database connections
MONGODB_URI=mongodb+srv://prod-user:password@prod-cluster.mongodb.net/aegis_prod
NEO4J_URI=neo4j+s://prod-id.databases.neo4j.io
JWT_SECRET_KEY=super-secure-production-key
```

#### **Staging (.env.staging)**

```env
# Staging database connections
MONGODB_URI=mongodb+srv://staging-user:password@staging-cluster.mongodb.net/aegis_staging
NEO4J_URI=neo4j+s://staging-id.databases.neo4j.io
```

### Load Balancer Setup

```yaml
# nginx.conf for load balancing
upstream aegis_guardian {
server guardian1:3001;
server guardian2:3001;
server guardian3:3001;
}

server {
listen 80;
location / {
proxy_pass http://aegis_guardian;
}
}
```

## Monitoring & Observability

### Prometheus Metrics

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Grafana Dashboard

```yaml
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Troubleshooting

### Common Issues

#### Agents not connecting

```bash
# Check Guardian logs
docker-compose logs aegis-guardian

# Check agent logs
docker-compose logs aegis-agent-1

# Verify network
docker network ls
```

#### Database connection issues

```bash
# Test MongoDB connection
python -c "import pymongo; print(pymongo.MongoClient('your-uri').admin.command('ping'))"

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; print('Neo4j OK')"
```

#### Port conflicts

```bash
# Check what's using port 3001
netstat -tulpn | grep 3001

# Use different port
docker-compose up -d -p 3002:3001 aegis-guardian
```

---

**🛡️ Your complete Aegis of Alderaan system is now ready for deployment!**
