# 🚨 Aegis of Alderaan - Attack Simulation Guide

This guide shows how to simulate various attacks and observe how your Aegis protection system responds.

## 🎯 **Complete Attack Simulation Workflow**

### **Step 1: Ensure System is Running**

```powershell
# Terminal 1: Guardian Server
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\guardian-server
python start_server.py

# Terminal 2: Agent
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan\agent
python start_agent.py

# Terminal 3: Response Monitor
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
python response_monitor.py
```

### **Step 2: Start Monitoring (Terminal 3)**

```powershell
python response_monitor.py
# Choose option 2 for continuous monitoring
```

### **Step 3: Launch Attack (Terminal 4)**

```powershell
cd c:\Users\mohan\Desktop\Cisco\aegis-of-alderaan
python attack_simulator.py
```

## 🔥 **Attack Scenarios to Test (Core 4 Types)**

### **Scenario 1: High CPU Attack**

**Purpose**: Test CPU threshold detection and auto-remediation

1. Start attack simulator
2. Choose option 1 (CPU Stress Attack)
3. Set duration: 60 seconds, intensity: 95%
4. **Expected Response**:
   - Agent detects high CPU usage (>10%)
   - Anomaly logged in Guardian
   - Self-healing attempts to reduce load
   - Alert sent to Guardian server

### **Scenario 2: Memory Exhaustion**

**Purpose**: Test memory leak detection

1. Choose option 2 (Memory Leak Attack)
2. Set duration: 45 seconds, leak rate: 100 MB/sec
3. **Expected Response**:
   - Memory usage exceeds 85% threshold
   - Memory anomaly detected
   - Guardian receives memory alerts
   - System attempts garbage collection

### **Scenario 3: DDoS Simulation**

**Purpose**: Test network attack detection

1. Choose option 3 (DDoS Simulation)
2. Set duration: 30 seconds, target: 8.8.8.8
3. **Expected Response**:
   - Network traffic spikes above 100 Mbps
   - DDoS anomaly detected
   - Network flood patterns identified
   - Guardian logs attack correlation

### **Scenario 4: Network Traffic Spike**

**Purpose**: Test network traffic monitoring

1. Choose option 4 (Network Traffic Spike)
2. Set duration: 20 seconds, target: 8.8.8.8
3. **Expected Response**:
   - Network traffic exceeds baseline
   - Traffic pattern anomaly detected
   - Guardian receives network alerts
   - Traffic analysis and correlation

### **Scenario 5: Multi-Vector Attack**

**Purpose**: Test system under coordinated core attacks

1. Choose option 5 (Multi-Vector Attack)
2. Set duration: 90 seconds
3. **Expected Response**:
   - CPU, Memory, and Network anomalies detected simultaneously
   - Guardian correlates attack patterns
   - Priority-based remediation
   - Network-wide alert coordination

## 📊 **What to Watch For**

### **In Agent Logs** (`Terminal 2`):

```
✅ High CPU detected: 95.2% (threshold: 80%)
🔧 Attempting CPU optimization...
📊 Memory usage spike: 87.1% (threshold: 85%)
🚨 Anomaly detected: CPU_SPIKE
📤 Sending alert to Guardian...
```

### **In Guardian Logs** (`Terminal 1`):

```
📨 Received anomaly from agent-001: CPU_SPIKE
🧠 Analyzing attack pattern...
📋 Remediation plan generated
🎯 Sending commands to agent-001
💾 Storing incident in database
```

### **In Response Monitor** (`Terminal 3`):

```
📊 Active Agents: 1
   🤖 agent-001 - UNDER_ATTACK
📈 Latest Metrics:
   CPU: 95.2%
   Memory: 87.1%
   Disk: 45.3%
🚨 Recent Anomalies: 3
   ⚠️  [2025-07-17T12:00:15] HIGH: CPU usage anomaly detected
```

## 🛡️ **Expected System Behaviors**

### **Expected System Behaviors (Core 4 Types)**

### **Anomaly Detection:**

- CPU >10% → CPU_SPIKE anomaly (lowered for testing)
- Memory >85% → MEMORY_LEAK anomaly
- Network >100Mbps → DDOS_ATTEMPT anomaly
- Network traffic spikes → NETWORK_ANOMALY

### **Self-Healing Actions:**

- High CPU → Process priority adjustment
- Memory leak → Garbage collection trigger
- DDoS attack → Rate limiting and traffic analysis
- Network spikes → Connection monitoring

### **Guardian Coordination:**

- Real-time anomaly aggregation
- Pattern correlation across agents
- Centralized remediation planning
- Historical attack tracking

## 🔍 **Testing Scenarios**

### **Quick Test (5 minutes):**

1. Start CPU attack (30 seconds, 50%)
2. Watch agent detect and respond
3. Verify Guardian receives alerts
4. Check database storage

### **Comprehensive Test (15 minutes):**

1. Core multi-vector attack (90 seconds)
2. Monitor all system responses
3. Verify remediation effectiveness
4. Check Neo4j network topology updates

### **Endurance Test (30 minutes):**

1. Sequential core attacks (CPU → Memory → DDoS)
2. Test long-term pattern detection
3. Verify system stability
4. Check MongoDB metrics storage

## 🚀 **Advanced Testing**

### **Multiple Agents:**

1. Start multiple agents (different machines/VMs)
2. Launch coordinated attacks
3. Test network-wide correlation
4. Verify distributed response

### **Custom Attacks:**

Edit `attack_simulator.py` to create:

- Advanced CPU stress patterns
- Memory consumption algorithms
- Custom DDoS simulations
- Network traffic analysis attacks

## 📈 **Success Metrics**

### **Success Metrics (Core 4 Types)**

### **Detection Speed:**

- CPU anomaly detection: <5 seconds (10% threshold)
- Memory anomaly detection: <10 seconds
- DDoS detection: <15 seconds
- Network spike detection: <5 seconds

### **Response Effectiveness:**

- CPU normalized: <30 seconds
- Memory freed: <45 seconds
- Network patterns analyzed: <20 seconds
- Alerts propagated: <5 seconds

### **System Resilience:**

- No false positives for core types
- Minimal performance impact
- Graceful degradation under attack
- Rapid recovery and baseline restoration

---

## 🎮 **Ready to Start?**

1. **Open 4 terminals** as described above
2. **Start with Scenario 1** (CPU attack - now detects at 10%)
3. **Observe the responses** in all terminals
4. **Try core attack types** (CPU, Memory, DDoS, Network)
5. **Check the database** for stored metrics and anomalies

Your Aegis of Alderaan system should demonstrate real-time threat detection for the 4 core anomaly types, coordinated response, and resilient recovery! 🛡️
