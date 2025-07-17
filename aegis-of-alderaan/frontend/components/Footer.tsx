import { Device, Threat, ConnectionStatus, SystemStatus } from '../types';
import { Separator } from './ui/separator';

interface FooterProps {
  devices: Device[];
  threats: Threat[];
  connectionStatus: ConnectionStatus;
  systemStatus: SystemStatus;
}

export default function Footer({ devices, threats, connectionStatus, systemStatus }: FooterProps) {
  return (
    <footer className="border-t border-border bg-background/95 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center space-x-4">
            <span>&copy; {new Date().getFullYear()} Aegis of Alderaan</span>
            <Separator orientation="vertical" className="h-4" />
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${systemStatus.autoRecoveryActive ? 'bg-blue-500' : 'bg-gray-500'}`}></div>
              <span>Auto-Recovery: {systemStatus.autoRecoveryActive ? 'Active' : 'Inactive'}</span>
            </div>
            <Separator orientation="vertical" className="h-4" />
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${systemStatus.aiProtectionActive ? 'bg-purple-500' : 'bg-gray-500'}`}></div>
              <span>AI Protection: {systemStatus.aiProtectionActive ? 'Active' : 'Inactive'}</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span>Avg. Response: <span className="text-foreground">{systemStatus.avgResponseTime.toFixed(1)}ms</span></span>
            <Separator orientation="vertical" className="h-4" />
            <span>Threats Blocked: <span className="text-foreground">{systemStatus.threatsBlocked}</span></span>
          </div>
        </div>
      </div>
    </footer>
  );
}
