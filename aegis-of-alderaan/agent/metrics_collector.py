"""
Aegis of Alderaan - Metrics Collector
Collects system metrics (CPU, RAM, Disk, Network) from endpoints
"""

import asyncio
import psutil
import time
import logging
from datetime import datetime
from typing import Dict, List
import json

class MetricsCollector:
    def __init__(self, config, communicator=None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.metrics_buffer = []
        self.last_network_stats = None
        self.communicator = communicator
        
    def set_communicator(self, communicator):
        """Set the communicator for sending metrics"""
        self.communicator = communicator
        
    async def start(self):
        """Start collecting metrics"""
        self.logger.info("Starting metrics collection")
        self.running = True
        
        # Initialize network stats
        self.last_network_stats = psutil.net_io_counters()
        
        while self.running:
            try:
                metrics = await self.collect_system_metrics()
                self.metrics_buffer.append(metrics)
                
                # Send metrics to Guardian if communicator is available
                if self.communicator:
                    try:
                        await self.communicator.send_metrics(metrics)
                        self.logger.debug(f"Sent metrics: CPU={metrics.get('cpu_percent', 0):.1f}%, Memory={metrics.get('memory_percent', 0):.1f}%")
                        print(f"Metrics sent: CPU={metrics.get('cpu_percent', 0):.1f}%")  # Debug output
                    except Exception as e:
                        self.logger.warning(f"Failed to send metrics: {e}")
                        print(f"Failed to send metrics: {e}")  # Debug output
                
                # Keep buffer size manageable
                if len(self.metrics_buffer) > self.config['metrics']['batch_size']:
                    self.metrics_buffer = self.metrics_buffer[-self.config['metrics']['batch_size']:]
                
                await asyncio.sleep(self.config['metrics']['collection_interval'])
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop metrics collection"""
        self.logger.info("Stopping metrics collection")
        self.running = False
    
    async def collect_system_metrics(self) -> Dict:
        """Collect comprehensive system metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        # CPU metrics - Use non-blocking measurement
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Shorter interval
        cpu_count = psutil.cpu_count()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics - Use Windows drive letter
        try:
            disk_usage = psutil.disk_usage('C:\\')
        except:
            # Fallback to current directory
            disk_usage = psutil.disk_usage('.')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network_stats = psutil.net_io_counters()
        network_speed = self.calculate_network_speed(network_stats)
        
        # Process metrics
        process_count = len(psutil.pids())
        
        # System uptime
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        metrics = {
            'agent_id': self.config['agent']['id'],
            'hostname': self.config['agent']['hostname'],
            'timestamp': timestamp,
            # Flat format for easy access
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk_usage.percent,
            # Detailed nested format
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'load_avg': load_avg
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            },
            'disk': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent,
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0
            },
            'network': {
                'bytes_sent': network_stats.bytes_sent,
                'bytes_recv': network_stats.bytes_recv,
                'packets_sent': network_stats.packets_sent,
                'packets_recv': network_stats.packets_recv,
                'speed_mbps': network_speed
            },
            'system': {
                'process_count': process_count,
                'uptime': uptime,
                'boot_time': boot_time
            }
        }
        
        # Add network interface details
        network_interfaces = self.get_network_interfaces()
        metrics['network']['interfaces'] = network_interfaces
        
        return metrics
    
    def calculate_network_speed(self, current_stats) -> float:
        """Calculate network speed in Mbps"""
        if self.last_network_stats is None:
            self.last_network_stats = current_stats
            return 0.0
        
        time_delta = self.config['metrics']['collection_interval']
        bytes_delta = (current_stats.bytes_sent + current_stats.bytes_recv) - \
                     (self.last_network_stats.bytes_sent + self.last_network_stats.bytes_recv)
        
        # Convert to Mbps
        speed_mbps = (bytes_delta * 8) / (time_delta * 1024 * 1024)
        
        self.last_network_stats = current_stats
        return round(speed_mbps, 2)
    
    def get_network_interfaces(self) -> List[Dict]:
        """Get detailed network interface information"""
        interfaces = []
        
        for interface_name, addresses in psutil.net_if_addrs().items():
            interface_stats = psutil.net_if_stats().get(interface_name)
            
            interface_info = {
                'name': interface_name,
                'is_up': interface_stats.isup if interface_stats else False,
                'speed': interface_stats.speed if interface_stats else 0,
                'addresses': []
            }
            
            for addr in addresses:
                address_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                }
                interface_info['addresses'].append(address_info)
            
            interfaces.append(interface_info)
        
        return interfaces
    
    def get_latest_metrics(self) -> Dict:
        """Get the most recent metrics"""
        return self.metrics_buffer[-1] if self.metrics_buffer else {}
    
    def get_metrics_batch(self) -> List[Dict]:
        """Get all buffered metrics and clear the buffer"""
        batch = self.metrics_buffer.copy()
        self.metrics_buffer.clear()
        return batch
    
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """Check if metrics exceed configured thresholds"""
        alerts = []
        monitoring_config = self.config['monitoring']
        
        # CPU threshold
        if metrics['cpu']['percent'] > monitoring_config['cpu_threshold']:
            alerts.append({
                'type': 'cpu_high',
                'value': metrics['cpu']['percent'],
                'threshold': monitoring_config['cpu_threshold'],
                'severity': 'warning' if metrics['cpu']['percent'] < 95 else 'critical'
            })
        
        # Memory threshold
        if metrics['memory']['percent'] > monitoring_config['memory_threshold']:
            alerts.append({
                'type': 'memory_high',
                'value': metrics['memory']['percent'],
                'threshold': monitoring_config['memory_threshold'],
                'severity': 'warning' if metrics['memory']['percent'] < 95 else 'critical'
            })
        
        # Disk threshold
        if metrics['disk']['percent'] > monitoring_config['disk_threshold']:
            alerts.append({
                'type': 'disk_high',
                'value': metrics['disk']['percent'],
                'threshold': monitoring_config['disk_threshold'],
                'severity': 'warning' if metrics['disk']['percent'] < 98 else 'critical'
            })
        
        # Network threshold
        if metrics['network']['speed_mbps'] > monitoring_config['network_threshold']:
            alerts.append({
                'type': 'network_high',
                'value': metrics['network']['speed_mbps'],
                'threshold': monitoring_config['network_threshold'],
                'severity': 'info'
            })
        
        return alerts
