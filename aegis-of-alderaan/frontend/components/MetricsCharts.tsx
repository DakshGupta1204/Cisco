import { useState } from 'react';
import { Device, NetworkMetrics, SystemStatus } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Cpu, MemoryStick, Network, Server, Bot } from 'lucide-react';

interface MetricsChartsProps {
  metrics: NetworkMetrics[];
  devices: Device[];
  systemStatus: SystemStatus;
}

const DeviceDetailModal = ({ device, metrics }: { device: Device, metrics: NetworkMetrics[] }) => {
  const deviceMetrics = metrics
    .filter(m => m.deviceId === device.id)
    .map(m => ({
      time: new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      cpu: m.cpu,
      memory: m.memory,
      network: m.network,
    }));

  return (
    <DialogContent className="max-w-4xl">
      <DialogHeader>
        <DialogTitle className="flex items-center space-x-2">
          <Server className="w-5 h-5" />
          <span>{device.hostname}</span>
        </DialogTitle>
      </DialogHeader>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        <div className="md:col-span-1">
          <h3 className="font-semibold mb-2">Details</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">ID:</span>
              <span className="font-mono">{device.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">IP Address:</span>
              <span className="font-mono">{device.ipAddress}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <span className={`font-medium ${device.status === 'healthy' ? 'text-green-500' : 'text-red-500'}`}>{device.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Last Seen:</span>
              <span>{new Date(device.lastSeen).toLocaleString()}</span>
            </div>
          </div>
          <h3 className="font-semibold mb-2 mt-6">Software Agents</h3>
          <div className="space-y-2">
            {device.agents.map(agent => (
              <div key={agent.id} className="flex items-center justify-between text-xs p-2 rounded-md bg-muted/50">
                <div className="flex items-center space-x-2">
                  <Bot className="w-4 h-4 text-muted-foreground" />
                  <span>{agent.name}</span>
                </div>
                <span className={`font-medium ${agent.status === 'running' ? 'text-green-500' : 'text-red-500'}`}>{agent.status}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="md:col-span-2">
          <h3 className="font-semibold mb-2">Live Metrics</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm w-16">CPU</span>
              <Progress value={device.metrics.cpu} className="h-2 flex-1" />
              <span className="text-sm font-mono w-12 text-right">{device.metrics.cpu.toFixed(1)}%</span>
            </div>
            <div className="flex items-center space-x-2">
              <MemoryStick className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm w-16">Memory</span>
              <Progress value={device.metrics.memory} className="h-2 flex-1" />
              <span className="text-sm font-mono w-12 text-right">{device.metrics.memory.toFixed(1)}%</span>
            </div>
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm w-16">Network</span>
              <Progress value={device.metrics.network} className="h-2 flex-1" />
              <span className="text-sm font-mono w-12 text-right">{device.metrics.network.toFixed(1)}%</span>
            </div>
          </div>
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Performance History</h3>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={deviceMetrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border) / 0.5)" />
                  <XAxis 
                    dataKey="time" 
                    angle={-30}
                    textAnchor="end"
                    height={40}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} 
                    tickLine={false} 
                    axisLine={false} 
                  />
                  <YAxis 
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} 
                    tickLine={false} 
                    axisLine={false} 
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      color: 'hsl(var(--foreground))',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Area type="monotone" dataKey="cpu" stroke="#ef4444" fill="#ef4444" fillOpacity={0.1} strokeWidth={2} />
                  <Area type="monotone" dataKey="memory" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.1} strokeWidth={2} />
                  <Area type="monotone" dataKey="network" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </DialogContent>
  )
}

export default function MetricsCharts({ metrics, devices, systemStatus }: MetricsChartsProps) {
  const [timeRange, setTimeRange] = useState<'15m' | '1h' | '6h' | '24h'>('1h');
  const [activeTab, setActiveTab] = useState<'cpu' | 'memory' | 'network'>('cpu');
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);

  const timeRangeInMinutes = { '15m': 15, '1h': 60, '6h': 360, '24h': 1440 };
  
  const now = new Date();
  const timeCutoff = new Date(now.getTime() - timeRangeInMinutes[timeRange] * 60 * 1000);

  const filteredMetrics = metrics.filter(m => new Date(m.timestamp) > timeCutoff);

  const chartData = filteredMetrics.map(m => ({
    time: new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    cpu: m.cpu,
    memory: m.memory,
    network: m.network,
  }));

  const tabConfig = {
    cpu: { color: '#ef4444', name: 'CPU Usage' },
    memory: { color: '#f59e0b', name: 'Memory Usage' },
    network: { color: '#3b82f6', name: 'Network Traffic' },
  };

  return (
    <Dialog onOpenChange={(isOpen) => !isOpen && setSelectedDevice(null)}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-2xl font-light tracking-wide text-foreground">System Metrics</h2>
            <p className="text-sm text-muted-foreground">
              Live performance monitoring and threat analysis.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Select value={timeRange} onValueChange={(value: '15m' | '1h' | '6h' | '24h') => setTimeRange(value)}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Time range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15m">Last 15m</SelectItem>
                <SelectItem value="1h">Last 1h</SelectItem>
                <SelectItem value="6h">Last 6h</SelectItem>
                <SelectItem value="24h">Last 24h</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Main Chart */}
        <Card>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="w-full">
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle className="text-lg font-medium">{tabConfig[activeTab].name}</CardTitle>
              <TabsList className="grid w-full max-w-xs grid-cols-3">
                <TabsTrigger value="cpu">CPU</TabsTrigger>
                <TabsTrigger value="memory">Memory</TabsTrigger>
                <TabsTrigger value="network">Network</TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent className="p-4 h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id={`color-${activeTab}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={tabConfig[activeTab].color} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={tabConfig[activeTab].color} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border) / 0.5)" />
                  <XAxis 
                    dataKey="time" 
                    angle={-30}
                    textAnchor="end"
                    height={40}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} 
                    tickLine={false} 
                    axisLine={false} 
                  />
                  <YAxis 
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} 
                    tickLine={false} 
                    axisLine={false} 
                    unit="%" 
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      color: 'hsl(var(--foreground))',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Area type="monotone" dataKey={activeTab} stroke={tabConfig[activeTab].color} fill={`url(#color-${activeTab})`} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Tabs>
        </Card>

        {/* Device-specific metrics */}
        <div>
          <h3 className="text-xl font-light tracking-wide text-foreground mb-4">Device Performance</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {devices.map(device => (
              <DialogTrigger key={device.id} asChild onClick={() => setSelectedDevice(device)}>
                <Card className="cursor-pointer hover:border-primary transition-colors group">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg font-semibold tracking-tight group-hover:text-primary">{device.hostname}</CardTitle>
                      <div className={`w-2.5 h-2.5 rounded-full ${device.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    </div>
                    <p className="text-xs text-muted-foreground font-mono">{device.ipAddress}</p>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-0">
                    <div>
                      <div className="flex justify-between items-baseline text-xs mb-1">
                        <span className="text-muted-foreground">CPU</span>
                        <span className="font-mono text-foreground">{device.metrics.cpu.toFixed(1)}%</span>
                      </div>
                      <Progress value={device.metrics.cpu} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between items-baseline text-xs mb-1">
                        <span className="text-muted-foreground">Memory</span>
                        <span className="font-mono text-foreground">{device.metrics.memory.toFixed(1)}%</span>
                      </div>
                      <Progress value={device.metrics.memory} className="h-1.5" />
                    </div>
                    <div>
                      <div className="flex justify-between items-baseline text-xs mb-1">
                        <span className="text-muted-foreground">Network</span>
                        <span className="font-mono text-foreground">{device.metrics.network.toFixed(1)}%</span>
                      </div>
                      <Progress value={device.metrics.network} className="h-1.5" />
                    </div>
                  </CardContent>
                </Card>
              </DialogTrigger>
            ))}
          </div>
        </div>
      </div>
      {selectedDevice && <DeviceDetailModal device={selectedDevice} metrics={filteredMetrics} />}
    </Dialog>
  );
}