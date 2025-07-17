import { useState } from 'react';
import { Device, Threat } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { LayoutGrid, List, Server, Database, Router, Smartphone, ShieldCheck, ShieldAlert, Shield, Cpu, MemoryStick, Network, Computer } from 'lucide-react';

interface DeviceStatusProps {
  devices: Device[];
  threats?: Threat[];
}

export default function DeviceStatus({ devices, threats = [] }: DeviceStatusProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const getStatusConfig = (status: Device['status']) => {
    switch (status) {
      case 'healthy': return { variant: 'default' as const, icon: <ShieldCheck className="w-4 h-4 text-green-500" />, color: 'text-green-500', bg: 'bg-green-500/10' };
      case 'warning': return { variant: 'secondary' as const, icon: <ShieldAlert className="w-4 h-4 text-yellow-500" />, color: 'text-yellow-500', bg: 'bg-yellow-500/10' };
      case 'under_attack': return { variant: 'destructive' as const, icon: <ShieldAlert className="w-4 h-4 text-red-500" />, color: 'text-red-500', bg: 'bg-red-500/10' };
      case 'quarantined': return { variant: 'destructive' as const, icon: <Shield className="w-4 h-4 text-gray-500" />, color: 'text-gray-500', bg: 'bg-gray-500/10' };
      case 'healing': return { variant: 'outline' as const, icon: <Shield className="w-4 h-4 text-blue-500" />, color: 'text-blue-500', bg: 'bg-blue-500/10' };
      default: return { variant: 'secondary' as const, icon: <Shield className="w-4 h-4 text-gray-400" />, color: 'text-gray-400', bg: 'bg-gray-400/10' };
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'web_server': return <Server className="w-5 h-5 text-muted-foreground" />;
      case 'database': return <Database className="w-5 h-5 text-muted-foreground" />;
      case 'load_balancer': return <Router className="w-5 h-5 text-muted-foreground" />;
      case 'iot_device': return <Smartphone className="w-5 h-5 text-muted-foreground" />;
      case 'computer': return <Computer className="w-5 h-5 text-muted-foreground" />;
      default: return <Server className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const filteredDevices = devices.filter(device => {
    if (filterStatus === 'all') return true;
    return device.status === filterStatus;
  });

  const statusCounts = devices.reduce((acc, device) => {
    acc[device.status] = (acc[device.status] || 0) + 1;
    return acc;
  }, {} as Record<Device['status'], number>);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-light tracking-tight text-foreground">
            Device Status
          </h2>
          <p className="text-muted-foreground">
            Detailed view of all connected devices and their health metrics.
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="healthy">Healthy</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="under_attack">Under Attack</SelectItem>
              <SelectItem value="healing">Healing</SelectItem>
              <SelectItem value="quarantined">Quarantined</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="flex bg-muted p-1 rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="px-2 py-1 h-auto"
            >
              <LayoutGrid className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="px-2 py-1 h-auto"
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Statistics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total</p>
            <p className="text-3xl font-bold text-foreground">{devices.length}</p>
          </CardContent>
        </Card>
        {Object.entries(statusCounts).map(([status, count]) => {
          const config = getStatusConfig(status as Device['status']);
          return (
            <Card key={status}>
              <CardContent className="p-4">
                <p className={`text-sm capitalize ${config.color}`}>{status.replace('_', ' ')}</p>
                <p className={`text-3xl font-bold ${config.color}`}>{count}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Device Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredDevices.map((device) => {
            const statusConfig = getStatusConfig(device.status);
            return (
              <Card key={device.id} className={`hover:border-primary/50 transition-colors border ${statusConfig.bg} border-transparent`}>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      {getTypeIcon(device.type)}
                      <div>
                        <CardTitle className="text-base font-semibold">{device.hostname}</CardTitle>
                        <p className="text-xs text-muted-foreground font-mono">{device.ipAddress}</p>
                      </div>
                    </div>
                    <div className={`p-1.5 rounded-full ${statusConfig.bg}`}>
                      {statusConfig.icon}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3 pt-2">
                  <div className="space-y-2 text-xs">
                    <div className="flex items-center">
                      <Cpu className="w-4 h-4 mr-2 text-muted-foreground" />
                      <span className="w-12 text-muted-foreground">CPU</span>
                      <Progress value={device.metrics.cpu} className="h-1.5 flex-1" />
                      <span className="w-12 text-right font-mono">{device.metrics.cpu.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center">
                      <MemoryStick className="w-4 h-4 mr-2 text-muted-foreground" />
                      <span className="w-12 text-muted-foreground">Memory</span>
                      <Progress value={device.metrics.memory} className="h-1.5 flex-1" />
                      <span className="w-12 text-right font-mono">{device.metrics.memory.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center">
                      <Network className="w-4 h-4 mr-2 text-muted-foreground" />
                      <span className="w-12 text-muted-foreground">Network</span>
                      <Progress value={device.metrics.network} className="h-1.5 flex-1" />
                      <span className="w-12 text-right font-mono">{device.metrics.network.toFixed(1)}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        /* List View */
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Device</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">CPU</TableHead>
                <TableHead className="text-right">Memory</TableHead>
                <TableHead className="text-right">Network</TableHead>
                <TableHead>Last Seen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDevices.map((device) => {
                const statusConfig = getStatusConfig(device.status);
                return (
                  <TableRow key={device.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        {getTypeIcon(device.type)}
                        <div>
                          <div className="font-medium">{device.hostname}</div>
                          <div className="text-xs text-muted-foreground font-mono">{device.ipAddress}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusConfig.variant} className={`text-xs capitalize ${statusConfig.bg} ${statusConfig.color}`}>
                        {device.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">{device.metrics.cpu.toFixed(1)}%</TableCell>
                    <TableCell className="text-right font-mono">{device.metrics.memory.toFixed(1)}%</TableCell>
                    <TableCell className="text-right font-mono">{device.metrics.network.toFixed(1)}%</TableCell>
                    <TableCell>{new Date(device.lastSeen).toLocaleTimeString()}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>
      )}
    </div>
  );
}
