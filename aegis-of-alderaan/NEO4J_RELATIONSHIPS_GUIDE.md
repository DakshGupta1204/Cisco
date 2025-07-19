# Neo4j Relationships and Self-Healing Guide

## Overview

The Aegis of Alderaan system now includes comprehensive **Neo4j graph database integration** for modeling agent relationships, coordinating self-healing processes, and implementing agent mirroring capabilities.

## New Features

### 🔗 Graph Database Relationships

#### 1. Mirror Relationships

- **Bidirectional mirroring** between primary and backup agents
- **Priority-based** mirror selection
- **Active/Passive/Backup** mirror types
- **Automatic failover** capabilities

#### 2. Monitoring Relationships

- Agent-to-agent **health monitoring**
- **Distributed monitoring** topology
- **Cross-agent supervision**

#### 3. Network Connections

- **Topology mapping** of agent communications
- **Connection type classification** (CONNECTED_TO, COMMUNICATES_WITH, etc.)
- **Network path discovery**

### 🩺 Self-Healing Coordination

#### 1. Health Issue Tracking

- **Centralized health issue** registration
- **Severity classification** (low, medium, high, critical)
- **Issue type categorization** (CPU, memory, network, etc.)

#### 2. Healing Process Management

- **Automatic mirror selection** for healing
- **Healing process tracking** with unique IDs
- **Success/failure reporting**
- **Healing coordination** between agents

#### 3. Mirror Activation

- **Seamless takeover** by mirror agents
- **Status synchronization** across the network
- **Role transition** management

## API Endpoints

### Relationship Management

#### Create Mirror Relationship

```http
POST /agents/{agent_id}/relationships/mirror
Content-Type: application/json

{
  "mirror_agent": "agent_002"
}
```

#### Create Monitoring Relationship

```http
POST /agents/{agent_id}/relationships/monitor
Content-Type: application/json

{
  "target_agent": "agent_003"
}
```

#### Create Network Connection

```http
POST /agents/{agent_id}/relationships/connect
Content-Type: application/json

{
  "target_agent": "agent_004",
  "connection_type": "COMMUNICATES_WITH"
}
```

### Mirroring Operations

#### Get Agent Mirrors

```http
GET /agents/{agent_id}/mirrors
```

#### Setup Comprehensive Mirroring

```http
POST /agents/{agent_id}/mirror/setup
Content-Type: application/json

{
  "mirrors": [
    {
      "agent_id": "agent_002",
      "type": "active",
      "priority": 1
    },
    {
      "agent_id": "agent_003",
      "type": "backup",
      "priority": 2
    }
  ]
}
```

#### Activate Mirror Agent

```http
POST /agents/{agent_id}/mirror/activate
Content-Type: application/json

{
  "mirror_agent": "agent_002"
}
```

### Self-Healing Operations

#### Initiate Self-Healing

```http
POST /agents/{agent_id}/healing/initiate
Content-Type: application/json

{
  "issue_type": "high_cpu_usage",
  "severity": "critical",
  "details": {
    "cpu_percent": 95,
    "duration": 300
  }
}
```

#### Get Active Healing Processes

```http
GET /healing/active
```

#### Complete Healing Process

```http
POST /healing/{healing_id}/complete
Content-Type: application/json

{
  "success": true,
  "details": "Healing completed successfully"
}
```

### Topology Visualization

#### Get Network Topology

```http
GET /network/topology
```

#### Get Mirror Topology

```http
GET /network/mirror-topology
```

## Agent Message Handling

### New Message Types

#### 1. Healing Request

