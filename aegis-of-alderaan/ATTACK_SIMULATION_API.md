# 🚨 Attack Simulation API Documentation

## 🎯 Frontend Integration Guide

Your Guardian backend now has comprehensive attack simulation endpoints for frontend buttons!

## 🔗 **Base URL**

- **Local**: `http://localhost:3001`
- **Cloud**: `https://your-app.onrender.com`

---

## 🚨 **Attack Simulation Endpoints**

### 1. **Get Available Attack Types**

```http
GET /simulate/attack/types
```

**Response:**

```json
{
  "attack_types": [
    {
      "id": "cpu_spike",
      "name": "CPU Spike Attack",
      "description": "Simulate high CPU usage",
      "parameters": [
        {
          "name": "cpu_percentage",
          "type": "number",
          "default": 80,
          "min": 10,
          "max": 100
        },
        {
          "name": "duration",
          "type": "number",
          "default": 30,
          "min": 5,
          "max": 300
        }
      ]
    },
    {
      "id": "memory_exhaustion",
      "name": "Memory Exhaustion",
      "description": "Simulate memory overflow",
      "parameters": [
        {
          "name": "memory_mb",
          "type": "number",
          "default": 500,
          "min": 100,
          "max": 2000
        },
        {
          "name": "duration",
          "type": "number",
          "default": 30,
          "min": 5,
          "max": 300
        }
      ]
    },
    {
      "id": "network_flood",
      "name": "Network Flooding",
      "description": "Simulate network traffic overload",
      "parameters": [
        {
          "name": "packet_rate",
          "type": "number",
          "default": 1000,
          "min": 100,
          "max": 10000
        },
        {
          "name": "duration",
          "type": "number",
          "default": 30,
          "min": 5,
          "max": 300
        }
      ]
    },
    {
      "id": "ddos",
      "name": "DDoS Attack",
      "description": "Simulate distributed denial of service",
      "parameters": [
        {
          "name": "request_rate",
          "type": "number",
          "default": 500,
          "min": 100,
          "max": 5000
        },
        {
          "name": "vector",
          "type": "select",
          "options": ["http_flood", "syn_flood", "udp_flood"],
          "default": "http_flood"
        },
        {
          "name": "duration",
          "type": "number",
          "default": 30,
          "min": 5,
          "max": 300
        }
      ]
    }
  ]
}
```

### 2. **Get Connected Agents (For Target Selection)**

```http
GET /agents
```

**Response:**

```json
{
  "agents": [
    {
      "agent_id": "agent-001",
      "hostname": "primary-monitor",
      "status": "active",
      "role": "primary_monitor"
    },
    {
      "agent_id": "agent-002",
      "hostname": "backup-monitor",
      "status": "active",
      "role": "backup_monitor"
    }
  ]
}
```

---

## 🎯 **Frontend Button Examples**

### **CPU Attack Button**

```javascript
// Frontend JavaScript
async function simulateCPUAttack(targetAgent) {
  const response = await fetch("/simulate/attack/cpu", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_agent: targetAgent,
      cpu_percentage: 85,
      duration: 60,
    }),
  });

  const result = await response.json();
  console.log("CPU Attack Started:", result);
}
```

### **Memory Attack Button**

```javascript
async function simulateMemoryAttack(targetAgent) {
  const response = await fetch("/simulate/attack/memory", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_agent: targetAgent,
      memory_mb: 750,
      duration: 45,
    }),
  });

  const result = await response.json();
  console.log("Memory Attack Started:", result);
}
```

### **Network Attack Button**

```javascript
async function simulateNetworkAttack(targetAgent) {
  const response = await fetch("/simulate/attack/network", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_agent: targetAgent,
      packet_rate: 2000,
      duration: 30,
    }),
  });

  const result = await response.json();
  console.log("Network Attack Started:", result);
}
```

### **DDoS Attack Button**

```javascript
async function simulateDDoSAttack(targetAgent) {
  const response = await fetch("/simulate/attack/ddos", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_agent: targetAgent,
      vector: "http_flood",
      request_rate: 1000,
      duration: 60,
    }),
  });

  const result = await response.json();
  console.log("DDoS Attack Started:", result);
}
```

---

## 🛑 **Stop Attack Simulation**

```javascript
async function stopAttackSimulation(targetAgent, simulationId) {
  const response = await fetch("/simulate/attack/stop", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      target_agent: targetAgent,
      simulation_id: simulationId,
    }),
  });

  const result = await response.json();
  console.log("Attack Stopped:", result);
}
```

---

## 📊 **Get Attack History**

