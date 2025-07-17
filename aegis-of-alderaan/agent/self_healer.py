"""
Aegis of Alderaan - Self Healer
Handles agent recovery, mirroring, and failover mechanisms
"""

import asyncio
import logging
import psutil
import subprocess
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp

class SelfHealer:
    def __init__(self, config, communicator):
        self.config = config
        self.communicator = communicator
        self.logger = logging.getLogger(__name__)
        
        self.running = False
        self.health_status = 'healthy'
        self.mirror_agent_url = None
        self.recovery_actions = []
        
        # Health check parameters
        self.last_health_check = datetime.utcnow()
        self.consecutive_failures = 0
        self.max_failures = 3
        
        # Recovery strategies
        self.recovery_strategies = {
            'high_cpu': self.recover_high_cpu,
            'high_memory': self.recover_high_memory,
            'network_failure': self.recover_network,
            'disk_full': self.recover_disk_space,
            'process_failure': self.recover_process
        }
    
    async def start(self):
        """Start self-healing monitoring"""
        self.logger.info("Starting self-healing service")
        self.running = True
        
        while self.running:
            try:
                await self.perform_health_check()
                await self.check_mirror_status()
                await asyncio.sleep(self.config['failover']['health_check_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in self-healer: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stop self-healing service"""
        self.logger.info("Stopping self-healing service")
        self.running = False
    
    async def perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            health_report = await self.generate_health_report()
            
            if health_report['overall_status'] == 'unhealthy':
                await self.initiate_recovery(health_report)
            else:
                self.consecutive_failures = 0
                self.health_status = 'healthy'
                
            self.last_health_check = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.max_failures:
                await self.initiate_failover()
    
    async def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        try:
            # System resource checks
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process checks
            process_count = len(psutil.pids())
            
            # Network connectivity check
            network_healthy = await self.check_network_connectivity()
            
            # Communication check
            comm_healthy = self.communicator.is_connected()
            
            # Determine overall health
            issues = []
            
            if cpu_percent > 95:
                issues.append('high_cpu')
            if memory.percent > 95:
                issues.append('high_memory')
            if disk.percent > 95:
                issues.append('disk_full')
            if not network_healthy:
                issues.append('network_failure')
            if not comm_healthy:
                issues.append('communication_failure')
                
            overall_status = 'unhealthy' if issues else 'healthy'
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': overall_status,
                'issues': issues,
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'process_count': process_count
                },
                'connectivity': {
                    'network': network_healthy,
                    'guardian': comm_healthy
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating health report: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'unknown',
                'error': str(e)
            }
    
    async def check_network_connectivity(self) -> bool:
        """Check network connectivity"""
        try:
            # Try to reach Guardian server
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.config['guardian']['http_url']}/health") as response:
                    return response.status == 200
        except:
            return False
    
    async def initiate_recovery(self, health_report: Dict):
        """Initiate recovery based on health issues"""
        issues = health_report.get('issues', [])
        
        self.logger.warning(f"Health issues detected: {issues}")
        
        for issue in issues:
            if issue in self.recovery_strategies:
                try:
                    await self.recovery_strategies[issue](health_report)
                    await self.log_recovery_action(issue, 'attempted')
                except Exception as e:
                    self.logger.error(f"Recovery failed for {issue}: {e}")
                    await self.log_recovery_action(issue, 'failed', str(e))
    
    async def recover_high_cpu(self, health_report: Dict):
        """Recover from high CPU usage"""
        self.logger.info("Attempting CPU recovery")
        
        # Kill high CPU processes (if safe)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 50:  # High CPU processes
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Kill non-essential high CPU processes
        for proc_info in processes[:3]:  # Limit to 3 processes
            try:
                proc = psutil.Process(proc_info['pid'])
                if proc_info['name'] not in ['python', 'aegis-agent']:  # Don't kill ourselves
                    proc.terminate()
                    self.logger.info(f"Terminated process {proc_info['name']} (PID: {proc_info['pid']})")
            except Exception as e:
                self.logger.error(f"Failed to terminate process: {e}")
    
    async def recover_high_memory(self, health_report: Dict):
        """Recover from high memory usage"""
        self.logger.info("Attempting memory recovery")
        
        # Clear system caches (if possible)
        try:
            if hasattr(psutil, 'virtual_memory'):
                # Force garbage collection in Python
                import gc
                gc.collect()
                
        except Exception as e:
            self.logger.error(f"Memory recovery failed: {e}")
    
    async def recover_network(self, health_report: Dict):
        """Recover from network issues"""
        self.logger.info("Attempting network recovery")
        
        try:
            # Restart network service (Windows)
            subprocess.run(['ipconfig', '/release'], check=False, capture_output=True)
            await asyncio.sleep(2)
            subprocess.run(['ipconfig', '/renew'], check=False, capture_output=True)
            
        except Exception as e:
            self.logger.error(f"Network recovery failed: {e}")
    
    async def recover_disk_space(self, health_report: Dict):
        """Recover disk space"""
        self.logger.info("Attempting disk space recovery")
        
        try:
            # Clean temporary files
            import tempfile
            import shutil
            
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                try:
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Disk recovery failed: {e}")
    
    async def recover_process(self, health_report: Dict):
        """Recover from process failures"""
        self.logger.info("Attempting process recovery")
        
        # Restart critical services if needed
        # This would be implementation-specific
        pass
    
    async def initiate_failover(self):
        """Initiate failover to mirror agent"""
        self.logger.critical("Initiating failover due to consecutive failures")
        
        try:
            # Notify Guardian of failover
            await self.communicator.send_alert(
                'failover_initiated',
                f'Agent {self.config["agent"]["id"]} initiating failover',
                'critical'
            )
            
            # Try to contact mirror agent
            if self.mirror_agent_url:
                await self.transfer_to_mirror()
            
            # Set agent to recovery mode
            self.health_status = 'recovering'
            
        except Exception as e:
            self.logger.error(f"Failover failed: {e}")
    
    async def transfer_to_mirror(self):
        """Transfer responsibilities to mirror agent"""
        try:
            transfer_data = {
                'type': 'takeover_request',
                'from_agent': self.config['agent']['id'],
                'timestamp': datetime.utcnow().isoformat(),
                'reason': 'health_failure'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mirror_agent_url}/takeover",
                    json=transfer_data
                ) as response:
                    if response.status == 200:
                        self.logger.info("Successfully transferred to mirror agent")
                    else:
                        self.logger.error(f"Mirror transfer failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Failed to transfer to mirror: {e}")
    
    async def check_mirror_status(self):
        """Check status of mirror agent"""
        if not self.mirror_agent_url:
            return
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.mirror_agent_url}/health") as response:
                    if response.status != 200:
                        self.logger.warning("Mirror agent not responding")
                        
        except Exception as e:
            self.logger.warning(f"Mirror check failed: {e}")
    
    async def log_recovery_action(self, action_type: str, status: str, error: str = None):
        """Log recovery action"""
        action = {
            'timestamp': datetime.utcnow().isoformat(),
            'action_type': action_type,
            'status': status,
            'agent_id': self.config['agent']['id'],
            'error': error
        }
        
        self.recovery_actions.append(action)
        
        # Send to Guardian
        await self.communicator.send_message({
            'type': 'recovery_action',
            'data': action
        })
    
    def set_mirror_agent(self, mirror_url: str):
        """Set mirror agent URL"""
        self.mirror_agent_url = mirror_url
        self.logger.info(f"Mirror agent set: {mirror_url}")
    
    def get_health_status(self) -> str:
        """Get current health status"""
        return self.health_status
    
    def get_recovery_history(self) -> List[Dict]:
        """Get recovery action history"""
        return self.recovery_actions[-10:]  # Last 10 actions
