// lib/peer-api.ts
import {
  PeerRegistrationInfo,
  PeerMetrics
} from "../types";
import { apiService } from "./api";

interface RegistrationResponse {
    status: string;
    node_id: string;
    guardian_id: string;
    network_topology: any;
    assigned_capabilities: string[];
    connection_endpoints: any;
}

interface HeartbeatResponse {
    status: string;
}

interface MetricsResponse {
    status: string;
}

class PeerApiService {
  private guardianUrl: string;

  constructor() {
    this.guardianUrl = process.env.NEXT_PUBLIC_GUARDIAN_API_URL || "http://localhost:8000";
  }

  async registerWithGuardian(
    registrationInfo: PeerRegistrationInfo
  ): Promise<RegistrationResponse> {
    return apiService.post(
      `${this.guardianUrl}/distributed/register`,
      registrationInfo
    );
  }

  async sendHeartbeat(nodeId: string): Promise<HeartbeatResponse> {
    return apiService.post(`${this.guardianUrl}/distributed/heartbeat/${nodeId}`, {});
  }

  async sendMetrics(nodeId: string, metrics: PeerMetrics): Promise<MetricsResponse> {
    return apiService.post(`${this.guardianUrl}/distributed/metrics/${nodeId}`, {
      metrics,
    });
  }
}

export const peerApiService = new PeerApiService();
