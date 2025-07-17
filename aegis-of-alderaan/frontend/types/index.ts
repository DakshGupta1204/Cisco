// Core data types matching the API specification
// Represents the 5 AI software programs running on each device
export interface Agent {
  id: string;
  name: 'CPU Monitor' | 'Memory Monitor' | 'Network Analyzer' | 'Malware Scanner' | 'Firewall Daemon';
  status: 'running' | 'stopped' | 'error';
  lastHeartbeat: Date;
}

// Represents a physical or virtual machine in the network
export interface Device {
  id:string;
  hostname: string;
  ipAddress: string;
  type: 'web_server' | 'database' | 'load_balancer' | 'iot_device' | 'computer';
  status: 'healthy' | 'warning' | 'under_attack' | 'quarantined' | 'healing';
  location: {
    datacenter: string;
    rack: string;
    coordinates: { x: number; y: number };
  };
  metrics: {
    cpu: number;
    memory: number;
    network: number;
    connections: number;
    uptime: number;
  };
  security: {
    threatsBlocked: number;
    lastScan: Date;
    vulnerabilities: number;
  };
  lastSeen: Date;
  version: string;
  agents: Agent[]; // Each device has multiple software agents
}

export interface Threat {
  id: string;
  type: 'ddos' | 'malware' | 'intrusion' | 'anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  affectedDevices: string[]; // Changed from affectedAgents
  sourceIP?: string;
  status: 'detected' | 'analyzing' | 'responding' | 'resolved';
  responseTime: number; // milliseconds
  aiAnalysis: {
    explanation: string;
    confidence: number;
    recommendedActions: string[];
    riskAssessment: string;
  };
  responseActions: ResponseAction[];
}

export interface ResponseAction {
  id: string;
  type: 'block_ip' | 'quarantine_device' | 'failover' | 'heal' | 'scan'; // Changed from quarantine_agent
  timestamp: Date;
  deviceId: string; // Changed from agentId
  status: 'initiated' | 'in_progress' | 'completed' | 'failed';
  details: string;
}

export interface NetworkEdge {
  from: string;
  to: string;
  type: 'normal' | 'attack' | 'response' | 'healing';
  bandwidth: number;
  latency: number;
}

export interface NetworkMetrics {
  timestamp: Date;
  deviceId?: string; // Changed from agentId
  cpu: number;
  memory: number;
  network: number;
  connections: number;
  uptime?: number;
  responseTime?: number;
}

export interface SystemStatus {
  status: 'secure' | 'warning' | 'under_attack' | 'responding' | 'healing';
  serviceAvailability: number; // percentage
  totalDevices: number; // Changed from totalAgents
  healthyDevices: number; // Changed from healthyAgents
  activeThreats: number;
  avgResponseTime: number;
  autoRecoveryActive: boolean;
  aiProtectionActive: boolean;
  threatsBlocked: number;
}

export interface ConnectionStatus {
  status: 'connected' | 'disconnected' | 'reconnecting';
  lastUpdate: Date;
  serverHealth: number;
}

export interface DashboardState {
  activeView: 'network' | 'metrics' | 'threats' | 'devices' | 'demo'; // Changed from 'agents'
  connectionStatus: ConnectionStatus;
  systemStatus: SystemStatus;
  devices: Device[]; // Changed from agents: Agent[]
  threats: Threat[];
  metrics: NetworkMetrics[];
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  duration: number; // seconds
  type: 'ddos' | 'malware' | 'intrusion';
  steps: DemoStep[];
}

export interface DemoStep {
  time: number; // seconds from start
  action: string;
  type: 'normal' | 'attack' | 'detection' | 'response' | 'recovery';
}

export interface WebSocketMessage {
  type: 'agent_update' | 'threat_detected' | 'response_action' | 'system_status' | 'metrics_update';
  data: any;
  timestamp: Date;
}
