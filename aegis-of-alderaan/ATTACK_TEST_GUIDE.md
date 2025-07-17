# 🎯 Quick Attack Detection Test Guide

## Current Issue Analysis

The attack simulator wasn't properly detected because:

1. ✅ **FIXED**: CPU detection threshold was too high (95% → 80%)
2. ✅ **FIXED**: Anomaly detector wasn't analyzing metrics actively
3. ✅ **FIXED**: Attack simulator wasn't generating sufficient load
4. ✅ **FIXED**: Missing connection between metrics collector and anomaly detector

## 🚀 Quick Test Steps

### **Step 1: Start Guardian Server (Terminal 1)**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\guardian-server
python start_server.py
```

_Wait for: "Guardian server is running on http://localhost:3001"_

### **Step 2: Start Agent (Terminal 2)**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent
python start_agent.py
```

_Wait for: "🤖 Agent started successfully" and "✅ Connected to Guardian server"_

### **Step 3: Start Response Monitor (Terminal 3)**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
python response_monitor.py
# Choose option 2 for continuous monitoring
```

_Should show: "📊 Active Agents: 1" or "📊 Active Agents: 2"_

### **Step 4: Launch Attack (Terminal 4)**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
python simple_cpu_attack.py
```

## 🔍 **What You Should See**

### **In Agent Terminal (Terminal 2):**

```
🔍 Starting anomaly detection
🚨 ANOMALY DETECTED: CPU_SPIKE - High CPU usage detected: 85.2%
📤 Sending alert to Guardian...
🔧 Attempting CPU optimization...
```

### **In Guardian Terminal (Terminal 1):**

```
📨 Received anomaly from agent-001: CPU_SPIKE
💾 Storing anomaly in database
🧠 Analyzing attack pattern...
```

### **In Response Monitor (Terminal 3):**

```
📊 Active Agents: 1
   🤖 agent-001 - active
📈 Latest Metrics (agent-001):
   CPU: 85.2%
   Memory: 45.1%
   Disk: 32.1%
🚨 Recent Anomalies: 1
   ⚠️  [2025-07-17T12:25:30] HIGH: CPU usage anomaly detected
```

### **In Attack Terminal (Terminal 4):**

```
🔥 STARTING AGGRESSIVE CPU ATTACK FOR 15 SECONDS
⏰  1s - CPU:  85.1% | Memory:  45.1%
🚨 HIGH CPU DETECTED: 85.1% (Threshold: 80%)
⏰  2s - CPU:  89.3% | Memory:  45.2%
🚨 HIGH CPU DETECTED: 89.3% (Threshold: 80%)
```

## 🛠️ **If Still Not Working**

### **Check Agent Logs:**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent
type agent.log
```

### **Check Guardian Logs:**

Check Terminal 1 for any error messages

### **Test Raw Attack Simulator:**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
python attack_simulator.py
# Choose option 1 (CPU Stress Attack)
# Set duration: 30, intensity: 95
```

## 🎯 **Key Improvements Made**

1. **Lowered CPU Detection Threshold**: 95% → 80%
2. **Active Anomaly Analysis**: Now analyzes metrics every 5 seconds
3. **Improved Attack Generator**: More aggressive CPU load
4. **Better Logging**: Clear anomaly detection messages
5. **Connected Components**: Anomaly detector now gets metrics

## 📊 **Expected Behavior**

- **Detection Time**: < 10 seconds after attack starts
- **CPU Threshold**: 80% triggers anomaly
- **Memory Threshold**: 85% triggers anomaly
- **Alert Propagation**: < 5 seconds to Guardian
- **Monitoring**: Real-time updates in response monitor

Your system should now properly detect and respond to attacks! 🛡️
