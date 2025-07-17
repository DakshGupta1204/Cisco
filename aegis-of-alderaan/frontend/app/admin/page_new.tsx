"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  Users,
  Activity,
  AlertTriangle,
  Wifi,
  Server,
  Eye,
  RefreshCw,
  Network,
  Brain,
  Zap,
} from "lucide-react";

interface PeerInfo {
  node_id: string;
  hostname: string;
  ip_address: string;
  role: string;
  health_status: string;
  last_heartbeat: string;
  capabilities: string[];
  metrics?: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_io: {
      bytes_sent: number;
      bytes_recv: number;
    };
  };
}

interface NetworkStatus {
  node_id: string;
  role: string;
  connected_peers: number;
  healthy_peers: number;
  last_updated: string;
  peers: Record<string, PeerInfo>;
}

export default function AdminPanel() {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus | null>(
    null
  );
  const [selectedPeer, setSelectedPeer] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Connect to Guardian WebSocket
    const connectWebSocket = () => {
      const websocket = new WebSocket("ws://localhost:3001/ws/guardian");

      websocket.onopen = () => {
        console.log("Connected to Guardian WebSocket");
        setWsConnected(true);
        setWs(websocket);
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "network_status") {
          setNetworkStatus(data.data);
        } else if (data.type === "peer_metrics") {
          // Update specific peer metrics
          setNetworkStatus((prev) => {
            if (!prev) return null;
            return {
              ...prev,
              peers: {
                ...prev.peers,
                [data.node_id]: {
                  ...prev.peers[data.node_id],
                  metrics: data.metrics,
                },
              },
            };
          });
        }
      };

      websocket.onclose = () => {
        console.log("Guardian WebSocket disconnected");
        setWsConnected(false);
        setWs(null);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        console.error("Guardian WebSocket error:", error);
      };
    };

    // Fetch initial network status
    const fetchNetworkStatus = async () => {
      try {
        const response = await fetch(
          "http://localhost:3001/distributed/network/status"
        );
        if (response.ok) {
          const data = await response.json();
          setNetworkStatus(data);
        }
      } catch (error) {
        console.error("Error fetching network status:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNetworkStatus();
    connectWebSocket();

    // Refresh network status every 10 seconds
    const interval = setInterval(fetchNetworkStatus, 10000);

    return () => {
      clearInterval(interval);
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const handleRunAIAnalysis = async (nodeId: string) => {
    try {
      const response = await fetch(
        `http://localhost:3001/ai/analyze/health/${nodeId}`,
        {
          method: "POST",
        }
      );
      if (response.ok) {
        const analysis = await response.json();
        console.log("AI Analysis:", analysis);
        // Could show this in a modal or notification
      }
    } catch (error) {
      console.error("Error running AI analysis:", error);
    }
  };

  const handleCoordinateHealing = async (nodeId: string) => {
    try {
      const response = await fetch(
        `http://localhost:3001/ai/healing/strategy/${nodeId}`,
        {
          method: "POST",
        }
      );
      if (response.ok) {
        const strategy = await response.json();
        console.log("Healing Strategy:", strategy);

        // Execute healing via distributed manager
        const healingResponse = await fetch(
          `http://localhost:3001/distributed/healing/coordinate`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              target_node: nodeId,
              healing_strategy: strategy.healing_strategy,
            }),
          }
        );

        if (healingResponse.ok) {
          console.log("Healing coordinated successfully");
        }
      }
    } catch (error) {
      console.error("Error coordinating healing:", error);
    }
  };

  const handleSimulateAttack = async (nodeId: string) => {
    try {
      const response = await fetch(
        "http://localhost:3001/simulate/attack/cpu",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            target_agent: nodeId,
            cpu_percentage: 85,
            duration: 30,
          }),
        }
      );
      if (response.ok) {
        console.log("Attack simulation started");
      }
    } catch (error) {
      console.error("Error simulating attack:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-purple-400 mx-auto mb-4" />
          <p className="text-purple-300">Loading Guardian Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-purple-800/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8 text-purple-400" />
              <div>
                <h1 className="text-2xl font-bold">Aegis Guardian</h1>
                <p className="text-purple-300 text-sm">
                  Distributed Network Control Center
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div
                className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                  wsConnected
                    ? "bg-green-900/50 text-green-300"
                    : "bg-red-900/50 text-red-300"
                }`}
              >
                <Wifi className="h-4 w-4" />
                <span className="text-sm">
                  {wsConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <div className="text-sm text-purple-300">
                Node ID: {networkStatus?.node_id}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Network Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-purple-800/50 to-blue-800/50 rounded-lg p-6 border border-purple-600/30"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Connected Peers</p>
                <p className="text-3xl font-bold">
                  {networkStatus?.connected_peers || 0}
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-800/50 to-emerald-800/50 rounded-lg p-6 border border-green-600/30"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-300 text-sm">Healthy Peers</p>
                <p className="text-3xl font-bold">
                  {networkStatus?.healthy_peers || 0}
                </p>
              </div>
              <Activity className="h-8 w-8 text-green-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-orange-800/50 to-red-800/50 rounded-lg p-6 border border-orange-600/30"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-300 text-sm">Alerts</p>
                <p className="text-3xl font-bold">
                  {
                    Object.values(networkStatus?.peers || {}).filter(
                      (p) => p.health_status !== "healthy"
                    ).length
                  }
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-blue-800/50 to-cyan-800/50 rounded-lg p-6 border border-blue-600/30"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-300 text-sm">Network Status</p>
                <p className="text-lg font-bold">Active</p>
              </div>
              <Network className="h-8 w-8 text-blue-400" />
            </div>
          </motion.div>
        </div>

        {/* Peer Management */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Peer List */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Server className="h-5 w-5 mr-2" />
              Connected Peers
            </h2>
            <div className="space-y-4">
              {Object.entries(networkStatus?.peers || {}).map(
                ([nodeId, peer]) => (
                  <motion.div
                    key={nodeId}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`bg-slate-800/50 rounded-lg p-6 border transition-all cursor-pointer ${
                      selectedPeer === nodeId
                        ? "border-purple-500 bg-purple-900/30"
                        : "border-slate-700 hover:border-purple-600/50"
                    }`}
                    onClick={() => setSelectedPeer(nodeId)}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`w-3 h-3 rounded-full ${
                            peer.health_status === "healthy"
                              ? "bg-green-400"
                              : "bg-red-400"
                          }`}
                        />
                        <div>
                          <h3 className="font-bold">{peer.hostname}</h3>
                          <p className="text-sm text-slate-400">
                            {peer.ip_address} • {peer.role}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRunAIAnalysis(nodeId);
                          }}
                          className="p-2 text-purple-400 hover:bg-purple-800/50 rounded-lg transition-colors"
                          title="Run AI Analysis"
                        >
                          <Brain className="h-4 w-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCoordinateHealing(nodeId);
                          }}
                          className="p-2 text-green-400 hover:bg-green-800/50 rounded-lg transition-colors"
                          title="Coordinate Healing"
                        >
                          <Zap className="h-4 w-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSimulateAttack(nodeId);
                          }}
                          className="p-2 text-red-400 hover:bg-red-800/50 rounded-lg transition-colors"
                          title="Simulate Attack"
                        >
                          <AlertTriangle className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    {peer.metrics && (
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                          <p className="text-xs text-slate-400">CPU</p>
                          <p className="text-lg font-bold">
                            {peer.metrics.cpu_usage.toFixed(1)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-slate-400">Memory</p>
                          <p className="text-lg font-bold">
                            {peer.metrics.memory_usage.toFixed(1)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-slate-400">Disk</p>
                          <p className="text-lg font-bold">
                            {peer.metrics.disk_usage.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="mt-4 flex flex-wrap gap-2">
                      {peer.capabilities.map((capability) => (
                        <span
                          key={capability}
                          className="px-2 py-1 bg-purple-800/50 text-purple-300 rounded text-xs"
                        >
                          {capability}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                )
              )}
            </div>
          </div>

          {/* Peer Details */}
          <div>
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <Eye className="h-5 w-5 mr-2" />
              Peer Details
            </h2>
            {selectedPeer && networkStatus?.peers[selectedPeer] ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
              >
                <div className="space-y-4">
                  <div>
                    <h3 className="font-bold text-lg">
                      {networkStatus.peers[selectedPeer].hostname}
                    </h3>
                    <p className="text-slate-400">
                      {networkStatus.peers[selectedPeer].ip_address}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400">Node ID</p>
                    <p className="font-mono text-sm">{selectedPeer}</p>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400">Role</p>
                    <p className="capitalize">
                      {networkStatus.peers[selectedPeer].role}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400">Health Status</p>
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          networkStatus.peers[selectedPeer].health_status ===
                          "healthy"
                            ? "bg-green-400"
                            : "bg-red-400"
                        }`}
                      />
                      <span className="capitalize">
                        {networkStatus.peers[selectedPeer].health_status}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400">Last Heartbeat</p>
                    <p className="text-sm">
                      {networkStatus.peers[selectedPeer].last_heartbeat
                        ? new Date(
                            networkStatus.peers[selectedPeer].last_heartbeat
                          ).toLocaleString()
                        : "Never"}
                    </p>
                  </div>

                  {networkStatus.peers[selectedPeer].metrics && (
                    <div>
                      <p className="text-sm text-slate-400 mb-2">
                        System Metrics
                      </p>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>CPU Usage</span>
                          <span>
                            {networkStatus.peers[
                              selectedPeer
                            ].metrics!.cpu_usage.toFixed(1)}
                            %
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Memory Usage</span>
                          <span>
                            {networkStatus.peers[
                              selectedPeer
                            ].metrics!.memory_usage.toFixed(1)}
                            %
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Disk Usage</span>
                          <span>
                            {networkStatus.peers[
                              selectedPeer
                            ].metrics!.disk_usage.toFixed(1)}
                            %
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 text-center text-slate-400">
                Select a peer to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
