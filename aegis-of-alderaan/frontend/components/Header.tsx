import { ConnectionStatus, SystemStatus } from '../types';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';

interface HeaderProps {
  connectionStatus: ConnectionStatus;
  systemStatus: SystemStatus;
}

export default function Header({ connectionStatus, systemStatus }: HeaderProps) {
  const getStatusColor = (status: SystemStatus['status']) => {
    switch (status) {
      case 'secure': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'under_attack': return 'bg-red-500';
      case 'responding': return 'bg-blue-500';
      case 'healing': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: SystemStatus['status']) => {
    switch (status) {
      case 'secure': return 'SECURE';
      case 'warning': return 'WARNING';
      case 'under_attack': return 'UNDER ATTACK';
      case 'responding': return 'RESPONDING';
      case 'healing': return 'HEALING';
      default: return 'UNKNOWN';
    }
  };

  return (
    <header className="bg-card border-b border-border px-8 py-6">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-2xl font-bold text-white">🛡️</span>
          </div>
          <div className="space-y-1">
            <h1 className="text-3xl font-bold text-foreground">
              Aegis of Alderaan
            </h1>
            <p className="text-base text-muted-foreground font-medium">Distributed AI Security Platform</p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center space-x-8">
          {/* System Status */}
          <div className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full shadow-lg animate-pulse ${getStatusColor(systemStatus.status)}`}></div>
            <div className="space-y-1">
              <Badge 
                variant={systemStatus.status === 'secure' ? 'default' : 'destructive'} 
                className="text-sm font-bold"
              >
                Status: {getStatusText(systemStatus.status)}
              </Badge>
            </div>
          </div>

          <Separator orientation="vertical" className="h-12" />

          {/* Service Availability */}
          <div className="flex items-center space-x-4 min-w-48">
            <div className="space-y-2 flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">Service Availability</span>
                <span className="text-sm font-bold text-green-400">
                  {systemStatus.serviceAvailability.toFixed(1)}%
                </span>
              </div>
              <Progress 
                value={systemStatus.serviceAvailability} 
                className="h-2"
              />
            </div>
          </div>

          <Separator orientation="vertical" className="h-12" />

          {/* Connection Status */}
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full shadow-lg ${
              connectionStatus.status === 'connected' ? 'bg-green-500 animate-pulse shadow-green-500/50' :
              connectionStatus.status === 'reconnecting' ? 'bg-yellow-500 animate-ping shadow-yellow-500/50' :
              'bg-red-500 shadow-red-500/50'
            }`}></div>
            <div className="space-y-1">
              <Badge variant={connectionStatus.status === 'connected' ? 'default' : 'secondary'} className="text-xs">
                {connectionStatus.status === 'connected' ? 'Connected' :
                 connectionStatus.status === 'reconnecting' ? 'Reconnecting...' :
                 'Disconnected'}
              </Badge>
            </div>
          </div>

          <Separator orientation="vertical" className="h-12" />

          {/* Current Time */}
          <div className="text-right space-y-1">
            <div className="text-xs text-muted-foreground">Current Time</div>
            <div className="text-sm font-mono text-foreground">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
