"""
Aegis of Alderaan - Agent Manager
Core agent management and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

class AgentManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.components = {}
        self.running = False
        
    async def register_component(self, name: str, component):
        """Register a component with the manager"""
        self.components[name] = component
        self.logger.info(f"Registered component: {name}")
    
    async def start_all_components(self):
        """Start all registered components"""
        self.logger.info("Starting all components")
        self.running = True
        
        tasks = []
        for name, component in self.components.items():
            if hasattr(component, 'start'):
                tasks.append(component.start())
                self.logger.info(f"Starting component: {name}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all_components(self):
        """Stop all registered components"""
        self.logger.info("Stopping all components")
        self.running = False
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    await component.stop()
                    self.logger.info(f"Stopped component: {name}")
            except Exception as e:
                self.logger.error(f"Error stopping component {name}: {e}")
    
    def get_component(self, name: str):
        """Get a registered component by name"""
        return self.components.get(name)
    
    def get_status(self) -> Dict:
        """Get status of all components"""
        status = {
            'running': self.running,
            'components': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'get_status'):
                    status['components'][name] = component.get_status()
                else:
                    status['components'][name] = 'active'
            except Exception as e:
                status['components'][name] = f'error: {e}'
        
        return status
