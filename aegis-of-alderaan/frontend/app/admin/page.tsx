"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  Users,
  Activity,
  AlertTriangle,
  Wifi,
  Server,
  Play,
  RefreshCw,
  Network,
  Brain,
  Zap,
  Cpu,
  CheckCircle,
  XCircle,
  PowerOff,
} from "lucide-react";
import { apiService } from "../../lib/api";
import {
  NetworkStatus,
  PeerInfo,
  HealingStrategy,
  AttackSimulationPayload,
} from "../../types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "../../components/ui/label";
import { Input } from "../../components/ui/input";
import { useToast } from "../../components/ui/use-toast";

type AttackType = "cpu_spike" | "memory_leak" | "network_flood";
type AttackIntensity = "low" | "medium" | "high";

const PeerCard = ({
  peer,
  onAnalyze,
  onHeal,
  onSimulateAttack,
}: {
  peer: PeerInfo;
  onAnalyze: (id: string) => void;
  onHeal: (id: string) => void;
  onSimulateAttack: (id: string) => void;
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-500";
      case "unhealthy":
        return "text-yellow-500";
      case "healing":
        return "text-blue-500";
      default:
        return "text-red-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className={`h-5 w-5 ${getStatusColor(status)}`} />;
      case "unhealthy":
        return (
          <AlertTriangle className={`h-5 w-5 ${getStatusColor(status)}`} />
        );
      case "healing":
        return <Zap className={`h-5 w-5 ${getStatusColor(status)}`} />;
      default:
        return <XCircle className={`h-5 w-5 ${getStatusColor(status)}`} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-card p-4 rounded-lg border"
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold flex items-center gap-2">
            <Server className="h-5 w-5" /> {peer.node_id}
          </h3>
          <p className="text-sm text-muted-foreground">{peer.address}</p>
        </div>
        <div className="flex items-center gap-2 text-sm font-semibold">
          {getStatusIcon(peer.status)}
          <span className={getStatusColor(peer.status)}>
            {peer.status.charAt(0).toUpperCase() + peer.status.slice(1)}
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="text-sm">
          <div className="flex justify-between items-center">
            <span>CPU</span>
            <span className="font-mono">
              {peer.metrics.cpu_usage.toFixed(1)}%
            </span>
          </div>
          <Progress value={peer.metrics.cpu_usage} className="h-2" />
        </div>
        <div className="text-sm">
          <div className="flex justify-between items-center">
            <span>Memory</span>
            <span className="font-mono">
              {peer.metrics.memory_usage.toFixed(1)}%
            </span>
          </div>
          <Progress value={peer.metrics.memory_usage} className="h-2" />
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border flex justify-between items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAnalyze(peer.node_id)}
        >
          <Brain className="h-4 w-4 mr-1" /> Analyze
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onHeal(peer.node_id)}
        >
          <Zap className="h-4 w-4 mr-1" /> Heal
        </Button>
        <Button
          size="sm"
          variant="destructive"
          onClick={() => onSimulateAttack(peer.node_id)}
        >
          <Cpu className="h-4 w-4 mr-1" /> Attack
        </Button>
      </div>
    </motion.div>
  );
};

