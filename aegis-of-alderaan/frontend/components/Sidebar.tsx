import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import { SystemStatus } from '../types';
import { Network, BarChart2, ShieldAlert, Server, FlaskConical, Power } from 'lucide-react';

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  systemStatus: SystemStatus;
}

export default function Sidebar({ activeView, onViewChange, systemStatus }: SidebarProps) {
  const menuItems = [
    { id: 'network', label: 'Network', icon: <Network className="w-6 h-6" /> },
    { id: 'metrics', label: 'Metrics', icon: <BarChart2 className="w-6 h-6" /> },
    { 
      id: 'threats', 
      label: 'Threats', 
      icon: <ShieldAlert className="w-6 h-6" />,
      badge: systemStatus.activeThreats > 0 ? systemStatus.activeThreats : null
    },
    { 
      id: 'devices', 
      label: 'Devices', 
      icon: <Server className="w-6 h-6" />,
      badge: systemStatus.totalDevices - systemStatus.healthyDevices > 0 ? 
             systemStatus.totalDevices - systemStatus.healthyDevices : null
    },
    { id: 'demo', label: 'Demo', icon: <FlaskConical className="w-6 h-6" /> }
  ];

  return (
    <aside className="w-20 bg-background border-r border-border p-4 flex flex-col items-center space-y-8 sticky top-0 h-screen">
      {/* Logo */}
      <div className="w-10 h-10 bg-foreground rounded-lg flex items-center justify-center">
        <Power className="w-6 h-6 text-background" />
      </div>

      {/* Collapsed Menu Items */}
      <div className="space-y-2">
        {menuItems.map((item) => (
          <TooltipProvider key={item.id} delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={() => onViewChange(item.id)}
                  variant={activeView === item.id ? "secondary" : "ghost"}
                  className="w-14 h-14 rounded-lg relative flex items-center justify-center"
                >
                  {item.icon}
                  {item.badge && (
                    <Badge 
                      variant="destructive" 
                      className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs rounded-full"
                    >
                      {item.badge}
                    </Badge>
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>{item.label}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ))}
      </div>

      <div className="flex-grow" />

      {/* System Status Indicators */}
      <div className="space-y-4">
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger>
              <div className={`w-3 h-3 rounded-full ${systemStatus.status === 'secure' ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></div>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>System Status: {systemStatus.status}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger>
              <div className={`w-3 h-3 rounded-full ${systemStatus.aiProtectionActive ? 'bg-blue-500' : 'bg-gray-500'}`}></div>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>AI Protection: {systemStatus.aiProtectionActive ? 'Active' : 'Inactive'}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </aside>
  );
}
