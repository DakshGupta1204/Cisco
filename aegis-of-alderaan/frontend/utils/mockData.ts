import { Device, Threat, NetworkMetrics, ResponseAction, Agent } from '../types';

const generateSoftwareAgents = (): Agent[] => {
  const agentNames = ['CPU Monitor', 'Memory Monitor', 'Network Analyzer', 'Malware Scanner', 'Firewall Daemon'] as const;
  return agentNames.map((name, i) => ({
    id: `agent_sw_${i + 1}`,
    name,
    status: Math.random() > 0.1 ? 'running' : 'error',
    lastHeartbeat: new Date(Date.now() - Math.random() * 10000),
  }));
};

export function generateMockDevices(): Device[] {
  const deviceTypes = ['web_server', 'database', 'load_balancer', 'iot_device', 'computer'] as const;
  const statuses = ['healthy', 'warning', 'under_attack', 'quarantined', 'healing'] as const;
  const datacenters = ['DC-East-1', 'DC-West-1', 'DC-Central-1'];
  
  return Array.from({ length: 8 }, (_, i) => {
    const deviceType = deviceTypes[i % deviceTypes.length];
    const status = i === 1 ? 'under_attack' : i === 2 ? 'warning' : 'healthy';
    
    return {
      id: `device_${i + 1}`,
      hostname: `${deviceType.replace('_', '-')}-${i + 1}`,
      ipAddress: `10.0.${Math.floor(i / 4)}.${i % 4 + 1}`,
      type: deviceType,
      status,
      location: {
        datacenter: datacenters[i % datacenters.length],
        rack: `Rack-${Math.floor(i / 3) + 1}`,
        coordinates: {
          x: (i % 4) * 200 + 100,
          y: Math.floor(i / 4) * 150 + 100
        }
      },
      metrics: {
        cpu: status === 'under_attack' ? 85 + Math.random() * 10 : Math.random() * 70,
        memory: status === 'under_attack' ? 80 + Math.random() * 15 : Math.random() * 75,
        network: status === 'under_attack' ? 90 + Math.random() * 10 : Math.random() * 60,
        connections: Math.floor(Math.random() * 1000) + 100,
        uptime: Math.floor(Math.random() * 8760) + 24 // 1-365 days in hours
      },
      security: {
        threatsBlocked: Math.floor(Math.random() * 50),
        lastScan: new Date(Date.now() - Math.random() * 86400000), // Last 24 hours
        vulnerabilities: Math.floor(Math.random() * 3)
      },
      lastSeen: new Date(),
      version: `v2.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
      agents: generateSoftwareAgents(),
    };
  });
}

export function generateMockThreats(): Threat[] {
  const threatTypes = ['ddos', 'malware', 'intrusion', 'anomaly'] as const;
  const severities = ['low', 'medium', 'high', 'critical'] as const;
  const statuses = ['detected', 'analyzing', 'responding', 'resolved'] as const;
  
  const mockActions: ResponseAction[] = [
    {
      id: 'action_1',
      type: 'block_ip',
      timestamp: new Date(Date.now() - 5000),
      deviceId: 'device_1',
      status: 'completed',
      details: 'Blocked malicious IP 192.168.1.100'
    },
    {
      id: 'action_2',
      type: 'failover',
      timestamp: new Date(Date.now() - 3000),
      deviceId: 'device_2',
      status: 'in_progress',
      details: 'Failing over traffic to backup servers'
    }
  ];

  return Array.from({ length: 15 }, (_, i) => {
    const threatType = threatTypes[i % threatTypes.length];
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const status = i < 2 ? 'responding' : i < 5 ? 'resolved' : 'detected';
    
    return {
      id: `threat_${i + 1}`,
      type: threatType,
      severity,
      timestamp: new Date(Date.now() - (i * 300000) - Math.random() * 300000), // Spread over last few hours
      affectedDevices: [`device_${Math.floor(Math.random() * 8) + 1}`],
      sourceIP: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      status,
      responseTime: Math.floor(Math.random() * 10000) + 1000, // 1-11 seconds
      aiAnalysis: {
        explanation: generateThreatExplanation(threatType, severity),
        confidence: 75 + Math.random() * 25, // 75-100%
        recommendedActions: generateRecommendedActions(threatType),
        riskAssessment: generateRiskAssessment(severity)
      },
      responseActions: i < 2 ? mockActions : []
    };
  });
}

export function generateMockMetrics(): NetworkMetrics[] {
  const now = new Date();
  return Array.from({ length: 60 }, (_, i) => ({
    timestamp: new Date(now.getTime() - (59 - i) * 60000), // Last 60 minutes
    deviceId: `device_${Math.floor(Math.random() * 8) + 1}`,
    cpu: 20 + Math.random() * 60,
    memory: 30 + Math.random() * 50,
    network: 10 + Math.random() * 80,
    connections: Math.floor(Math.random() * 500) + 100,
    responseTime: Math.random() * 100 + 10
  }));
}

function generateThreatExplanation(type: string, severity: string): string {
  const explanations = {
    ddos: [
      "Coordinated attack from multiple IP addresses attempting to overwhelm server resources",
      "High volume of requests detected from suspicious sources",
      "Traffic patterns indicate distributed denial of service attack"
    ],
    malware: [
      "Suspicious process detected with characteristics of cryptocurrency mining malware",
      "Unknown executable attempting to modify system files",
      "Process behavior matches known malware signatures"
    ],
    intrusion: [
      "Unauthorized access attempt detected on admin endpoints",
      "Multiple failed authentication attempts from single source",
      "Suspicious login patterns indicating potential breach attempt"
    ],
    anomaly: [
      "Unusual network traffic patterns detected",
      "Abnormal system resource usage identified",
      "Irregular user behavior patterns observed"
    ]
  };
  
  const typeExplanations = explanations[type as keyof typeof explanations];
  return typeExplanations[Math.floor(Math.random() * typeExplanations.length)];
}

function generateRecommendedActions(type: string): string[] {
  const actions = {
    ddos: [
      "Enable rate limiting on affected endpoints",
      "Activate DDoS protection mechanisms",
      "Redirect traffic through load balancers",
      "Monitor server resources closely"
    ],
    malware: [
      "Quarantine affected system immediately",
      "Run full system scan",
      "Check for lateral movement",
      "Update antivirus signatures"
    ],
    intrusion: [
      "Lock affected user accounts",
      "Review access logs",
      "Enable two-factor authentication",
      "Monitor for privilege escalation"
    ],
    anomaly: [
      "Investigate traffic sources",
      "Review system configurations",
      "Monitor user activities",
      "Check for data exfiltration"
    ]
  };
  
  return actions[type as keyof typeof actions] || ["Monitor situation", "Take preventive measures"];
}

function generateRiskAssessment(severity: string): string {
  const assessments = {
    low: "Minimal impact expected. Standard monitoring protocols sufficient.",
    medium: "Moderate risk to system integrity. Enhanced monitoring recommended.",
    high: "Significant threat to operations. Immediate attention required.",
    critical: "Severe risk to business continuity. Emergency response protocols activated."
  };
  
  return assessments[severity as keyof typeof assessments];
}
