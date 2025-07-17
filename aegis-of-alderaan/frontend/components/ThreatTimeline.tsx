import { Threat, Device } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ShieldAlert, ShieldCheck, Hourglass, Search, AlertTriangle, CheckCircle, Shield, Bot } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';

interface ThreatTimelineProps {
  threats: Threat[];
  devices: Device[];
}

export default function ThreatTimeline({ threats, devices }: ThreatTimelineProps) {
  const deviceMap = new Map(devices.map(d => [d.id, d]));

  const getSeverityConfig = (severity: Threat['severity']) => {
    switch (severity) {
      case 'critical': return { color: 'border-red-500/50 bg-red-500/10 text-red-500', icon: <AlertTriangle className="w-4 h-4" /> };
      case 'high': return { color: 'border-orange-500/50 bg-orange-500/10 text-orange-500', icon: <AlertTriangle className="w-4 h-4" /> };
      case 'medium': return { color: 'border-yellow-500/50 bg-yellow-500/10 text-yellow-500', icon: <AlertTriangle className="w-4 h-4" /> };
      case 'low': return { color: 'border-blue-500/50 bg-blue-500/10 text-blue-500', icon: <Shield className="w-4 h-4" /> };
      default: return { color: 'border-gray-500/50 bg-gray-500/10 text-gray-500', icon: <Shield className="w-4 h-4" /> };
    }
  };

  const getStatusIcon = (status: Threat['status']) => {
    switch (status) {
      case 'detected': return <ShieldAlert className="w-5 h-5 text-red-500" />;
      case 'responding': return <Hourglass className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'resolved': return <ShieldCheck className="w-5 h-5 text-green-500" />;
      case 'analyzing': return <Search className="w-5 h-5 text-blue-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return new Date(timestamp).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-1">
        <h2 className="text-3xl font-light tracking-tight text-foreground">
          Threat Timeline
        </h2>
        <p className="text-muted-foreground">
          Real-time security events and AI-powered threat detection.
        </p>
      </div>

      {/* Threat Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Threats</p>
            <p className="text-3xl font-bold text-foreground">{threats.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Critical</p>
            <p className="text-3xl font-bold text-red-500">
              {threats.filter(t => t.severity === 'critical').length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Resolved</p>
            <p className="text-3xl font-bold text-green-500">
              {threats.filter(t => t.status === 'resolved').length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Analyzing</p>
            <p className="text-3xl font-bold text-blue-500">
              {threats.filter(t => t.status === 'analyzing').length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      <Card>
        <CardContent className="p-0">
          <Accordion type="single" collapsible className="w-full">
            {threats.map((threat, index) => {
              const severityConfig = getSeverityConfig(threat.severity);
              return (
                <AccordionItem value={`item-${index}`} key={threat.id} className="border-b border-border last:border-b-0">
                  <AccordionTrigger className="px-6 py-4 hover:bg-muted/50 transition-colors font-normal">
                    <div className="flex items-center space-x-4 text-left flex-1">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${severityConfig.color}`}>
                        {severityConfig.icon}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-base tracking-tight text-foreground">{threat.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                        <p className="text-sm text-muted-foreground">{formatTimestamp(threat.timestamp)}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Badge variant={threat.status === 'resolved' ? 'default' : 'outline'} className={`capitalize text-xs ${
                        threat.status === 'resolved' ? 'bg-green-500/10 text-green-600 border-green-500/20' : 
                        threat.status === 'detected' ? 'bg-red-500/10 text-red-600 border-red-500/20' : ''
                      }`}>
                        {threat.status}
                      </Badge>
                      {getStatusIcon(threat.status)}
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-6 pt-2 space-y-6 bg-muted/30">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                      <div className="md:col-span-2">
                        <div className="flex items-start space-x-3">
                          <Bot className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold text-foreground">AI Analysis</p>
                            <p className="text-muted-foreground mt-1">{threat.aiAnalysis.explanation}</p>
                          </div>
                        </div>
                      </div>
                      <div>
                        <div className="flex items-start space-x-3">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold text-foreground">Recommended Actions</p>
                            <ul className="list-none mt-1 space-y-1">
                              {threat.aiAnalysis.recommendedActions.map((action, i) => (
                                <li key={i} className="text-muted-foreground flex items-start">
                                  <span className="mr-2 mt-1">-</span>
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-sm">
                      <p className="font-semibold text-foreground mb-2">Affected Devices</p>
                      <div className="flex flex-wrap gap-2">
                        {threat.affectedDevices.map(deviceId => {
                          const device = deviceMap.get(deviceId);
                          return (
                            <Badge key={deviceId} variant="secondary" className="font-mono">
                              {device ? device.hostname : deviceId}
                            </Badge>
                          );
                        })}
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              )
            })}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}