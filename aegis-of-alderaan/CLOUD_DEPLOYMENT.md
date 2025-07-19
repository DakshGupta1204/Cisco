# Aegis of Alderaan - Cloud Deployment Guide

This guide explains how to deploy the Aegis of Alderaan system with cloud databases instead of local installations.

## Prerequisites

- Python 3.8+ installed
- Git installed
- Accounts for cloud services (MongoDB Atlas, Neo4j Aura)

## 1. Cloud Database Setup

### MongoDB Atlas Setup

1. **Create Account & Cluster**

   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a free account
   - Create a new cluster (choose M0 Sandbox for free tier)
   - Wait for cluster deployment (takes 3-7 minutes)

2. **Configure Database Access**

   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Create a user with "Read and write to any database" permissions
   - Note down the username and password

3. **Configure Network Access**

   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - For development: Add `0.0.0.0/0` (anywhere)
   - For production: Add your specific IP addresses

4. **Get Connection String**
   - Go to "Clusters" and click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password

### Neo4j Aura Setup

1. **Create Account & Database**

   - Go to [Neo4j Aura](https://console.neo4j.io/)
   - Create a free account
   - Click "New Instance"
   - Choose "AuraDB Free"
   - Set a database name and password

2. **Get Connection Details**
   - After creation, note down:
     - Connection URI (starts with `neo4j+s://`)
     - Username (usually `neo4j`)
     - Password (what you set during creation)

## 2. Project Configuration

### Step 1: Clone and Setup

```bash
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
cp .env.example .env
```

### Step 2: Update Environment Variables

Edit the `.env` file with your cloud database credentials:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.xxxxx.mongodb.net/aegis-guardian?retryWrites=true&w=majority

# Neo4j Aura
NEO4J_URI=neo4j+s://your-database-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
```

### Step 3: Install Dependencies

```bash
# Guardian Server
cd guardian-server
pip install -r requirements.txt

# Agent
cd ../agent
pip install -r requirements.txt
```

## 3. Testing Cloud Connections

### Test Guardian Server

```bash
cd guardian-server
python start_server.py
```

You should see:

- ✅ "Connected to MongoDB Cloud successfully"
- ✅ "Connected to Neo4j Cloud successfully"
- ✅ "Guardian Server started on http://0.0.0.0:8000"

### Test Agent Connection

```bash
cd agent
python start_agent.py
```

You should see:

- ✅ "Agent started successfully"
- ✅ "Connected to Guardian server"
- ✅ "JWT authentication successful"

## 4. Production Deployment

### Security Best Practices

1. **Environment Variables**

   - Never commit `.env` files to version control
   - Use your hosting platform's environment variable system
   - Rotate JWT secrets regularly

2. **Database Security**

   - Use specific IP whitelisting instead of 0.0.0.0/0
   - Enable database audit logging
   - Use strong passwords and rotate them

3. **Network Security**
   - Use HTTPS/WSS for all connections
   - Implement rate limiting
   - Use reverse proxy (nginx, CloudFlare)

### Cloud Hosting Options

#### Guardian Server

- **Heroku**: Easy deployment with git push
- **AWS EC2**: Full control, scalable
- **DigitalOcean Droplets**: Simple VPS hosting
- **Railway**: Modern deployment platform

#### Agent Deployment

- Install on target endpoints
- Use configuration management (Ansible, Puppet)
- Docker containers for isolated deployment

## 5. Monitoring and Maintenance

### Health Checks

```bash
# Check Guardian server health
curl http://your-server-url/health

# Check database connections
curl http://your-server-url/status
```

### Log Monitoring

- Monitor application logs
- Set up alerts for connection failures
- Use log aggregation (ELK stack, Splunk)

## 6. Troubleshooting

### Common Issues

1. **Connection Timeouts**

   - Check network access settings
   - Verify IP whitelisting
   - Increase connection timeout values

2. **Authentication Failures**

   - Verify username/password
   - Check JWT secret consistency
   - Ensure password special characters are URL-encoded

3. **SSL/TLS Issues**
   - Ensure `neo4j+s://` for Neo4j Aura
   - Use `mongodb+srv://` for Atlas
   - Verify SSL certificates

### Getting Help

- Check the logs in `guardian.log`
- Verify environment variables are loaded
- Test database connections individually
- Check cloud provider status pages

## 7. Cost Optimization

### Free Tier Limits

- **MongoDB Atlas**: 512 MB storage, 100 connections
- **Neo4j Aura**: 200k nodes, 400k relationships

### Scaling Tips

- Monitor database usage
- Implement data retention policies
- Use database indexing effectively
- Consider sharding for large datasets

---

## Quick Start Commands

```bash
# Setup
cp .env.example .env
# Edit .env with your cloud credentials

# Start Guardian Server
cd guardian-server
pip install -r requirements.txt
python start_server.py

# Start Agent (in new terminal)
cd agent
pip install -r requirements.txt
python start_agent.py
```

Your Aegis of Alderaan system is now running with cloud databases! 🚀