```json
{
  "type": "healing_request",
  "failed_agent": "agent_001",
  "healing_id": "heal_123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 2. Mirror Setup

```json
{
  "type": "mirror_setup",
  "primary_agent": "agent_001",
  "mirror_config": {
    "type": "active",
    "priority": 1
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 3. Mirror Activation

```json
{
  "type": "mirror_activation",
  "primary_agent": "agent_001",
  "role": "active_mirror",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 4. Mirror Takeover

```json
{
  "type": "mirror_takeover",
  "mirror_agent": "agent_002",
  "status": "inactive",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Usage Examples

### 1. Setting Up Basic Mirroring

```python
# Create mirror relationship
await create_mirror_relationship("primary_agent", "backup_agent")

# Setup comprehensive mirroring
mirror_configs = [
    {"agent_id": "backup_1", "type": "active", "priority": 1},
    {"agent_id": "backup_2", "type": "passive", "priority": 2}
]
await setup_agent_mirroring("primary_agent", mirror_configs)
```

### 2. Initiating Self-Healing

```python
# Register health issue and initiate healing
healing_config = {
    "issue_type": "memory_leak",
    "severity": "high",
    "details": {"memory_usage": "90%"}
}
result = await initiate_self_healing("failing_agent", healing_config)
print(f"Healing ID: {result['healing_id']}")
```

### 3. Building Monitoring Network

```python
# Create monitoring relationships
await create_monitoring_relationship("monitor_1", "server_1")
await create_monitoring_relationship("monitor_1", "server_2")
await create_monitoring_relationship("monitor_2", "server_3")

# Create network connections
await create_network_connection("server_1", "server_2", "BACKUP_CONNECTION")
await create_network_connection("monitor_1", "monitor_2", "COMMUNICATES_WITH")
```

## Testing and Validation

### Quick Test Script

```bash
# Run quick demo
python test_neo4j_relationships.py --quick

# Run comprehensive test suite
python test_neo4j_relationships.py

# Launch with interactive demo
python launch_neo4j_features.py --demo
```

### Test Coverage

✅ **Mirror Relationships**

- Bidirectional mirror creation
- Priority-based selection
- Mirror activation/deactivation

✅ **Monitoring Relationships**

- Cross-agent monitoring setup
- Health check coordination
- Status propagation

✅ **Network Connections**

- Topology mapping
- Connection type management
- Path discovery

✅ **Self-Healing**

- Issue registration
- Healing coordination
- Process tracking
- Success/failure reporting

✅ **Agent Mirroring**

- Comprehensive mirror setup
- Role transitions
- Redundancy management

## Database Schema

### Neo4j Node Types

#### Agent Nodes

```cypher
(:Agent {
  agent_id: string,
  hostname: string,
  role: string,
  status: string,
  last_updated: timestamp
})
```

#### Health Issue Nodes

```cypher
(:HealthIssue {
  issue_id: string,
  agent_id: string,
  issue_type: string,
  severity: string,
  status: string,
  details: string,
  created_at: timestamp
})
```

#### Healing Process Nodes

```cypher
(:HealingProcess {
  healing_id: string,
  failed_agent: string,
  healing_agent: string,
  status: string,
  started_at: timestamp,
  completed_at: timestamp
})
```

### Relationship Types

- **HAS_MIRROR** - Primary to mirror agent
- **IS_MIRROR_OF** - Mirror to primary agent
- **MONITORS** - Monitoring relationship
- **CONNECTED_TO** - Network connection
- **COMMUNICATES_WITH** - Communication link
- **HEALING** - Active healing relationship
- **TOOK_OVER** - Takeover relationship
- **HAS_ISSUE** - Health issue relationship

## Configuration

### Environment Variables

```bash
# Neo4j Cloud Connection (Aura)
NEO4J_URI=neo4j+s://your-database-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### Guardian Configuration

The Guardian server automatically connects to Neo4j on startup and creates necessary constraints and indexes.

## Benefits

### 🎯 **Enhanced Resilience**

- **Automatic failover** with mirror agents
- **Distributed healing** coordination
- **Network-aware** recovery strategies

### 📊 **Topology Awareness**

- **Real-time network** visualization
- **Relationship mapping** for optimization
- **Path discovery** for efficient communication

### 🔄 **Self-Healing Automation**

- **Proactive issue** detection
- **Coordinated recovery** processes
- **Success tracking** and reporting

### 🪞 **Advanced Mirroring**

- **Multi-tier backup** strategies
- **Priority-based** failover
- **Seamless role** transitions

## Next Steps

1. **Dashboard Integration** - Visualize relationships in web dashboard
2. **ML-Based Healing** - Machine learning for optimal healing strategies
3. **Geographic Distribution** - Location-aware mirroring
4. **Performance Optimization** - Relationship-based load balancing
5. **Security Integration** - Trust relationships and access control

---

**🛡️ Aegis of Alderaan - Protecting your network with intelligent graph-based relationships and coordinated self-healing capabilities.**
