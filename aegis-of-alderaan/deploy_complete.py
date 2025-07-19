#!/usr/bin/env python3
"""
Aegis of Alderaan - Complete Deployment Script
Deploy Guardian + Multiple Agents + Neo4j Relationships all at once
"""

import subprocess
import time
import sys
import os
import requests

class AegisDeployment:
    def __init__(self):
        self.services = [
            "aegis-guardian",
            "aegis-agent-1", 
            "aegis-agent-2",
            "aegis-agent-3",
            "aegis-relationships"
        ]
    
    def check_requirements(self):
        """Check if Docker and docker-compose are available"""
        print("🔍 Checking deployment requirements...")
        
        try:
            # Check Docker
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not found. Please install Docker first.")
            return False
        
        try:
            # Check docker-compose
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose not found. Please install docker-compose.")
            return False
        
        # Check .env file
        if os.path.exists(".env"):
            print("✅ Environment file (.env) found")
        else:
            print("❌ .env file not found. Please create it with your database credentials.")
            return False
        
        return True
    
    def build_images(self):
        """Build Docker images"""
        print("\n🏗️ Building Docker images...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "build", "--no-cache"],
                check=True,
                text=True
            )
            print("✅ Docker images built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build images: {e}")
            return False
    
    def deploy_services(self):
        """Deploy all services"""
        print("\n🚀 Deploying Aegis services...")
        
        try:
            # Start services in order
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                check=True,
                text=True
            )
            print("✅ Services deployed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy services: {e}")
            return False
    
    def wait_for_guardian(self, timeout=120):
        """Wait for Guardian to be healthy"""
        print("\n⏳ Waiting for Guardian server to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:3001/health", timeout=5)
                if response.status_code == 200:
                    health = response.json()
                    print(f"✅ Guardian is healthy: {health}")
                    return True
            except:
                pass
            
            print(".", end="", flush=True)
            time.sleep(5)
        
        print(f"\n❌ Guardian failed to start within {timeout} seconds")
        return False
    
    def check_agent_connections(self):
        """Check if agents are connected"""
        print("\n👥 Checking agent connections...")
        
        try:
            response = requests.get("http://localhost:3001/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                
                print(f"📊 Connected agents: {len(agents)}")
                for agent in agents:
                    agent_id = agent.get('agent_id', 'unknown')
                    hostname = agent.get('hostname', 'unknown')
                    status = agent.get('status', 'unknown')
                    print(f"  🤖 {agent_id} ({hostname}) - {status}")
                
                return len(agents) > 0
            else:
                print(f"❌ Failed to get agents: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking agents: {e}")
            return False
    
    def check_neo4j_topology(self):
        """Check Neo4j topology"""
        print("\n🗺️ Checking Neo4j topology...")
        
        try:
            response = requests.get("http://localhost:3001/network/topology", timeout=10)
            if response.status_code == 200:
                data = response.json()
                topology = data.get('topology', {})
                nodes = topology.get('nodes', [])
                edges = topology.get('edges', [])
                
                print(f"📊 Neo4j nodes: {len(nodes)}")
                print(f"🔗 Neo4j relationships: {len(edges)}")
                
                if edges:
                    print("Relationship types:")
                    rel_types = {}
                    for edge in edges:
                        rel_type = edge.get('relationship_type', 'unknown')
                        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                    
                    for rel_type, count in rel_types.items():
                        print(f"  • {rel_type}: {count}")
                
                return len(nodes) > 0 and len(edges) > 0
            else:
                print(f"❌ Failed to get topology: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking topology: {e}")
            return False
    
    def show_status(self):
        """Show deployment status"""
        print("\n📊 Deployment Status:")
        
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get status: {e}")
    
    def show_logs(self, service=None, tail=20):
        """Show service logs"""
        if service:
            print(f"\n📝 Logs for {service} (last {tail} lines):")
            try:
                result = subprocess.run(
                    ["docker-compose", "logs", "--tail", str(tail), service],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to get logs: {e}")
        else:
            print(f"\n📝 All service logs (last {tail} lines each):")
            for svc in self.services:
                print(f"\n--- {svc} ---")
                self.show_logs(svc, 10)
    
    def deploy_complete_system(self):
        """Deploy the complete Aegis system"""
        print("🛡️ Aegis of Alderaan - Complete System Deployment")
        print("="*60)
        
        # Step 1: Check requirements
        if not self.check_requirements():
            print("❌ Requirements not met. Aborting deployment.")
            return False
        
        # Step 2: Build images
        if not self.build_images():
            print("❌ Build failed. Aborting deployment.")
            return False
        
        # Step 3: Deploy services
        if not self.deploy_services():
            print("❌ Deployment failed.")
            return False
        
        # Step 4: Wait for Guardian
        if not self.wait_for_guardian():
            print("❌ Guardian failed to start.")
            self.show_logs("aegis-guardian")
            return False
        
        # Step 5: Check agents
        time.sleep(10)  # Give agents time to connect
        if not self.check_agent_connections():
            print("⚠️ Some agents may not be connected yet.")
            self.show_logs("aegis-agent-1", 10)
        
        # Step 6: Check Neo4j (after relationship setup)
        time.sleep(15)  # Give relationship manager time to run
        self.check_neo4j_topology()
        
        # Step 7: Show final status
        self.show_status()
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print("✅ Guardian Server: http://localhost:3001")
        print("✅ API Documentation: http://localhost:3001/docs")
        print("✅ Health Check: http://localhost:3001/health")
        print("✅ Multiple agents connected and monitoring")
        print("✅ Neo4j relationships established")
        print("\n🔧 Management Commands:")
        print("  • View logs: docker-compose logs -f")
        print("  • Stop system: docker-compose down")
        print("  • Restart: docker-compose restart")
        print("  • Scale agents: docker-compose up -d --scale aegis-agent-1=3")
        
        return True

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "logs":
            deployment = AegisDeployment()
            service = sys.argv[2] if len(sys.argv) > 2 else None
            deployment.show_logs(service)
        elif sys.argv[1] == "status":
            deployment = AegisDeployment()
            deployment.show_status()
        elif sys.argv[1] == "down":
            print("🛑 Stopping Aegis system...")
            subprocess.run(["docker-compose", "down"])
        else:
            print("Usage: python deploy_complete.py [logs|status|down]")
    else:
        deployment = AegisDeployment()
        deployment.deploy_complete_system()

if __name__ == "__main__":
    main()
