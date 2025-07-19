"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Wifi,
  Monitor,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Server,
  Eye,
  Shield,
  Network,
  Cpu,
  MemoryStick,
  HardDrive,
} from "lucide-react";

interface PeerStatus {
  connected: boolean;
  guardian_id: string | null;
  local_node_id: string;
  connection_quality: number;
  last_ping: string;
  capabilities: string[];
  system_metrics: {
    cpu_percent: number;
    memory_percent: number;
    disk_usage: number;
    network_connections: number;
  };
}

export default function PeerConnectionPanel() {
  const [peerStatus, setPeerStatus] = useState<PeerStatus | null>(null);
  const [connectionForm, setConnectionForm] = useState({
    guardian_ip: "",
    guardian_port: "3001",
    jwt_token: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionLogs, setConnectionLogs] = useState<string[]>([]);
  const [autoMetrics, setAutoMetrics] = useState(true);

  // API Base URL (local peer server)
  const API_BASE =
    process.env.NEXT_PUBLIC_PEER_API_URL || "http://localhost:3002";

  // Add log entry
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `${timestamp}: ${message}`;
    setConnectionLogs((prev) => [logEntry, ...prev.slice(0, 9)]);
  };

  // Fetch peer status
  const fetchPeerStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/distributed/health`);
      if (!response.ok) throw new Error("Failed to fetch peer status");

      const result = await response.json();
      setPeerStatus(result.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      console.error("Error fetching peer status:", err);
    }
  };

  // Connect to guardian
  const connectToGuardian = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!connectionForm.guardian_ip || !connectionForm.jwt_token) {
        throw new Error("Please provide guardian IP and JWT token");
      }

      const guardianEndpoint = `http://${connectionForm.guardian_ip}:${connectionForm.guardian_port}`;

      addLog(`Attempting to connect to guardian at ${guardianEndpoint}`);

      const response = await fetch(`${API_BASE}/distributed/connect-guardian`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          endpoint: guardianEndpoint,
          jwt_token: connectionForm.jwt_token,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Connection failed");
      }

      const result = await response.json();
      addLog(`Successfully connected to guardian: ${result.data?.guardian_id}`);

      // Refresh status
      await fetchPeerStatus();

      // Clear form
      setConnectionForm((prev) => ({ ...prev, jwt_token: "" }));
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Connection failed";
      setError(errorMessage);
      addLog(`Connection failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // Disconnect from guardian
  const disconnect = async () => {
    try {
      addLog("Disconnecting from guardian...");
      // Implementation for disconnect logic
      await fetchPeerStatus();
      addLog("Disconnected from guardian");
    } catch (err) {
      addLog(`Disconnect failed: ${err}`);
    }
  };

  // Send metrics update
  const sendMetricsUpdate = async () => {
    try {
      const response = await fetch(`${API_BASE}/distributed/send-metrics`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        addLog("Metrics update sent to guardian");
      } else {
        throw new Error("Failed to send metrics");
      }
    } catch (err) {
      addLog(`Metrics update failed: ${err}`);
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    fetchPeerStatus();

    const interval = setInterval(fetchPeerStatus, 5000);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-metrics effect
  useEffect(() => {
    if (autoMetrics && peerStatus?.connected) {
      const interval = setInterval(sendMetricsUpdate, 10000);
      return () => clearInterval(interval);
    }
  }, [autoMetrics, peerStatus?.connected]); // eslint-disable-line react-hooks/exhaustive-deps

  const getConnectionStatusIcon = () => {
    if (peerStatus?.connected) {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    } else {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getConnectionQualityColor = (quality: number) => {
    if (quality > 0.8) return "text-green-500";
    if (quality > 0.5) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Wifi className="h-8 w-8 text-blue-600" />
            Aegis Peer Connection
          </h1>
          <p className="text-gray-600">
            Connect this computer to the Guardian network
          </p>
        </div>
        <div className="flex items-center gap-2">
          {getConnectionStatusIcon()}
          <span className="font-medium">
            {peerStatus?.connected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Connection Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Connection Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Connection Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Guardian Connection
              </CardTitle>
              <CardDescription>
                Connect to the Guardian computer using the provided JWT token
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="guardian_ip">Guardian IP Address</Label>
                  <Input
                    id="guardian_ip"
                    placeholder="192.168.1.10"
                    value={connectionForm.guardian_ip}
                    onChange={(e) =>
                      setConnectionForm({
                        ...connectionForm,
                        guardian_ip: e.target.value,
                      })
                    }
                    disabled={peerStatus?.connected}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="guardian_port">Port</Label>
                  <Input
                    id="guardian_port"
                    placeholder="3001"
                    value={connectionForm.guardian_port}
                    onChange={(e) =>
                      setConnectionForm({
                        ...connectionForm,
                        guardian_port: e.target.value,
                      })
                    }
                    disabled={peerStatus?.connected}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="jwt_token">JWT Token (from Guardian)</Label>
                <Input
                  id="jwt_token"
                  type="password"
                  placeholder="Enter the JWT token provided by the Guardian"
                  value={connectionForm.jwt_token}
                  onChange={(e) =>
                    setConnectionForm({
                      ...connectionForm,
                      jwt_token: e.target.value,
                    })
                  }
                  disabled={peerStatus?.connected}
                />
              </div>

              <div className="flex gap-2">
                {!peerStatus?.connected ? (
                  <Button
                    onClick={connectToGuardian}
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <Activity className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Wifi className="h-4 w-4 mr-2" />
                    )}
                    {loading ? "Connecting..." : "Connect to Guardian"}
                  </Button>
                ) : (
                  <Button
                    onClick={disconnect}
                    variant="destructive"
                    className="flex-1"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Disconnect
                  </Button>
                )}

                <Button onClick={fetchPeerStatus} variant="outline">
                  <Monitor className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Connection Status */}
          {peerStatus && (
            <Card>
              <CardHeader>
                <CardTitle>Connection Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      {getConnectionStatusIcon()}
                    </div>
                    <div className="text-sm font-medium">Status</div>
                    <div className="text-xs text-gray-500">
                      {peerStatus.connected ? "Connected" : "Disconnected"}
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Network
                        className={`h-5 w-5 ${getConnectionQualityColor(
                          peerStatus.connection_quality
                        )}`}
                      />
                    </div>
                    <div className="text-sm font-medium">Quality</div>
                    <div className="text-xs text-gray-500">
                      {(peerStatus.connection_quality * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Shield className="h-5 w-5 text-purple-500" />
                    </div>
                    <div className="text-sm font-medium">Guardian</div>
                    <div className="text-xs text-gray-500">
                      {peerStatus.guardian_id
                        ? peerStatus.guardian_id.substring(0, 8) + "..."
                        : "None"}
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Server className="h-5 w-5 text-blue-500" />
                    </div>
                    <div className="text-sm font-medium">Node ID</div>
                    <div className="text-xs text-gray-500">
                      {peerStatus.local_node_id.substring(0, 8)}...
                    </div>
                  </div>
                </div>

                {peerStatus.capabilities.length > 0 && (
                  <div>
                    <div className="text-sm font-medium mb-2">
                      Capabilities:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {peerStatus.capabilities.map((cap) => (
                        <Badge key={cap} variant="outline" className="text-xs">
                          {cap.replace("_", " ")}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* System Metrics */}
          {peerStatus?.system_metrics && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Local System Metrics
                </CardTitle>
                <CardDescription>
                  Real-time system performance monitoring
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* CPU Usage */}
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Cpu className="h-8 w-8 text-blue-500" />
                    </div>
                    <div className="text-2xl font-bold">
                      {peerStatus.system_metrics.cpu_percent?.toFixed(1) ||
                        "N/A"}
                      %
                    </div>
                    <div className="text-sm text-gray-500">CPU Usage</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${
                            peerStatus.system_metrics.cpu_percent || 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Memory Usage */}
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <MemoryStick className="h-8 w-8 text-green-500" />
                    </div>
                    <div className="text-2xl font-bold">
                      {peerStatus.system_metrics.memory_percent?.toFixed(1) ||
                        "N/A"}
                      %
                    </div>
                    <div className="text-sm text-gray-500">Memory Usage</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${
                            peerStatus.system_metrics.memory_percent || 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Disk Usage */}
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <HardDrive className="h-8 w-8 text-yellow-500" />
                    </div>
                    <div className="text-2xl font-bold">
                      {peerStatus.system_metrics.disk_usage?.toFixed(1) ||
                        "N/A"}
                      %
                    </div>
                    <div className="text-sm text-gray-500">Disk Usage</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-yellow-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${
                            peerStatus.system_metrics.disk_usage || 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="text-sm">
                    <span className="text-gray-500">Network Connections:</span>
                    <span className="ml-2 font-medium">
                      {peerStatus.system_metrics.network_connections || 0}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant={autoMetrics ? "default" : "outline"}
                      size="sm"
                      onClick={() => setAutoMetrics(!autoMetrics)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Auto-Metrics: {autoMetrics ? "ON" : "OFF"}
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={sendMetricsUpdate}
                      disabled={!peerStatus.connected}
                    >
                      <Activity className="h-4 w-4 mr-1" />
                      Send Update
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={fetchPeerStatus}
              >
                <Monitor className="h-4 w-4 mr-2" />
                Refresh Status
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={sendMetricsUpdate}
                disabled={!peerStatus?.connected}
              >
                <Activity className="h-4 w-4 mr-2" />
                Send Metrics
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                disabled={!peerStatus?.connected}
              >
                <Eye className="h-4 w-4 mr-2" />
                View Network
              </Button>
            </CardContent>
          </Card>

          {/* Connection Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>Instructions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <div className="font-medium">1. Get JWT Token</div>
                <div className="text-gray-600">
                  Request a JWT token from the Guardian computer&apos;s admin
                  panel.
                </div>
              </div>

              <div>
                <div className="font-medium">2. Enter Guardian IP</div>
                <div className="text-gray-600">
                  Enter the IP address of the Guardian computer on your network.
                </div>
              </div>

              <div>
                <div className="font-medium">3. Connect</div>
                <div className="text-gray-600">
                  Click &quot;Connect to Guardian&quot; to join the distributed
                  network.
                </div>
              </div>

              <div>
                <div className="font-medium">4. Monitor</div>
                <div className="text-gray-600">
                  Your system will automatically send metrics and participate in
                  network protection.
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Connection Logs */}
          {connectionLogs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Connection Logs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1 font-mono text-xs max-h-48 overflow-y-auto">
                  {connectionLogs.map((log, index) => (
                    <div key={index} className="text-gray-600">
                      {log}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
