# 🎯 Aegis AI System - Ready for Postman Testing!

## ✅ What's Ready

### 📦 **Complete AI-Powered API**

- **7 AI Endpoints** with Gemini 2.0 Flash integration
- **Graph Database Integration** with Neo4j mirroring
- **Attack Simulation Routes** for frontend integration
- **Self-Healing Processes** with intelligent automation

### 🧪 **Postman Test Suite**

- **Complete Collection**: `Aegis_AI_Postman_Collection.json`
- **Environment Setup**: `Aegis_AI_Postman_Environment.json`
- **Testing Guide**: `POSTMAN_TESTING_GUIDE.md`

## 🚀 Quick Start for Postman Testing

### 1. **Start the Server**

```bash
cd guardian-server
python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload
```

### 2. **Import into Postman**

1. Open Postman
2. Import `Aegis_AI_Postman_Collection.json`
3. Import `Aegis_AI_Postman_Environment.json`
4. Set environment to "Aegis AI Development Environment"

### 3. **Start Testing**

🌐 **Server**: http://localhost:3001  
📖 **API Docs**: http://localhost:3001/docs  
⚡ **Health Check**: http://localhost:3001/health

## 🧠 Key AI Endpoints to Test

### **Health Analysis (Core AI Feature)**

```
POST http://localhost:3001/ai/analyze/health/test-agent-001
```

**Response**: AI health analysis with severity, root cause, confidence score

### **Mirror Recommendation (Smart Decisions)**

```
POST http://localhost:3001/ai/mirror/recommend/test-agent-001
```

**Response**: AI recommendation for mirror activation with risk assessment

### **Healing Strategy (Intelligent Recovery)**

```
POST http://localhost:3001/ai/healing/strategy/test-agent-001
```

**Response**: Step-by-step AI-generated healing plan with phases

### **AI Mirror Topology (Enhanced View)**

```
GET http://localhost:3001/ai/mirror/topology
```

**Response**: Graph topology with AI health insights for each node

### **Failure Prediction (Predictive Analytics)**

```
POST http://localhost:3001/ai/predict/failure/test-agent-001
```

**Response**: AI prediction of failure risk and recommended actions

## ⚔️ Attack Simulation for Testing

### **Available Attack Types**

```
GET http://localhost:3001/simulate/attack/types
```

### **CPU Attack Simulation**

```
POST http://localhost:3001/simulate/attack/cpu
Body: {
  "target_agent": "test-agent-001",
  "cpu_percentage": 90,
  "duration": 30
}
```

### **Memory Attack Simulation**

```
POST http://localhost:3001/simulate/attack/memory
Body: {
  "target_agent": "test-agent-001",
  "memory_mb": 800,
  "duration": 30
}
```

## 🕸️ Neo4j Graph Database Testing

### **Create Mirror Relationships**

```
POST http://localhost:3001/agents/test-agent-001/relationships/mirror
Body: {
  "mirror_agent": "test-mirror-001"
}
```

### **Setup Agent Mirroring**

```
POST http://localhost:3001/agents/test-agent-001/mirror/setup
Body: {
  "mirrors": [
    {
      "agent_id": "test-mirror-001",
      "type": "active",
      "priority": 1
    }
  ]
}
```

## 🎯 Testing Scenarios

### **Scenario 1: Basic AI Health Check**

1. `GET /health` → Verify all services
2. `POST /ai/analyze/health/test-agent-001` → Get AI assessment
3. Check response for AI analysis fields

### **Scenario 2: Complete AI Workflow**

1. Health Analysis → Get current status
2. Mirror Recommendation → Get AI advice
3. Healing Strategy → Get recovery plan
4. Mirror Topology → View enhanced graph

### **Scenario 3: Attack + AI Response**

1. Simulate CPU attack → Create stress
2. AI Health Analysis → See AI assessment of impact
3. AI Healing Strategy → Get AI recovery plan
4. Stop attack → End simulation

## 📊 Expected AI Responses

### **Health Analysis Response**

```json
{
  "agent_id": "test-agent-001",
  "analysis": {
    "severity": "medium|high|critical",
    "root_cause": "Detailed AI explanation",
    "healing_strategy": "AI recommended approach",
    "mirror_recommendation": "should_activate|monitor_closely",
    "estimated_recovery_time": 15,
    "confidence_score": 0.85,
    "immediate_actions": ["Restart service", "Clear cache"],
    "preventive_measures": ["Monitor resources"]
  },
  "ai_enabled": true
}
```

### **Mirror Recommendation Response**

```json
{
  "recommendation": {
    "should_activate_mirror": true,
    "mirror_node_id": "best-candidate",
    "transition_strategy": "gradual",
    "risk_assessment": "low"
  }
}
```

## 🛠️ Troubleshooting

### **If AI not working:**

- Check `.env` has `GEMINI_API_KEY=your-api-key`
- Install: `pip install google-generativeai`

### **If Neo4j not working:**

- Check `.env` has Neo4j credentials
- Try fallback mode (AI still works without Neo4j)

### **If MongoDB not working:**

- Check connection string in `.env`
- Some endpoints will use fallback responses

## 🎉 Success Indicators

✅ **Health endpoint shows all services green**  
✅ **AI endpoints return intelligent analysis**  
✅ **Mirror topology shows graph relationships**  
✅ **Attack simulations trigger AI responses**  
✅ **Confidence scores > 0.7 for AI recommendations**

## 🔥 Advanced Features to Test

- **Real-time WebSocket updates** (if you have WebSocket client)
- **JWT authentication** for secure agent connections
- **Attack simulation history** tracking
- **Self-healing process management**
- **Network topology visualization** data

---

## 🚀 You're Ready to Test!

Your Aegis AI-Powered Self-Healing System is fully implemented with:

🧠 **Gemini 2.0 Flash AI Integration**  
🕸️ **Neo4j Graph Database Mirroring**  
⚔️ **Attack Simulation API**  
🛡️ **Intelligent Self-Healing**  
📊 **Predictive Analytics**

**Start the server and begin testing in Postman!** 🎊
