'use client';

import { useState, useEffect } from 'react';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Separator } from '../components/ui/separator';
import Sidebar from '../components/Sidebar';
import NetworkTopology from '../components/NetworkTopology';
import MetricsCharts from '../components/MetricsCharts';
import ThreatTimeline from '../components/ThreatTimeline';
import DeviceStatus from '../components/DeviceStatus';
import Footer from '../components/Footer';
import { generateMockDevices, generateMockThreats, generateMockMetrics } from '../utils/mockData';
import { Device, Threat, NetworkMetrics, ConnectionStatus, SystemStatus, DashboardState } from '../types';
import { apiService } from '../lib/api';
import { Shield, Zap, Clock, Wifi, WifiOff, Server, Cpu, AlertTriangle, Bot, Info } from 'lucide-react';

export default function AegisOfAlderaan() {
  const [dashboardState, setDashboardState] = useState<DashboardState>({
    activeView: 'network',
    connectionStatus: {
      status: 'disconnected',
      lastUpdate: new Date(),
      serverHealth: 0
    },
    systemStatus: {
      status: 'secure',
      serviceAvailability: 100,
      totalDevices: 0,
      healthyDevices: 0,
      activeThreats: 0,
      avgResponseTime: 0,
      autoRecoveryActive: true,
      aiProtectionActive: true,
      threatsBlocked: 0
    },
    devices: [],
    threats: [],
    metrics: []
  });

  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    // Initialize with mock data first
    initializeMockData();
    
    // Try to connect to real API
    initializeApiConnection();
    
    // Set up WebSocket listeners
    setupWebSocketListeners();

    return () => {
      apiService.disconnectWebSocket();
    };
  }, []);

  const initializeMockData = () => {
    const mockDevices = generateMockDevices();
    const mockThreats = generateMockThreats();
    const mockMetrics = generateMockMetrics();

    setDashboardState(prev => ({
      ...prev,
      devices: mockDevices,
      threats: mockThreats,
      metrics: mockMetrics,
      systemStatus: {
        ...prev.systemStatus,
        totalDevices: mockDevices.length,
        healthyDevices: mockDevices.filter(d => d.status === 'healthy').length,
        activeThreats: mockThreats.filter(t => t.status === 'detected' || t.status === 'responding').length,
        avgResponseTime: mockMetrics[mockMetrics.length - 1]?.responseTime || 0,
        threatsBlocked: mockThreats.filter(t => t.status === 'resolved').length
      }
    }));
  };

  const initializeApiConnection = async () => {
    try {
      // Try health check first
      await apiService.healthCheck();
      
      // If successful, load real data
      const [devices, threats] = await Promise.all([
        apiService.getDevices(), // Changed from getAgents
        apiService.getThreats(50)
      ]);

      setDashboardState(prev => ({
        ...prev,
        devices,
        threats,
        connectionStatus: {
          status: 'connected',
          lastUpdate: new Date(),
          serverHealth: 100
        }
      }));

      // Connect WebSocket
      apiService.connectWebSocket();
      
    } catch (error) {
      console.log('API not available, using mock data:', error);
      setDemoMode(true);
      
      // Simulate periodic updates with mock data
      const interval = setInterval(() => {
        updateMockData();
      }, 3000);

      return () => clearInterval(interval);
    }
  };

  const setupWebSocketListeners = () => {
    // Connection status updates
    const unsubscribeConnection = apiService.subscribe('connection', (data) => {
      setDashboardState(prev => ({
        ...prev,
        connectionStatus: {
          status: data.status,
          lastUpdate: new Date(),
          serverHealth: data.status === 'connected' ? 100 : 0
        }
      }));
    });

    // Agent updates
    const unsubscribeAgents = apiService.subscribe('device_update', (data) => { // Changed from agent_update
      setDashboardState(prev => ({
        ...prev,
        devices: prev.devices.map(device => 
          device.id === data.id ? { ...device, ...data } : device
        )
      }));
    });

    // Threat detection
    const unsubscribeThreats = apiService.subscribe('threat_detected', (data) => {
      setDashboardState(prev => ({
        ...prev,
        threats: [data, ...prev.threats].slice(0, 50), // Keep last 50 threats
        systemStatus: {
          ...prev.systemStatus,
          activeThreats: prev.systemStatus.activeThreats + 1,
          status: data.severity === 'critical' ? 'under_attack' : 'warning'
        }
      }));
    });

    // System status updates
    const unsubscribeSystem = apiService.subscribe('system_status', (data) => {
      setDashboardState(prev => ({
        ...prev,
        systemStatus: { ...prev.systemStatus, ...data }
      }));
    });

    return () => {
      unsubscribeConnection();
      unsubscribeAgents();
      unsubscribeThreats();
      unsubscribeSystem();
    };
  };

  const updateMockData = () => {
    setDashboardState(prev => ({
      ...prev,
      devices: prev.devices.map(device => ({
        ...device,
        metrics: {
          ...device.metrics,
          cpu: Math.max(0, Math.min(100, device.metrics.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(0, Math.min(100, device.metrics.memory + (Math.random() - 0.5) * 5)),
          network: Math.max(0, Math.min(100, device.metrics.network + (Math.random() - 0.5) * 15))
        },
        lastSeen: new Date()
      })),
      connectionStatus: {
        ...prev.connectionStatus,
        lastUpdate: new Date(),
        serverHealth: Math.max(85, Math.random() * 100)
      }
    }));
  };

  const handleViewChange = (view: string) => {
    setDashboardState(prev => ({ 
      ...prev, 
      activeView: view as DashboardState['activeView'] 
    }));
  };

  const handleDemoTrigger = async (type: 'ddos' | 'malware' | 'intrusion') => {
    try {
      if (!demoMode) {
        await apiService.triggerAttack(type);
      } else {
        // Simulate demo attack in mock mode
        simulateDemoAttack(type);
      }
    } catch (error) {
      console.error('Failed to trigger demo attack:', error);
      simulateDemoAttack(type);
    }
  };

  const simulateDemoAttack = (type: 'ddos' | 'malware' | 'intrusion') => {
    // Create a simulated attack
    const newThreat: Threat = {
      id: `demo_threat_${Date.now()}`,
      type,
      severity: 'high',
      timestamp: new Date(),
      affectedDevices: [dashboardState.devices[0]?.id || 'device_1'],
      sourceIP: '192.168.100.1',
      status: 'detected',
      responseTime: 0,
      aiAnalysis: {
        explanation: `Demo ${type} attack simulated for presentation purposes`,
        confidence: 95,
        recommendedActions: ['Monitor situation', 'Prepare countermeasures'],
        riskAssessment: 'Controlled demo environment - no actual threat'
      },
      responseActions: []
    };

    setDashboardState(prev => ({
      ...prev,
      threats: [newThreat, ...prev.threats],
      systemStatus: {
        ...prev.systemStatus,
        status: 'under_attack',
        activeThreats: prev.systemStatus.activeThreats + 1
      }
    }));

    // Simulate response after 3 seconds
    setTimeout(() => {
      setDashboardState(prev => ({
        ...prev,
        threats: prev.threats.map(t => 
          t.id === newThreat.id ? { ...t, status: 'resolved' as const } : t
        ),
        systemStatus: {
          ...prev.systemStatus,
          status: 'secure',
          activeThreats: Math.max(0, prev.systemStatus.activeThreats - 1),
          threatsBlocked: prev.systemStatus.threatsBlocked + 1
        }
      }));
    }, 3000);
  };

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const getStatusColor = (status: typeof dashboardState.systemStatus.status) => {
    switch (status) {
      case 'secure': return 'bg-white dark:bg-gray-200';
      case 'warning': return 'bg-yellow-500';
      case 'under_attack': return 'bg-red-500';
      case 'responding': return 'bg-gray-400';
      case 'healing': return 'bg-gray-400';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: typeof dashboardState.systemStatus.status) => {
    switch (status) {
      case 'secure': return 'SECURE';
      case 'warning': return 'WARNING';
      case 'under_attack': return 'UNDER ATTACK';
      case 'responding': return 'RESPONDING';
      case 'healing': return 'HEALING';
      default: return 'UNKNOWN';
    }
  };

  const renderMainContent = () => {
    switch (dashboardState.activeView) {
      case 'network':
        return (
          <NetworkTopology 
            devices={dashboardState.devices} 
            threats={dashboardState.threats}
            onDemoTrigger={handleDemoTrigger}
          />
        );
      case 'metrics':
        return (
          <MetricsCharts 
            metrics={dashboardState.metrics} 
            devices={dashboardState.devices}
            systemStatus={dashboardState.systemStatus}
          />
        );
      case 'threats':
        return (
          <ThreatTimeline 
            threats={dashboardState.threats}
            devices={dashboardState.devices}
          />
        );
      case 'devices':
        return (
          <DeviceStatus 
            devices={dashboardState.devices}
            threats={dashboardState.threats}
          />
        );
      case 'demo':
        return (
          <div className="p-4 sm:p-6 md:p-8 space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-light tracking-tight">Demonstration Control Panel</h2>
              <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
                These actions simulate real-world attack vectors, allowing you to observe the platform's detection and response capabilities in a controlled environment.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              <div className="border border-border rounded-lg p-6 hover:border-red-500/50 hover:bg-red-500/10 transition-all duration-300 group">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6 text-red-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-foreground">Simulate DDoS Attack</h3>
                    <p className="text-muted-foreground mt-1 text-sm">
                      Initiates a high-volume traffic flood to test network resilience and traffic filtering capabilities. This demonstrates our ability to mitigate large-scale denial-of-service attacks.
                    </p>
                    <button
                      onClick={() => handleDemoTrigger('ddos')}
                      className="mt-4 text-sm font-semibold text-red-500 group-hover:underline"
                    >
                      Trigger Simulation &rarr;
                    </button>
                  </div>
                </div>
              </div>
              <div className="border border-border rounded-lg p-6 hover:border-yellow-500/50 hover:bg-yellow-500/10 transition-all duration-300 group">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center">
                    <Bot className="w-6 h-6 text-yellow-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-foreground">Simulate Malware Deployment</h3>
                    <p className="text-muted-foreground mt-1 text-sm">
                      Simulates the introduction of a malicious software agent into the network to test endpoint detection and response. This showcases our AI-driven threat identification.
                    </p>
                    <button
                      onClick={() => handleDemoTrigger('malware')}
                      className="mt-4 text-sm font-semibold text-yellow-500 group-hover:underline"
                    >
                      Trigger Simulation &rarr;
                    </button>
                  </div>
                </div>
              </div>
            </div>
            {demoMode && (
              <div className="border border-blue-500/20 bg-blue-500/5 rounded-lg p-4 max-w-4xl mx-auto flex items-center justify-center space-x-3">
                <Info className="w-5 h-5 text-blue-500" />
                <p className="text-muted-foreground font-light text-center">
                  Demo Mode Active - Using simulated data for presentation.
                </p>
              </div>
            )}
          </div>
        );
      default:
        return (
          <NetworkTopology 
            devices={dashboardState.devices} 
            threats={dashboardState.threats}
            onDemoTrigger={handleDemoTrigger}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Modern Clean Navbar */}
      <nav className="border-b border-border bg-background/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            {/* Logo Section */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-foreground rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-background" />
              </div>
              <h1 className="text-lg font-medium tracking-tighter text-foreground">
                Aegis
              </h1>
            </div>

            {/* Status Section - Center */}
            <div className="hidden lg:flex items-center space-x-6">
              {/* Service Availability */}
              <div className="flex items-center space-x-3">
                <Server className="w-5 h-5 text-muted-foreground" />
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs space-x-4">
                    <span className="font-light text-muted-foreground">Availability</span>
                    <span className="font-mono text-foreground">
                      {dashboardState.systemStatus.serviceAvailability.toFixed(1)}%
                    </span>
                  </div>
                  <Progress 
                    value={dashboardState.systemStatus.serviceAvailability} 
                    className="h-1 w-28 bg-gray-200 dark:bg-gray-800"
                  />
                </div>
              </div>

              <Separator orientation="vertical" className="h-6 bg-border/50" />

              {/* Devices Status */}
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-5 h-5 text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">{dashboardState.systemStatus.healthyDevices}</span>
                  <span className="text-xs font-light text-muted-foreground">Healthy Devices</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className={`w-5 h-5 ${dashboardState.systemStatus.activeThreats > 0 ? 'text-red-500' : 'text-muted-foreground'}`} />
                  <span className={`text-sm font-medium ${dashboardState.systemStatus.activeThreats > 0 ? 'text-red-500' : 'text-foreground'}`}>
                    {dashboardState.systemStatus.activeThreats}
                  </span>
                  <span className="text-xs font-light text-muted-foreground">Active Threats</span>
                </div>
              </div>
            </div>

            {/* Connection & Time */}
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="hidden md:flex items-center space-x-2">
                {dashboardState.connectionStatus.status === 'connected' ? 
                  <Wifi className="w-5 h-5 text-green-500" /> : 
                  <WifiOff className={`w-5 h-5 ${dashboardState.connectionStatus.status === 'reconnecting' ? 'text-yellow-500' : 'text-red-500'}`} />
                }
                <span className="text-xs font-light text-muted-foreground">
                  {dashboardState.connectionStatus.status === 'connected' ? 'Online' :
                   dashboardState.connectionStatus.status === 'reconnecting' ? 'Reconnecting' :
                   'Offline'}
                </span>
              </div>

              <Separator orientation="vertical" className="h-6 bg-border/50 hidden md:block" />

              {/* Current Time */}
              <div className="hidden sm:flex items-center space-x-2">
                <Clock className="w-5 h-5 text-muted-foreground" />
                <span className="text-sm font-mono font-light text-foreground">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <div className="w-5 h-5 flex flex-col justify-center space-y-1">
                  <div className={`w-full h-0.5 bg-foreground transition-all duration-300 ${mobileMenuOpen ? 'rotate-45 translate-y-1' : ''}`}></div>
                  <div className={`w-full h-0.5 bg-foreground transition-all duration-300 ${mobileMenuOpen ? 'opacity-0' : ''}`}></div>
                  <div className={`w-full h-0.5 bg-foreground transition-all duration-300 ${mobileMenuOpen ? '-rotate-45 -translate-y-1' : ''}`}></div>
                </div>
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="lg:hidden mt-4 pt-4 border-t border-border">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-light text-muted-foreground">Availability:</span>
                  <span className="text-sm font-medium text-foreground">
                    {dashboardState.systemStatus.serviceAvailability.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-light text-muted-foreground">Connection:</span>
                  <span className="text-sm font-light text-muted-foreground">
                    {dashboardState.connectionStatus.status}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-light text-muted-foreground">Healthy Devices:</span>
                  <span className="text-sm font-medium text-foreground">{dashboardState.systemStatus.healthyDevices}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-light text-muted-foreground">Active Threats:</span>
                  <span className={`text-sm font-medium ${dashboardState.systemStatus.activeThreats > 0 ? 'text-red-500' : 'text-foreground'}`}>
                    {dashboardState.systemStatus.activeThreats}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>
      
      <div className="flex flex-1">
        <Sidebar 
          activeView={dashboardState.activeView} 
          onViewChange={handleViewChange}
          systemStatus={dashboardState.systemStatus}
        />
        
        <main className="flex-1 p-4 sm:p-6 md:p-8 transition-all duration-500 ease-in-out overflow-y-auto">
          <div className="max-w-full mx-auto h-full">
            <div className="animate-in fade-in-25 duration-500">
              {renderMainContent()}
            </div>
          </div>
        </main>
      </div>
      
      <Footer 
        devices={dashboardState.devices} 
        threats={dashboardState.threats} 
        connectionStatus={dashboardState.connectionStatus}
        systemStatus={dashboardState.systemStatus}
      />
    </div>
  );
}