```javascript
async function getAttackHistory() {
  const response = await fetch("/simulate/attack/history?limit=10");
  const result = await response.json();
  console.log("Attack History:", result.simulations);
}
```

---

## 🎨 **Frontend UI Components**

### **React Component Example**

```jsx
import React, { useState, useEffect } from "react";

function AttackSimulator() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [attackTypes, setAttackTypes] = useState([]);

  useEffect(() => {
    // Load agents and attack types
    loadAgents();
    loadAttackTypes();
  }, []);

  const loadAgents = async () => {
    const response = await fetch("/agents");
    const data = await response.json();
    setAgents(data.agents);
  };

  const loadAttackTypes = async () => {
    const response = await fetch("/simulate/attack/types");
    const data = await response.json();
    setAttackTypes(data.attack_types);
  };

  const handleAttackButton = async (attackType) => {
    if (!selectedAgent) {
      alert("Please select a target agent");
      return;
    }

    const endpoint = `/simulate/attack/${attackType.id}`;
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_agent: selectedAgent,
        duration: 60,
      }),
    });

    const result = await response.json();
    alert(`${attackType.name} started on ${selectedAgent}`);
  };

  return (
    <div className="attack-simulator">
      <h2>🚨 Attack Simulator</h2>

      <div className="agent-selector">
        <label>Target Agent:</label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
        >
          <option value="">Select Agent</option>
          {agents.map((agent) => (
            <option key={agent.agent_id} value={agent.agent_id}>
              {agent.hostname} ({agent.agent_id})
            </option>
          ))}
        </select>
      </div>

      <div className="attack-buttons">
        {attackTypes.map((attackType) => (
          <button
            key={attackType.id}
            onClick={() => handleAttackButton(attackType)}
            className={`attack-btn attack-${attackType.id}`}
          >
            {attackType.name}
          </button>
        ))}
      </div>
    </div>
  );
}

export default AttackSimulator;
```

### **CSS Styles**

```css
.attack-simulator {
  padding: 20px;
  border: 2px solid #ff6b6b;
  border-radius: 8px;
  background: #fff5f5;
}

.agent-selector {
  margin-bottom: 20px;
}

.agent-selector select {
  padding: 8px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.attack-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.attack-btn {
  padding: 15px 20px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.attack-cpu_spike {
  background: #ff6b6b;
  color: white;
}

.attack-memory_exhaustion {
  background: #4ecdc4;
  color: white;
}

.attack-network_flood {
  background: #45b7d1;
  color: white;
}

.attack-ddos {
  background: #f39c12;
  color: white;
}

.attack-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.attack-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

---

## 📱 **Mobile-Friendly Buttons**

```html
<div class="mobile-attack-grid">
  <button
    onclick="simulateCPUAttack('agent-001')"
    class="mobile-attack-btn cpu"
  >
    🔥 CPU Attack
  </button>
  <button
    onclick="simulateMemoryAttack('agent-001')"
    class="mobile-attack-btn memory"
  >
    💾 Memory Attack
  </button>
  <button
    onclick="simulateNetworkAttack('agent-001')"
    class="mobile-attack-btn network"
  >
    🌊 Network Flood
  </button>
  <button
    onclick="simulateDDoSAttack('agent-001')"
    class="mobile-attack-btn ddos"
  >
    ⚡ DDoS Attack
  </button>
</div>
```

---

## 🔔 **Real-Time Updates via WebSocket**

```javascript
// Connect to WebSocket for real-time attack status
const ws = new WebSocket("ws://localhost:3001/ws/dashboard");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "attack_simulation_started") {
    console.log("Attack started:", data);
    updateAttackStatus(data.simulation_id, "running");
  }

  if (data.type === "attack_simulation_completed") {
    console.log("Attack completed:", data);
    updateAttackStatus(data.simulation_id, "completed");
  }

  if (data.type === "anomaly_detected") {
    console.log("Anomaly detected during attack:", data);
    showAnomalyAlert(data);
  }
};
```

---

## ✅ **Testing Your Integration**

1. **Start your Guardian server**:

   ```bash
   docker-compose up -d
   ```

2. **Test attack endpoint**:

   ```bash
   curl -X POST http://localhost:3001/simulate/attack/cpu \
     -H "Content-Type: application/json" \
     -d '{"target_agent": "agent-001", "cpu_percentage": 80, "duration": 30}'
   ```

3. **Check attack history**:
   ```bash
   curl http://localhost:3001/simulate/attack/history
   ```

---

**🎉 Your frontend now has complete attack simulation capabilities with these backend routes!**
