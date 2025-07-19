// types/index.ts

// Represents the metrics for a single peer node
export interface PeerMetrics {
  cpu_usage: number;
  memory_usage: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
  };
  disk_io: {
    read_bytes: number;
    write_bytes: number;
  };
  active_connections: number;
  threats_detected: number;
}

// Represents the status and information of a single peer
export interface PeerInfo {
  node_id: string;
  address: string;
  status: "healthy" | "unhealthy" | "disconnected" | "healing";
  last_heartbeat: string; // ISO 8601 date string
  metrics: PeerMetrics;
  role: "peer";
}

// The overall status of the distributed network, as seen by the Guardian
export interface NetworkStatus {
  node_id: string;
  role: "guardian";
  connected_peers: number;
  healthy_peers: number;
  last_updated: string; // ISO 8601 date string
  peers: {
    [key: string]: PeerInfo; // Dictionary of peers, keyed by node_id
  };
}

export interface ConnectionEndpoints {
  guardian_websocket: string;
  peer_websocket: string;
  metrics_endpoint: string;
  health_endpoint: string;
}

export interface NetworkTopology {
    guardian: PeerInfo | null;
    peers: PeerInfo[];
    connections: Record<string, string[]>;
    total_nodes: number;
}

// Payload for simulating an attack on a target agent
export interface AttackSimulationPayload {
  attack_type: "cpu_spike" | "memory_leak" | "network_flood";
  target_agent: string;
  params: {
    duration_seconds?: number;
    intensity?: "low" | "medium" | "high";
    port?: number;
  };
}

// Represents a healing strategy suggested by the AI
export interface HealingStrategy {
  strategy: 'restart_service' | 'isolate_node' | 'reallocate_resources' | 'patch_vulnerability';
  confidence: number;
  estimated_time_seconds: number;
  details: string;
}

// Information used by a peer to register with the Guardian
export interface PeerRegistrationInfo {
  node_id: string;
  address: string; // e.g., "http://192.168.1.101:8080"
  role: "peer";
  jwt_token: string; // The token identifying the peer
}

// API Response Types
export interface AIAnalysisResponse {
  status: "analysis_started" | "analysis_failed";
  agent_id: string;
  details?: string;
}

export interface HealingResponse {
  status: "healing_coordinated" | "healing_failed";
  details: string;
}

export interface AttackResponse {
  status: "attack_simulated" | "simulation_failed";
  details: string;
}

// WebSocket Message Types
export type WebSocketEvent = "connection" | "network_update";

export interface ConnectionMessage {
  status: "connected" | "disconnected" | "error";
  error?: Error;
}

export type ListenerCallback = (
  data: NetworkStatus | ConnectionMessage
) => void;
