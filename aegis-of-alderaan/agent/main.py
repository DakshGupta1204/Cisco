#!/usr/bin/env python3
"""
Aegis of Alderaan - Agent Entry Point
Main orchestrator for the resilient network protection agent
"""

import asyncio
import logging
import signal
import sys
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from metrics_collector import MetricsCollector
from communicator import Communicator
from anomaly_detector import AnomalyDetector
from self_healer import SelfHealer
from jwt_auth import JWTAuth

class AegisAgent:
    def __init__(self, config_path="config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        
        # Initialize components
        self.jwt_auth = JWTAuth(self.config['security']['jwt_secret'])
        self.metrics_collector = MetricsCollector(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)
        self.communicator = Communicator(self.config, self.jwt_auth)
        self.self_healer = SelfHealer(self.config, self.communicator)
        
        # Connect components
        self.anomaly_detector.set_metrics_collector(self.metrics_collector)
        self.anomaly_detector.set_communicator(self.communicator)  # 🔧 FIX: Connect anomaly detector to communicator
        self.metrics_collector.set_communicator(self.communicator)
        
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            config_file = Path(__file__).parent / config_path
            with open(config_file, 'r') as f:
                config_content = f.read()
            
            # Replace environment variables in the content
            import re
            
            def replace_env_var(match):
                var_expr = match.group(1)
                if ':-' in var_expr:
                    # Handle ${VAR:-default} syntax
                    var_name, default_value = var_expr.split(':-', 1)
                    return os.getenv(var_name, default_value)
                else:
                    # Handle ${VAR} syntax
                    return os.getenv(var_expr, match.group(0))
            
            # Replace ${VAR} and ${VAR:-default} patterns
            config_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, config_content)
            
            # Parse the YAML after environment variable substitution
            config = yaml.safe_load(config_content)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config['logging']
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler()
            ]
        )
    
    async def start(self):
        """Start the agent with all components"""
        self.logger.info(f"Starting Aegis Agent: {self.config['agent']['id']}")
        self.running = True
        
        try:
            # Start all components
            tasks = [
                self.metrics_collector.start(),
                self.communicator.start(),
                self.anomaly_detector.start(),
                self.self_healer.start(),
                self.heartbeat_loop()
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Error starting agent: {e}")
            await self.stop()
    
    async def stop(self):
        """Gracefully stop all components"""
        self.logger.info("Stopping Aegis Agent...")
        self.running = False
        
        # Stop all components
        await self.metrics_collector.stop()
        await self.communicator.stop()
        await self.anomaly_detector.stop()
        await self.self_healer.stop()
        
        self.logger.info("Agent stopped")
    
    async def heartbeat_loop(self):
        """Send periodic heartbeat to Guardian"""
        while self.running:
            try:
                await self.communicator.send_heartbeat()
                await asyncio.sleep(self.config['guardian']['heartbeat_interval'])
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())

async def main():
    """Main entry point"""
    agent = AegisAgent()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, agent.signal_handler)
    signal.signal(signal.SIGTERM, agent.signal_handler)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await agent.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
