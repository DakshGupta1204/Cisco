import { useState, useMemo } from 'react';
import { Device, Threat } from '../types';
import { Card, CardContent } from './ui/card';
import { Server, Database, Router, Smartphone, ShieldCheck, Cpu, Computer } from 'lucide-react';

interface NetworkTopologyProps {
  devices: Device[];
  threats: Threat[];
  onDemoTrigger?: (type: 'ddos' | 'malware' | 'intrusion') => void;
}

export default function NetworkTopology({ devices, threats }: NetworkTopologyProps) {
  const [hoveredDevice, setHoveredDevice] = useState<string | null>(null);

  const getNodeStatus = (device: Device) => {
    const isThreatened = threats.some(t => t.affectedDevices.includes(device.id) && (t.status === 'detected' || t.status === 'responding'));
    if (isThreatened) return 'threat';
    return device.status;
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'web_server': return <Server className="w-8 h-8" />;
      case 'database': return <Database className="w-8 h-8" />;
      case 'load_balancer': return <Router className="w-8 h-8" />;
      case 'iot_device': return <Smartphone className="w-8 h-8" />;
      case 'computer': return <Computer className="w-8 h-8" />;
      default: return <Cpu className="w-8 h-8" />;
    }
  };

  const hubNode = { id: 'central_hub', x: 150, y: 100, type: 'core_firewall' };

  const nodePositions = useMemo(() => {
    const positions = [];
    const cols = Math.min(Math.ceil(devices.length / 2), 4);
    const gridWidth = 700;
    const gridHeight = 400;
    const colWidth = gridWidth / Math.max(1, cols);
    const rowHeight = gridHeight / Math.max(1, Math.ceil(devices.length / cols));
    const startX = 50;
    const startY = 250;

    for (let i = 0; i < devices.length; i++) {
      const device = devices[i];
      const col = i % cols;
      const row = Math.floor(i / cols);
      positions.push({
        ...device,
        x: startX + col * colWidth + colWidth / 2,
        y: startY + row * rowHeight,
      });
    }
    return positions;
  }, [devices]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-light tracking-tight text-foreground">Network Topology</h2>
          <p className="text-muted-foreground">
            Real-time visualization of the Aegis Security Hub and connected devices.
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-xs text-muted-foreground mb-1">Devices</div>
              <div className="text-2xl font-medium text-foreground">{devices.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-xs text-muted-foreground mb-1">Active Threats</div>
              <div className={`text-2xl font-medium ${threats.filter(t => t.status === 'detected' || t.status === 'responding').length > 0 ? 'text-red-500' : 'text-foreground'}`}>
                {threats.filter(t => t.status === 'detected' || t.status === 'responding').length}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Topology Visualization */}
      <Card className="w-full h-[650px] p-4">
        <svg width="100%" height="100%" viewBox="0 0 900 650">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="5" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <style>
              {`
                .data-flow {
                  stroke-dasharray: 4;
                  animation: dash 2s linear infinite;
                }
                .data-flow-down {
                  stroke-dasharray: 4;
                  animation: dash-down 5s linear infinite;
                }
                @keyframes dash {
                  to {
                    stroke-dashoffset: -20;
                  }
                }
                @keyframes dash-down {
                  from {
                    stroke-dashoffset: 0;
                  }
                  to {
                    stroke-dashoffset: 20;
                  }
                }
              `}
            </style>
          </defs>

          {/* Connections */}
          {nodePositions.map(node => {
            const status = getNodeStatus(node);
            const isHealthy = status === 'healthy';
            return (
              <g key={`line-group-${node.id}`}>
                <path
                  d={`M ${hubNode.x} ${hubNode.y} C ${hubNode.x} ${hubNode.y + 100}, ${node.x} ${node.y - 100}, ${node.x} ${node.y}`}
                  className={isHealthy ? "stroke-foreground/10" : "stroke-yellow-500/30"}
                  strokeWidth="1"
                  fill="none"
                />
                <path
                  d={`M ${hubNode.x} ${hubNode.y} C ${hubNode.x} ${hubNode.y + 100}, ${node.x} ${node.y - 100}, ${node.x} ${node.y}`}
                  className={isHealthy ? "stroke-green-500/80 data-flow" : "stroke-yellow-500/80 data-flow-down"}
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  fill="none"
                />
              </g>
            );
          })}
          
          {/* Central Hub Text (rendered before the node to be underneath) */}
          <g transform={`translate(${hubNode.x}, ${hubNode.y + 65})`}>
            <text textAnchor="middle" className="text-sm font-semibold fill-foreground">Aegis Security Hub</text>
            <text y="15" textAnchor="middle" className="text-xs fill-muted-foreground">Core Firewall & Analysis</text>
          </g>

          {/* Central Hub */}
          <g transform={`translate(${hubNode.x}, ${hubNode.y})`} className="cursor-pointer">
            <circle r="50" className="fill-background" />
            <circle r="50" className="fill-green-500/10 stroke-green-500/50" strokeWidth="1" />
            <g transform="translate(-24, -24)">
              <ShieldCheck className="w-12 h-12 text-green-500" />
            </g>
          </g>

          {/* Device Nodes */}
          {nodePositions.map(node => {
            const status = getNodeStatus(node);
            const isThreat = status === 'threat';
            return (
              <g 
                key={node.id} 
                transform={`translate(${node.x}, ${node.y})`}
                onMouseEnter={() => setHoveredDevice(node.id)}
                onMouseLeave={() => setHoveredDevice(null)}
                className="cursor-pointer group"
              >
                <circle 
                  r="35" 
                  className={`fill-background transition-all duration-300 group-hover:stroke-blue-500 ${
                    isThreat ? 'stroke-red-500' : 'stroke-foreground/20'
                  }`}
                  strokeWidth="1"
                />
                <circle 
                  r="35" 
                  className={`transition-all duration-300 ${
                    isThreat ? 'fill-red-500/10' : 'fill-transparent'
                  }`}
                />
                <g transform="translate(-16, -16)" className={isThreat ? 'text-red-500' : 'text-foreground/80'}>
                  {getNodeIcon(node.type)}
                </g>
                {isThreat && <circle r="35" className="fill-transparent stroke-red-500" style={{filter: 'url(#glow)'}} />}
              </g>
            );
          })}

          {/* Hovered Device Info */}
          {(() => {
            if (!hoveredDevice) return null;
            const device = nodePositions.find(d => d.id === hoveredDevice);
            if (!device) return null;
            const status = getNodeStatus(device);
            return (
              <g transform={`translate(${device.x + 40}, ${device.y - 30})`}>
                <rect x="0" y="0" width="180" height="70" rx="8" className="fill-background/90 stroke-border" />
                <text x="12" y="22" className="text-sm font-bold fill-foreground">{device.hostname}</text>
                <text x="12" y="40" className="text-xs fill-muted-foreground font-mono">{device.id}</text>
                <text x="12" y="58" className="text-xs fill-muted-foreground">
                  Status: <tspan className={`font-medium ${status === 'threat' ? 'fill-red-500' : 'fill-green-500'}`}>{status}</tspan>
                </text>
              </g>
            );
          })()}
        </svg>
      </Card>
    </div>
  );
}