const AttackSimulationDialog = ({
  open,
  onOpenChange,
  targetNodeId,
  onSimulate,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  targetNodeId: string | null;
  onSimulate: (payload: AttackSimulationPayload) => void;
}) => {
  const [attackType, setAttackType] = useState<AttackType>("cpu_spike");
  const [intensity, setIntensity] = useState<AttackIntensity>("medium");
  const [duration, setDuration] = useState(30);
  const { toast } = useToast();

  const handleSimulate = () => {
    if (!targetNodeId) return;
    const payload: AttackSimulationPayload = {
      attack_type: attackType,
      target_agent: targetNodeId,
      params: {
        duration_seconds: duration,
        intensity: intensity,
      },
    };
    onSimulate(payload);
    toast({
      title: "Attack Simulation Started",
      description: `Simulating ${attackType} on ${targetNodeId}.`,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Simulate Attack on {targetNodeId}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="attack-type">Attack Type</Label>
            <Select
              value={attackType}
              onValueChange={(v: AttackType) => setAttackType(v)}
            >
              <SelectTrigger id="attack-type">
                <SelectValue placeholder="Select attack type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cpu_spike">CPU Spike</SelectItem>
                <SelectItem value="memory_leak">Memory Leak</SelectItem>
                <SelectItem value="network_flood">Network Flood</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="intensity">Intensity</Label>
            <Select
              value={intensity}
              onValueChange={(v: AttackIntensity) => setIntensity(v)}
            >
              <SelectTrigger id="intensity">
                <SelectValue placeholder="Select intensity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="duration">Duration (seconds)</Label>
            <Input
              id="duration"
              type="number"
              value={duration}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDuration(parseInt(e.target.value, 10))}
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={handleSimulate}>
            <Play className="h-4 w-4 mr-2" />
            Start Simulation
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const HealingDialog = ({
  open,
  onOpenChange,
  targetNodeId,
  healingStrategy,
  onConfirm,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  targetNodeId: string | null;
  healingStrategy: HealingStrategy | null;
  onConfirm: (nodeId: string, strategy: HealingStrategy) => void;
}) => {
  if (!healingStrategy || !targetNodeId) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>AI Healing Strategy for {targetNodeId}</DialogTitle>
        </DialogHeader>
        <div className="py-4 space-y-4">
          <p>
            The AI has analyzed the issue and suggests the following action:
          </p>
          <Card>
            <CardHeader>
              <CardTitle className="capitalize">
                {healingStrategy.strategy.replace(/_/g, " ")}
              </CardTitle>
              <CardDescription>
                Confidence: {(healingStrategy.confidence * 100).toFixed(1)}%
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>{healingStrategy.details}</p>
              <p className="text-sm text-muted-foreground mt-2">
                Estimated time: {healingStrategy.estimated_time_seconds}s
              </p>
            </CardContent>
          </Card>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={() => onConfirm(targetNodeId, healingStrategy)}>
            <Zap className="h-4 w-4 mr-2" />
            Execute Healing
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default function AdminPanel() {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [isAttackDialogOpen, setAttackDialogOpen] = useState(false);
  const [isHealingDialogOpen, setHealingDialogOpen] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [currentHealingStrategy, setCurrentHealingStrategy] =
    useState<HealingStrategy | null>(null);
  const { toast } = useToast();

  const fetchNetworkStatus = useCallback(async () => {
    try {
      setError(null);
      const status = await apiService.getNetworkStatus();
      setNetworkStatus(status);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
      console.error("Error fetching network status:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNetworkStatus();

    apiService.connectWebSocket();

    const unsubscribeConnection = apiService.subscribe(
      "connection",
      (data) => {
        if ('status' in data) {
          setWsConnected(data.status === "connected");
        }
      }
    );

    const unsubscribeUpdates = apiService.subscribe(
      "network_update",
      (data) => {
        if ('node_id' in data) {
          setNetworkStatus(data);
          toast({
            title: "Network Updated",
            description: "Received real-time update from the Guardian.",
          });
        }
      }
    );

    return () => {
      unsubscribeConnection();
      unsubscribeUpdates();
      apiService.disconnectWebSocket();
    };
  }, [fetchNetworkStatus, toast]);

  const handleAnalyze = async (nodeId: string) => {
    toast({
      title: `Analyzing ${nodeId}...`,
      description: "Requesting AI health analysis.",
    });
    try {
      const result = await apiService.runAIAnalysis(nodeId);
      toast({
        title: "Analysis Started",
        description: `AI is now analyzing ${result.agent_id}.`,
      });
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Analysis Failed",
        description: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  const handleHeal = async (nodeId: string) => {
    toast({ title: `Getting healing strategy for ${nodeId}...` });
    try {
      const strategy = await apiService.getHealingStrategy(nodeId);
      setCurrentHealingStrategy(strategy);
      setSelectedNodeId(nodeId);
      setHealingDialogOpen(true);
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Failed to Get Strategy",
        description: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  const handleConfirmHealing = async (
    nodeId: string,
    strategy: HealingStrategy
  ) => {
    toast({ title: `Executing healing on ${nodeId}...` });
    try {
      await apiService.coordinateHealing(nodeId, strategy);
      toast({
        title: "Healing Initiated",
        description: `Coordinating healing for ${nodeId}.`,
      });
      setHealingDialogOpen(false);
      fetchNetworkStatus(); // Refresh status after action
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Healing Failed",
        description: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  const handleSimulateAttack = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    setAttackDialogOpen(true);
  };

  const handleConfirmAttack = async (payload: AttackSimulationPayload) => {
    try {
      await apiService.simulateAttack(payload);
      toast({
        title: "Attack Simulation Started",
        description: `Simulating ${payload.attack_type} on ${payload.target_agent}.`,
      });
      fetchNetworkStatus(); // Refresh status after action
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Attack Failed",
        description: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p>Loading Aegis Network Status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-6 w-6 text-destructive" /> Connection
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <Button onClick={fetchNetworkStatus} className="mt-4">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const peers = Object.values(networkStatus?.peers || {});

  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-6 bg-background text-foreground">
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary" />
            Aegis Guardian Panel
          </h1>
          <p className="text-muted-foreground">
            Central command for the distributed security network.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={wsConnected ? "default" : "destructive"}
            className="gap-1"
          >
            {wsConnected ? (
              <Wifi className="h-4 w-4" />
            ) : (
              <PowerOff className="h-4 w-4" />
            )}
            {wsConnected ? "Real-time On" : "Disconnected"}
          </Badge>
          <Button onClick={fetchNetworkStatus} variant="outline" size="icon">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Network Health
            </CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">Secure</div>
            <p className="text-xs text-muted-foreground">
              No active threats detected
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Connected Peers
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {networkStatus?.connected_peers || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {networkStatus?.healthy_peers || 0} healthy
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Guardian Status
            </CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Active</div>
            <p className="text-xs text-muted-foreground">
              {networkStatus?.node_id}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Last Update</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {networkStatus
                ? new Date(networkStatus.last_updated).toLocaleTimeString()
                : "N/A"}
            </div>
            <p className="text-xs text-muted-foreground">
              From Guardian server
            </p>
          </CardContent>
        </Card>
      </div>

      <main>
        <h2 className="text-2xl font-semibold mb-4">Peer Network</h2>
        {peers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {peers.map((peer) => (
              <PeerCard
                key={peer.node_id}
                peer={peer}
                onAnalyze={handleAnalyze}
                onHeal={handleHeal}
                onSimulateAttack={handleSimulateAttack}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 border-2 border-dashed rounded-lg">
            <Server className="h-12 w-12 mx-auto text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium">No Peers Connected</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Waiting for peer agents to connect to the network...
            </p>
          </div>
        )}
      </main>

      <AttackSimulationDialog
        open={isAttackDialogOpen}
        onOpenChange={setAttackDialogOpen}
        targetNodeId={selectedNodeId}
        onSimulate={handleConfirmAttack}
      />

      <HealingDialog
        open={isHealingDialogOpen}
        onOpenChange={setHealingDialogOpen}
        targetNodeId={selectedNodeId}
        healingStrategy={currentHealingStrategy}
        onConfirm={handleConfirmHealing}
      />
    </div>
  );
}
