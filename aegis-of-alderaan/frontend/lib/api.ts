import { Device, Threat, NetworkMetrics } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/dashboard';

class ApiService {
  private static instance: ApiService;
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  // HTTP API Methods
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }

  // Device APIs
  async getDevices(): Promise<Device[]> {
    return this.request('/devices');
  }

  async getDevice(deviceId: string): Promise<Device> {
    return this.request(`/devices/${deviceId}`);
  }

  async getDeviceMetrics(deviceId: string, timeRange?: string): Promise<NetworkMetrics[]> {
    const query = timeRange ? `?timeRange=${timeRange}` : '';
    return this.request(`/devices/${deviceId}/metrics${query}`);
  }

  async sendDeviceCommand(deviceId: string, command: string): Promise<{ success: boolean }> {
    return this.request(`/devices/${deviceId}/command`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    });
  }

  // Threat APIs
  async getThreats(limit?: number): Promise<Threat[]> {
    const query = limit ? `?limit=${limit}` : '';
    return this.request(`/threats${query}`);
  }

  async getAnomalies(): Promise<any[]> {
    return this.request('/anomalies');
  }

  // Network APIs
  async getNetworkTopology(): Promise<{ nodes: Device[]; edges: any[] }> {
    return this.request('/network/topology');
  }

  // Demo APIs
  async triggerAttack(type: 'ddos' | 'malware' | 'intrusion' = 'ddos'): Promise<{ success: boolean }> {
    return this.request('/simulate/attack', {
      method: 'POST',
      body: JSON.stringify({ type }),
    });
  }

  async resetDemo(): Promise<{ success: boolean }> {
    return this.request('/demo/reset', {
      method: 'POST',
    });
  }

  // WebSocket Connection Management
  connectWebSocket(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.notifyListeners('connection', { status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.notifyListeners(message.type, message.data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.notifyListeners('connection', { status: 'disconnected' });
        // Auto-reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyListeners('connection', { status: 'error', error });
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      // Retry connection after 5 seconds
      setTimeout(() => this.connectWebSocket(), 5000);
    }
  }

  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Event Listener Management
  subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.listeners.delete(eventType);
        }
      }
    };
  }

  private notifyListeners(eventType: string, data: any): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket listener for ${eventType}:`, error);
        }
      });
    }
  }

  // Utility method to check connection status
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'disconnecting';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }
}

export default ApiService;
export const apiService = ApiService.getInstance();
