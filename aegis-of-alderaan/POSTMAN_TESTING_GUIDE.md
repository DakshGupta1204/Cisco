# 🧪 Aegis AI System - Postman Testing Guide

## 🚀 Quick Start

### 1. Start the Server

```bash
# Option 1: Using the startup script
python start_server.py

# Option 2: Manual startup
cd guardian-server
python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload
```

### 2. Import Postman Collection

1. Open Postman
2. Click **Import**
3. Select `Aegis_AI_Postman_Collection.json`
4. Import `Aegis_AI_Postman_Environment.json` as environment

### 3. Configure Environment

- Set `base_url` to `http://localhost:3001`
- Set `agent_id` to `test-agent-001`

## 🎯 Test Sequence

### **Step 1: Health Check**

```
GET {{base_url}}/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "version": "1.0.0",
  "services": {
    "websocket": 0,
    "mongodb": true,
    "neo4j": true,
    "gemini_ai": true,
    "remediation": true
  }
}
```

### **Step 2: AI Health Analysis**

```
POST {{base_url}}/ai/analyze/health/{{agent_id}}
```

**Expected Response:**

```json
{
  "agent_id": "test-agent-001",
  "analysis": {
    "severity": "medium|high|critical",
    "root_cause": "AI analysis of the issue",
    "healing_strategy": "Recommended approach",
    "mirror_recommendation": "should_activate|attempt_heal",
    "estimated_recovery_time": 15,
    "confidence_score": 0.85,
    "immediate_actions": ["action1", "action2"],
    "preventive_measures": ["measure1", "measure2"]
  },
  "timestamp": "2024-...",
  "ai_enabled": true
}
```

### **Step 3: Mirror Recommendation**

```
POST {{base_url}}/ai/mirror/recommend/{{agent_id}}
```

**Expected Response:**

```json
{
  "agent_id": "test-agent-001",
  "recommendation": {
    "should_activate_mirror": true,
    "mirror_node_id": "best-mirror-candidate",
    "transition_strategy": "gradual|immediate",
    "rollback_conditions": ["condition1", "condition2"],
    "risk_assessment": "low|medium|high"
  },
  "available_mirrors": [...],
  "timestamp": "2024-..."
}
```

### **Step 4: Healing Strategy**

```
POST {{base_url}}/ai/healing/strategy/{{agent_id}}
```

**Expected Response:**

```json
{
  "agent_id": "test-agent-001",
  "health_analysis": {...},
  "healing_strategy": {
    "strategy_id": "unique_identifier",
    "priority": "immediate|urgent|normal",
    "phases": [
      {
        "phase": "immediate_stabilization",
        "actions": ["action1", "action2"],
        "expected_duration": 5,
        "success_criteria": ["criteria1", "criteria2"]
      }
    ],
    "estimated_total_time": 20
  },
  "timestamp": "2024-..."
}
```

### **Step 5: Mirror Topology**

```
GET {{base_url}}/ai/mirror/topology
```

**Expected Response:**

```json
{
  "mirror_topology": {
    "primary-agent-1": {
      "primary_info": {...},
      "mirrors": [...],
      "ai_health_analysis": {...}
    }
  },
  "total_primary_nodes": 1,
  "ai_analysis_enabled": true,
  "timestamp": "2024-..."
}
```

## 🔄 Advanced Testing Scenarios

### **Scenario 1: Complete AI Workflow**

1. **Health Check** → Verify system status
2. **AI Health Analysis** → Get intelligent assessment
3. **Mirror Recommendation** → Get AI mirror advice
4. **Healing Strategy** → Get step-by-step plan
5. **Mirror Activation** → Execute AI recommendation

### **Scenario 2: Attack Simulation + AI Response**

1. **Get Attack Types** → See available simulations
2. **Simulate CPU Attack** → Trigger high CPU usage
3. **AI Health Analysis** → Analyze the impact
4. **AI Healing Strategy** → Get recovery plan
5. **Stop Attack** → End simulation

### **Scenario 3: Neo4j Graph Operations**

1. **Create Mirror Relationship** → Setup graph connections
2. **Setup Agent Mirroring** → Configure multiple mirrors
3. **Get Mirror Topology** → View graph structure
4. **AI Mirror Topology** → Get AI-enhanced view

## 📊 Response Status Codes

| Code | Meaning             | Action                     |
| ---- | ------------------- | -------------------------- |
| 200  | Success             | Continue testing           |
| 404  | Agent not found     | Create test agent first    |
| 503  | Service unavailable | Check database connections |
| 500  | Server error        | Check logs for details     |

## 🛠️ Troubleshooting

### **Issue: Neo4j not available**

**Solution:**

```bash
# Check .env file has Neo4j credentials
NEO4J_URI=neo4j+s://your-database.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### **Issue: MongoDB not available**

**Solution:**

```bash
# Check MongoDB connection
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
```

### **Issue: Gemini AI not working**

**Solution:**

```bash
# Add Gemini API key to .env
GEMINI_API_KEY=your-gemini-api-key
```

### **Issue: Agent not found**

**Solution:**

```bash
# First authenticate an agent
POST /auth/agent
{
  "agent_id": "test-agent-001",
  "hostname": "test-server-1",
  "role": "web_server"
}
```

## 🎯 Key Endpoints to Test

### **🧠 AI Intelligence**

- `POST /ai/analyze/health/{agent_id}` - Core AI health analysis
- `POST /ai/mirror/recommend/{agent_id}` - Smart mirror decisions
- `POST /ai/healing/strategy/{agent_id}` - Intelligent recovery plans
- `POST /ai/predict/failure/{agent_id}` - Predictive analytics

### **🔄 Mirror Management**

- `GET /ai/mirror/topology` - AI-enhanced topology view
- `POST /ai/mirror/activate/{agent_id}` - AI-driven activation
- `GET /agents/{agent_id}/mirrors` - Mirror relationship status

### **⚔️ Attack Simulation**

- `GET /simulate/attack/types` - Available attack types
- `POST /simulate/attack/cpu` - CPU spike simulation
- `POST /simulate/attack/ddos` - DDoS attack simulation
- `GET /simulate/attack/history` - Attack simulation history

### **🕸️ Graph Database**

- `GET /network/topology` - Network graph structure
- `POST /agents/{agent_id}/relationships/mirror` - Create mirror links
- `GET /network/mirror-topology` - Mirror relationship graph

## 🎉 Expected AI Behaviors

### **Smart Health Analysis**

- **High CPU/Memory** → AI recommends immediate action
- **Multiple Issues** → AI suggests mirror activation
- **Service Failures** → AI creates step-by-step recovery

### **Intelligent Mirror Decisions**

- **Primary node critical** → AI recommends immediate mirror activation
- **Minor issues** → AI suggests monitoring and gradual transition
- **No suitable mirrors** → AI recommends alternative strategies

### **Autonomous Healing**

- **Confidence > 0.8** → AI provides detailed action plans
- **Complex issues** → AI breaks down into manageable phases
- **Risk assessment** → AI evaluates rollback conditions

## 📈 Performance Expectations

- **Health Analysis**: < 3 seconds
- **Mirror Recommendation**: < 2 seconds
- **Healing Strategy**: < 4 seconds
- **Topology Queries**: < 1 second

## 🎊 Success Criteria

✅ **All health checks return green**  
✅ **AI provides intelligent recommendations**  
✅ **Mirror topology shows proper relationships**  
✅ **Attack simulations trigger AI responses**  
✅ **Healing strategies show actionable steps**

Happy testing! 🚀
