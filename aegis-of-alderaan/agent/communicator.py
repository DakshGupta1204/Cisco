"""
Aegis of Alderaan - Communicator
WebSocket client for Guardian server communication
"""

import asyncio
import websockets
import json
import logging
import aiohttp
from datetime import datetime
from typing import Dict, Optional, Callable

class Communicator:
    def __init__(self, config, jwt_auth):
        self.config = config
        self.jwt_auth = jwt_auth
        self.logger = logging.getLogger(__name__)
        
        self.websocket = None
        self.running = False
        self.connected = False
        self.message_handlers = {}
        
        # Authentication token
        self.auth_token = None
        
    async def start(self):
        """Start the communicator with auto-reconnect"""
        self.logger.info("Starting communicator")
        self.running = True
        
        while self.running:
            try:
                await self.connect()
                await self.listen_for_messages()
            except Exception as e:
                self.logger.error(f"Communication error: {e}")
                self.connected = False
                await asyncio.sleep(self.config['guardian']['reconnect_interval'])
    
    async def stop(self):
        """Stop the communicator"""
        self.logger.info("Stopping communicator")
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
            self.connected = False
    
    async def connect(self):
        """Connect to Guardian server"""
        try:
            # First authenticate via HTTP
            await self.authenticate()
            
            # Then establish WebSocket connection
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            self.websocket = await websockets.connect(
                self.config['guardian']['server_url'],
                extra_headers=headers
            )
            
            self.connected = True
            self.logger.info("Connected to Guardian server")
            
            # Send registration message
            await self.register_agent()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Guardian: {e}")
            raise
    
    async def authenticate(self):
        """Authenticate with Guardian server via HTTP"""
        try:
            auth_data = {
                'agent_id': self.config['agent']['id'],
                'hostname': self.config['agent']['hostname'],
                'role': self.config['agent']['role']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['guardian']['http_url']}/auth/agent",
                    json=auth_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data['token']
                        self.logger.info("Authentication successful")
                    else:
                        raise Exception(f"Authentication failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            # Don't use fallback token - raise the error to force retry
            raise
    
    async def register_agent(self):
        """Register agent with Guardian"""
        registration_data = {
            'type': 'register',
            'agent_id': self.config['agent']['id'],
            'hostname': self.config['agent']['hostname'],
            'role': self.config['agent']['role'],
            'capabilities': ['metrics_collection', 'anomaly_detection', 'self_healing'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message(registration_data)
    
    async def listen_for_messages(self):
        """Listen for messages from Guardian"""
        while self.running and self.connected:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                await self.handle_message(data)
                
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("WebSocket connection closed")
                self.connected = False
                break
            except Exception as e:
                self.logger.error(f"Error receiving message: {e}")
                await asyncio.sleep(1)
    
    async def handle_message(self, data: Dict):
        """Handle incoming messages from Guardian"""
        message_type = data.get('type')
        
        if message_type in self.message_handlers:
            await self.message_handlers[message_type](data)
        else:
            self.logger.debug(f"Unhandled message type: {message_type}")
            
        # Default message handling
        if message_type == 'command':
            await self.handle_command(data)
        elif message_type == 'health_check':
            await self.handle_health_check(data)
        elif message_type == 'failover':
            await self.handle_failover(data)
        elif message_type == 'healing_request':
            await self.handle_healing_request(data)
        elif message_type == 'mirror_setup':
            await self.handle_mirror_setup(data)
        elif message_type == 'mirror_activation':
            await self.handle_mirror_activation(data)
        elif message_type == 'mirror_takeover':
            await self.handle_mirror_takeover(data)
    
    async def handle_command(self, data: Dict):
        """Handle command from Guardian"""
        command = data.get('command')
        self.logger.info(f"Received command: {command}")
    
    async def handle_healing_request(self, data: Dict):
        """Handle healing request from Guardian"""
        failed_agent = data.get('failed_agent')
        healing_id = data.get('healing_id')
        
        self.logger.info(f"Healing request received: taking over for {failed_agent}")
        
        try:
            # Simulate healing actions
            healing_success = await self.perform_healing_actions(failed_agent)
            
            # Report healing completion back to Guardian
            completion_message = {
                'type': 'healing_completion',
                'healing_id': healing_id,
                'failed_agent': failed_agent,
                'healing_agent': self.config['agent']['id'],
                'success': healing_success,
                'details': f"Healing {'successful' if healing_success else 'failed'} for {failed_agent}",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.send_message(completion_message)
            
        except Exception as e:
            self.logger.error(f"Healing process failed: {e}")
            # Report failure
            completion_message = {
                'type': 'healing_completion',
                'healing_id': healing_id,
                'failed_agent': failed_agent,
                'healing_agent': self.config['agent']['id'],
                'success': False,
                'details': f"Healing failed: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.send_message(completion_message)
    
    async def perform_healing_actions(self, failed_agent: str) -> bool:
        """Perform healing actions for a failed agent"""
        try:
            self.logger.info(f"Initiating healing procedures for {failed_agent}")
            
            # Simulate healing procedures
            await asyncio.sleep(2)  # Simulate healing time
            
            # Here you would implement actual healing logic:
            # - Take over failed agent's responsibilities
            # - Redirect traffic
            # - Update network configurations
            # - Synchronize data
            
            self.logger.info(f"Healing completed for {failed_agent}")
            return True
            
        except Exception as e:
            self.logger.error(f"Healing actions failed: {e}")
            return False
    
    async def handle_mirror_setup(self, data: Dict):
        """Handle mirror setup notification"""
        primary_agent = data.get('primary_agent')
        mirror_config = data.get('mirror_config', {})
        
        self.logger.info(f"Mirror setup notification: mirroring {primary_agent}")
        
        # Configure local mirroring
        mirror_type = mirror_config.get('type', 'active')
        priority = mirror_config.get('priority', 1)
        
        # Send acknowledgment
        ack_message = {
            'type': 'mirror_setup_ack',
            'primary_agent': primary_agent,
            'mirror_agent': self.config['agent']['id'],
            'mirror_type': mirror_type,
            'priority': priority,
            'status': 'configured',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message(ack_message)
    
    async def handle_mirror_activation(self, data: Dict):
        """Handle mirror activation - this agent becomes active"""
        primary_agent = data.get('primary_agent')
        role = data.get('role', 'active_mirror')
        
        self.logger.info(f"Mirror activation: taking over as active mirror for {primary_agent}")
        
        # Update local configuration
        # Here you would implement mirror activation logic:
        # - Become active for the primary agent's responsibilities
        # - Update local state
        # - Begin active monitoring/processing
        
        # Send confirmation
        confirmation_message = {
            'type': 'mirror_activation_ack',
            'primary_agent': primary_agent,
            'mirror_agent': self.config['agent']['id'],
            'new_role': role,
            'status': 'activated',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message(confirmation_message)
    
    async def handle_mirror_takeover(self, data: Dict):
        """Handle mirror takeover notification - this agent becomes inactive"""
        mirror_agent = data.get('mirror_agent')
        status = data.get('status', 'inactive')
        
        self.logger.info(f"Mirror takeover: {mirror_agent} is taking over, going {status}")
        
        # Update local configuration to inactive
        # Here you would implement takeover logic:
        # - Stop active processes
        # - Update status
        # - Hand over responsibilities
        
        # Send acknowledgment
        ack_message = {
            'type': 'mirror_takeover_ack',
            'original_agent': self.config['agent']['id'],
            'mirror_agent': mirror_agent,
            'new_status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message(ack_message)
    
    async def handle_health_check(self, data: Dict):
        """Handle health check from Guardian"""
        response = {
            'type': 'health_response',
            'agent_id': self.config['agent']['id'],
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_message(response)
    
    async def handle_failover(self, data: Dict):
        """Handle failover instructions"""
        self.logger.warning("Failover initiated by Guardian")
        # Implementation would depend on specific failover requirements
        
    async def send_message(self, data: Dict):
        """Send message to Guardian"""
        if not self.connected or not self.websocket:
            self.logger.warning("Cannot send message: not connected")
            return False
        
        try:
            message = json.dumps(data)
            await self.websocket.send(message)
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def send_metrics(self, metrics: Dict):
        """Send metrics to Guardian"""
        message = {
            'type': 'metrics',
            'data': metrics,
            'agent_id': self.config['agent']['id'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return await self.send_message(message)
    
    async def send_anomaly(self, anomaly: Dict):
        """Send anomaly alert to Guardian"""
        message = {
            'type': 'anomaly',
            'data': anomaly,
            'agent_id': self.config['agent']['id'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return await self.send_message(message)
    
    async def send_heartbeat(self):
        """Send heartbeat to Guardian"""
        heartbeat = {
            'type': 'heartbeat',
            'agent_id': self.config['agent']['id'],
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return await self.send_message(heartbeat)
    
    async def send_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Send alert to Guardian"""
        alert = {
            'type': 'alert',
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'agent_id': self.config['agent']['id'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return await self.send_message(alert)
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register custom message handler"""
        self.message_handlers[message_type] = handler
    
    def is_connected(self) -> bool:
        """Check if connected to Guardian"""
        return self.connected
