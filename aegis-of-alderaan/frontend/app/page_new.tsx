"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Shield,
  Server,
  Network,
  Users,
  Settings,
  ArrowRight,
  Laptop,
  Globe,
} from "lucide-react";

export default function HomePage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white flex items-center justify-center">
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center mb-6">
            <Shield className="h-16 w-16 text-blue-400 mr-4" />
            <div>
              <h1 className="text-4xl font-bold">Aegis of Alderaan</h1>
              <p className="text-blue-300 text-lg">
                Distributed Network Protection System
              </p>
            </div>
          </div>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto">
            Choose your role in the distributed network. Each laptop can serve
            as either a Guardian (admin center) or a Peer (protected node) in
            the resilient security system.
          </p>
        </motion.div>

        {/* Role Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Guardian Option */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className={`relative overflow-hidden rounded-xl border-2 transition-all cursor-pointer ${
              selectedRole === "guardian"
                ? "border-purple-500 bg-purple-900/30"
                : "border-slate-700 hover:border-purple-600/50 bg-slate-800/50"
            }`}
            onClick={() => setSelectedRole("guardian")}
          >
            <div className="p-8">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-purple-600/20 rounded-lg mr-4">
                  <Shield className="h-8 w-8 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">Guardian</h3>
                  <p className="text-purple-300">Control Center</p>
                </div>
              </div>

              <p className="text-slate-300 mb-6">
                Central coordination hub for the distributed network. Manages
                all peer connections, AI-powered threat analysis, and
                network-wide healing operations.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm">
                  <Users className="h-4 w-4 text-purple-400 mr-2" />
                  <span>Manage multiple peer nodes</span>
                </div>
                <div className="flex items-center text-sm">
                  <Network className="h-4 w-4 text-purple-400 mr-2" />
                  <span>Real-time network topology</span>
                </div>
                <div className="flex items-center text-sm">
                  <Settings className="h-4 w-4 text-purple-400 mr-2" />
                  <span>AI-powered threat analysis</span>
                </div>
                <div className="flex items-center text-sm">
                  <Globe className="h-4 w-4 text-purple-400 mr-2" />
                  <span>Distributed healing coordination</span>
                </div>
              </div>

              {selectedRole === "guardian" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4"
                >
                  <Link href="/admin">
                    <button className="w-full bg-purple-600 hover:bg-purple-700 rounded-lg px-4 py-3 font-medium transition-colors flex items-center justify-center space-x-2">
                      <span>Launch Guardian Panel</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </Link>
                </motion.div>
              )}
            </div>

            {/* Laptop Icon */}
            <div className="absolute top-4 right-4 opacity-20">
              <Laptop className="h-16 w-16" />
            </div>
          </motion.div>

          {/* Peer Option */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className={`relative overflow-hidden rounded-xl border-2 transition-all cursor-pointer ${
              selectedRole === "peer"
                ? "border-blue-500 bg-blue-900/30"
                : "border-slate-700 hover:border-blue-600/50 bg-slate-800/50"
            }`}
            onClick={() => setSelectedRole("peer")}
          >
            <div className="p-8">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-blue-600/20 rounded-lg mr-4">
                  <Server className="h-8 w-8 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">Peer</h3>
                  <p className="text-blue-300">Protected Node</p>
                </div>
              </div>

              <p className="text-slate-300 mb-6">
                Individual network participant that connects to the Guardian.
                Provides system metrics, receives protection, and participates
                in distributed healing processes.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center text-sm">
                  <Server className="h-4 w-4 text-blue-400 mr-2" />
                  <span>Real-time system monitoring</span>
                </div>
                <div className="flex items-center text-sm">
                  <Network className="h-4 w-4 text-blue-400 mr-2" />
                  <span>Guardian connection management</span>
                </div>
                <div className="flex items-center text-sm">
                  <Settings className="h-4 w-4 text-blue-400 mr-2" />
                  <span>Automated self-healing</span>
                </div>
                <div className="flex items-center text-sm">
                  <Shield className="h-4 w-4 text-blue-400 mr-2" />
                  <span>Mirror support & failover</span>
                </div>
              </div>

              {selectedRole === "peer" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4"
                >
                  <Link href="/peer">
                    <button className="w-full bg-blue-600 hover:bg-blue-700 rounded-lg px-4 py-3 font-medium transition-colors flex items-center justify-center space-x-2">
                      <span>Launch Peer Dashboard</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </Link>
                </motion.div>
              )}
            </div>

            {/* Laptop Icon */}
            <div className="absolute top-4 right-4 opacity-20">
              <Laptop className="h-16 w-16" />
            </div>
          </motion.div>
        </div>

        {/* Quick Setup Guide */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/50 rounded-lg p-6 border border-slate-700"
        >
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Quick Setup Guide
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-purple-300 mb-2">
                🛡️ Guardian Setup (Laptop 1)
              </h4>
              <ol className="text-sm space-y-1 text-slate-300">
                <li>
                  1. Run:{" "}
                  <code className="bg-slate-700 px-1 rounded">
                    python deploy_multi_laptop.py guardian
                  </code>
                </li>
                <li>2. Note the displayed IP address</li>
                <li>3. Share IP with peer laptops</li>
                <li>4. Access admin panel at /admin</li>
              </ol>
            </div>

            <div>
              <h4 className="font-semibold text-blue-300 mb-2">
                🤝 Peer Setup (Laptop 2 & 3)
              </h4>
              <ol className="text-sm space-y-1 text-slate-300">
                <li>
                  1. Run:{" "}
                  <code className="bg-slate-700 px-1 rounded">
                    python deploy_multi_laptop.py peer
                  </code>
                </li>
                <li>2. Enter Guardian IP address</li>
                <li>3. Choose unique agent ID</li>
                <li>4. Access peer dashboard at /peer</li>
              </ol>
            </div>
          </div>

          <div className="mt-4 p-4 bg-blue-900/30 border border-blue-600/50 rounded-lg">
            <p className="text-sm text-blue-300">
              💡 <strong>Tip:</strong> All laptops need to be on the same
              network. The Guardian will coordinate AI-powered threat detection
              and healing across all connected peers.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
