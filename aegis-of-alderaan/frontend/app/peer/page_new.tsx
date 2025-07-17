"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  Wifi,
  Server,
  Activity,
  AlertTriangle,
  RefreshCw,
  Network,
  Brain,
  Connect,
  Disconnect,
  Settings,
  Monitor,
  Cpu,
  MemoryStick,
  HardDrive,
} from "lucide-react";

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
  };
}

interface ConnectionStatus {
  connected: boolean;
  guardian_host: string;
  guardian_port: number;
  node_id: string;
  last_heartbeat: string | null;
  health_status: string;
}

export default function PeerPage() {
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(
    null
  );
  const [guardianHost, setGuardianHost] = useState("localhost");
  const [guardianPort, setGuardianPort] = useState(3001);
  const [isLoading, setIsLoading] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Fetch initial status
    const fetchStatus = async () => {
      try {
        const response = await fetch("http://localhost:3002/peer/status");
        if (response.ok) {
          const data = await response.json();
          setConnectionStatus(data.connection);
          setSystemMetrics(data.metrics);
        }
      } catch (error) {
        console.error("Error fetching peer status:", error);
      } finally {
        setIsLoading(false);
      }
    };

    // Connect to peer WebSocket for real-time updates
    const connectWebSocket = () => {
      const websocket = new WebSocket("ws://localhost:3002/ws/peer");

      websocket.onopen = () => {
        console.log("Connected to Peer WebSocket");
        setWs(websocket);
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "metrics_update") {
          setSystemMetrics(data.metrics);
        } else if (data.type === "connection_status") {
          setConnectionStatus(data.status);
        }
      };

      websocket.onclose = () => {
        console.log("Peer WebSocket disconnected");
        setWs(null);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        console.error("Peer WebSocket error:", error);
      };
    };

    fetchStatus();
    connectWebSocket();

    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);

    return () => {
      clearInterval(interval);
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const handleConnectToGuardian = async () => {
    setIsConnecting(true);
    try {
      const response = await fetch("http://localhost:3002/peer/connect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          guardian_host: guardianHost,
          guardian_port: guardianPort,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setConnectionStatus(result.connection);
        console.log("Connected to Guardian successfully");
      } else {
        console.error("Failed to connect to Guardian");
      }
    } catch (error) {
      console.error("Error connecting to Guardian:", error);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnectFromGuardian = async () => {
    try {
      const response = await fetch("http://localhost:3002/peer/disconnect", {
        method: "POST",
      });

      if (response.ok) {
        setConnectionStatus((prev) =>
          prev ? { ...prev, connected: false } : null
        );
        console.log("Disconnected from Guardian");
      }
    } catch (error) {
      console.error("Error disconnecting from Guardian:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-blue-300">Loading Peer Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-blue-800/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Server className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold">Aegis Peer Node</h1>
                <p className="text-blue-300 text-sm">
                  Distributed Network Participant
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div
                className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                  connectionStatus?.connected
                    ? "bg-green-900/50 text-green-300"
                    : "bg-red-900/50 text-red-300"
                }`}
              >
                <Network className="h-4 w-4" />
                <span className="text-sm">
                  {connectionStatus?.connected
                    ? "Connected to Guardian"
                    : "Disconnected"}
                </span>
              </div>
              <div className="text-sm text-blue-300">
                Node ID: {connectionStatus?.node_id || "Not assigned"}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Connection Management */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Guardian Connection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
          >
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Connect className="h-5 w-5 mr-2" />
              Guardian Connection
            </h2>

            {!connectionStatus?.connected ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">
                      Guardian Host
                    </label>
                    <input
                      type="text"
                      value={guardianHost}
                      onChange={(e) => setGuardianHost(e.target.value)}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                      placeholder="localhost"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">
                      Guardian Port
                    </label>
                    <input
                      type="number"
                      value={guardianPort}
                      onChange={(e) => setGuardianPort(Number(e.target.value))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                      placeholder="3001"
                    />
                  </div>
                </div>

                <button
                  onClick={handleConnectToGuardian}
                  disabled={isConnecting}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg px-4 py-3 font-medium transition-colors flex items-center justify-center space-x-2"
                >
                  {isConnecting ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <>
                      <Connect className="h-4 w-4" />
                      <span>Connect to Guardian</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-900/30 border border-green-600/50 rounded-lg">
                  <div>
                    <p className="font-medium">Connected to Guardian</p>
                    <p className="text-sm text-green-300">
                      {connectionStatus.guardian_host}:
                      {connectionStatus.guardian_port}
                    </p>
                  </div>
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Health Status</p>
                    <p className="capitalize">
                      {connectionStatus.health_status}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400">Last Heartbeat</p>
                    <p>
                      {connectionStatus.last_heartbeat
                        ? new Date(
                            connectionStatus.last_heartbeat
                          ).toLocaleTimeString()
                        : "Never"}
                    </p>
                  </div>
                </div>

                <button
                  onClick={handleDisconnectFromGuardian}
                  className="w-full bg-red-600 hover:bg-red-700 rounded-lg px-4 py-2 font-medium transition-colors flex items-center justify-center space-x-2"
                >
                  <Disconnect className="h-4 w-4" />
                  <span>Disconnect</span>
                </button>
              </div>
            )}
          </motion.div>

          {/* Node Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
          >
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Monitor className="h-5 w-5 mr-2" />
              Node Information
            </h2>

            <div className="space-y-4">
              <div>
                <p className="text-slate-400 text-sm">Node ID</p>
                <p className="font-mono text-sm">
                  {connectionStatus?.node_id || "Not assigned"}
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Role</p>
                <p className="capitalize">Peer</p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Capabilities</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="px-2 py-1 bg-blue-800/50 text-blue-300 rounded text-xs">
                    Metrics Collection
                  </span>
                  <span className="px-2 py-1 bg-blue-800/50 text-blue-300 rounded text-xs">
                    Self-Healing
                  </span>
                  <span className="px-2 py-1 bg-blue-800/50 text-blue-300 rounded text-xs">
                    Mirror Support
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* System Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
        >
          <h2 className="text-xl font-bold mb-6 flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            System Metrics
          </h2>

          {systemMetrics ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Cpu className="h-6 w-6 text-blue-400 mr-2" />
                  <span className="text-slate-400">CPU Usage</span>
                </div>
                <div className="text-3xl font-bold mb-2">
                  {systemMetrics.cpu_usage.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-400 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${systemMetrics.cpu_usage}%` }}
                  />
                </div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <MemoryStick className="h-6 w-6 text-green-400 mr-2" />
                  <span className="text-slate-400">Memory Usage</span>
                </div>
                <div className="text-3xl font-bold mb-2">
                  {systemMetrics.memory_usage.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-green-400 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${systemMetrics.memory_usage}%` }}
                  />
                </div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <HardDrive className="h-6 w-6 text-orange-400 mr-2" />
                  <span className="text-slate-400">Disk Usage</span>
                </div>
                <div className="text-3xl font-bold mb-2">
                  {systemMetrics.disk_usage.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-orange-400 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${systemMetrics.disk_usage}%` }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-400">
              No metrics available
            </div>
          )}
        </motion.div>

        {/* Network Statistics */}
        {systemMetrics?.network_io && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-8 bg-slate-800/50 rounded-lg p-6 border border-slate-700"
          >
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Wifi className="h-5 w-5 mr-2" />
              Network Statistics
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <p className="text-slate-400 mb-2">Bytes Sent</p>
                <p className="text-2xl font-bold">
                  {(systemMetrics.network_io.bytes_sent / 1024 / 1024).toFixed(
                    2
                  )}{" "}
                  MB
                </p>
              </div>
              <div className="text-center">
                <p className="text-slate-400 mb-2">Bytes Received</p>
                <p className="text-2xl font-bold">
                  {(systemMetrics.network_io.bytes_recv / 1024 / 1024).toFixed(
                    2
                  )}{" "}
                  MB
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
