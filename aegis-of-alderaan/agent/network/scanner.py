"""
Aegis of Alderaan - Network Scanner
Network discovery and monitoring utilities
"""

import asyncio
import socket
import logging
import subprocess
import os
from typing import Dict, List, Optional
from datetime import datetime
import ipaddress

class NetworkScanner:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def scan_local_network(self) -> List[Dict]:
        """Scan local network for active hosts"""
        active_hosts = []
        
        try:
            # Get local IP and network
            local_ip = self.get_local_ip()
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            
            self.logger.info(f"Scanning network: {network}")
            
            # Scan network hosts
            tasks = []
            for ip in network.hosts():
                tasks.append(self.ping_host(str(ip)))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, dict) and result.get('reachable'):
                    active_hosts.append(result)
                    
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
        
        return active_hosts
    
    async def ping_host(self, ip: str, timeout: int = 2) -> Dict:
        """Ping a host to check if it's reachable"""
        try:
            # Use system ping command
            if os.name == 'nt':  # Windows
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip]
            else:  # Unix-like
                cmd = ['ping', '-c', '1', '-W', str(timeout), ip]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if ping was successful
            reachable = process.returncode == 0
            
            result = {
                'ip': ip,
                'reachable': reachable,
                'response_time': None
            }
            
            if reachable:
                # Try to extract response time from output
                output = stdout.decode()
                result['hostname'] = await self.get_hostname(ip)
                # Parse response time if needed
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Ping failed for {ip}: {e}")
            return {
                'ip': ip,
                'reachable': False,
                'error': str(e)
            }
    
    async def get_hostname(self, ip: str) -> Optional[str]:
        """Get hostname for an IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return None
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    async def port_scan(self, ip: str, ports: List[int]) -> Dict:
        """Scan specific ports on a host"""
        open_ports = []
        
        for port in ports:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=2
                )
                writer.close()
                await writer.wait_closed()
                open_ports.append(port)
            except Exception:
                pass  # Port is closed or filtered
        
        return {
            'ip': ip,
            'open_ports': open_ports,
            'scanned_ports': ports
        }
    
    async def discover_peers(self) -> List[Dict]:
        """Discover other Aegis agents on the network"""
        peers = []
        
        # Scan for agents on common ports
        active_hosts = await self.scan_local_network()
        agent_port = self.config['agent'].get('port', 8080)
        
        for host in active_hosts:
            if host['reachable']:
                # Try to connect to agent port
                try:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(host['ip'], agent_port),
                        timeout=3
                    )
                    
                    # Send identification request
                    writer.write(b'AEGIS_IDENTIFY\n')
                    await writer.drain()
                    
                    # Read response
                    data = await asyncio.wait_for(reader.read(1024), timeout=2)
                    response = data.decode().strip()
                    
                    writer.close()
                    await writer.wait_closed()
                    
                    if response.startswith('AEGIS_AGENT'):
                        peers.append({
                            'ip': host['ip'],
                            'hostname': host.get('hostname'),
                            'agent_info': response,
                            'discovered_at': datetime.utcnow().isoformat()
                        })
                        
                except Exception:
                    pass  # Not an Aegis agent
        
        return peers
