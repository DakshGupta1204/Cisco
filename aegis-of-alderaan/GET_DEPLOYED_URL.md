# 🌐 Get Your Public Backend URL - Quick Guide

## 🚀 **Fastest Deployment (5 minutes)**

### Option 1: Railway (Recommended)

```bash
# Deploy with one command
python deploy_cloud.py
# Choose option 1
```

**Result**: `https://aegis-guardian-production.railway.app`

### Option 2: Manual Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
railway domain
```

### Option 3: Render.com

1. Go to [render.com](https://render.com)
2. "New" → "Web Service"
3. Connect your GitHub repo
4. Choose "Docker"
5. Add environment variables from `.env`
6. Deploy!

**Result**: `https://aegis-guardian.onrender.com`

---

## 📋 **What You Need**

### ✅ Files Ready:

- `Dockerfile` ✅ (Optimized for cloud)
- `railway.json` ✅ (Railway config)
- `render.yaml` ✅ (Render config)
- `fly.toml` ✅ (Fly.io config)
- `deploy_cloud.py` ✅ (Automated deployment)

### 🔑 Environment Variables:

Make sure your `.env` has:

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/aegis_db
NEO4J_URI=neo4j+s://your-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
JWT_SECRET_KEY=your-super-secret-key
```

---

## 🎯 **Your Deployed URLs**

After deployment, you'll get:

- **🏠 Main URL**: `https://your-app.railway.app`
- **📚 API Docs**: `https://your-app.railway.app/docs`
- **💓 Health**: `https://your-app.railway.app/health`
- **🤖 Agents**: `https://your-app.railway.app/agents`
- **🌐 Network**: `https://your-app.railway.app/network/topology`
- **🔌 WebSocket**: `wss://your-app.railway.app/ws`

---

## ⚡ **Quick Commands**

```bash
# Deploy to Railway
python deploy_cloud.py

# Or manual Railway
railway login && railway up

# Check deployment
curl https://your-app.railway.app/health

# View API docs
# Open: https://your-app.railway.app/docs
```

---

## 🎉 **Ready to Deploy!**

Your backend is fully configured for cloud deployment. Just run:

```bash
python deploy_cloud.py
```

Choose Railway (option 1) and you'll have your public backend URL in 5 minutes!

**🛡️ Your Aegis of Alderaan backend will be live and accessible from anywhere!**
