#!/usr/bin/env python3
"""
Aegis of Alderaan - Quick Launch with Neo4j Features
Launch Guardian, Agent, and test Neo4j relationships & self-healing
"""

import subprocess
import asyncio
import time
import os
import sys
import signal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AegisLauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def cleanup(self):
        """Clean up all processes"""
        logger.info("🧹 Cleaning up processes...")
        for process in self.processes:
            try:
                if process.poll() is None:  # Process still running
                    process.terminate()
                    process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        self.processes.clear()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Shutdown signal received")
        self.cleanup()
        sys.exit(0)
    
    def start_guardian_server(self):
        """Start Guardian server"""
        logger.info("🛡️ Starting Guardian Server...")
        guardian_dir = os.path.join(self.base_dir, "guardian-server")
        
        try:
            process = subprocess.Popen(
                ["python", "app.py"],
                cwd=guardian_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes.append(process)
            logger.info("✅ Guardian Server process started")
            return process
        except Exception as e:
            logger.error(f"❌ Failed to start Guardian Server: {e}")
            return None
    
    def start_agent(self):
        """Start an agent"""
        logger.info("🤖 Starting Agent...")
        agent_dir = os.path.join(self.base_dir, "agent")
        
        try:
            process = subprocess.Popen(
                ["python", "main.py"],
                cwd=agent_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes.append(process)
            logger.info("✅ Agent process started")
            return process
        except Exception as e:
            logger.error(f"❌ Failed to start Agent: {e}")
            return None
    
    def monitor_process_output(self, process, name, max_lines=10):
        """Monitor process output"""
        lines_shown = 0
        try:
            for line in process.stdout:
                if lines_shown < max_lines:
                    print(f"[{name}] {line.strip()}")
                    lines_shown += 1
                elif lines_shown == max_lines:
                    print(f"[{name}] ... (output continues)")
                    lines_shown += 1
        except:
            pass
    
    async def wait_for_services(self, timeout=30):
        """Wait for services to be ready"""
        logger.info("⏳ Waiting for services to start...")
        
        import aiohttp
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:3001/health", timeout=2) as response:
                        if response.status == 200:
                            logger.info("✅ Guardian Server is ready!")
                            return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.warning("⚠️ Services may not be fully ready")
        return False
    
    async def run_neo4j_tests(self, test_type="comprehensive"):
        """Run Neo4j relationship tests"""
        logger.info("🧪 Running Neo4j relationship and self-healing tests...")
        
        try:
            # Import and run the test
            if test_type == "quick":
                from test_neo4j_relationships import run_quick_demo
                await run_quick_demo()
            else:
                from test_neo4j_relationships import run_comprehensive_test
                await run_comprehensive_test()
                
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
    
    async def interactive_demo(self):
        """Run interactive demo"""
        logger.info("🎮 Starting Interactive Neo4j Demo")
        
        while True:
            print("\n" + "="*50)
            print("AEGIS NEO4J FEATURES DEMO")
            print("="*50)
            print("1. Test Mirror Relationships")
            print("2. Test Monitoring Relationships") 
            print("3. Test Network Connections")
            print("4. Test Self-Healing")
            print("5. View Network Topology")
            print("6. View Mirror Topology")
            print("7. Run Quick Demo")
            print("8. Run Full Test Suite")
            print("9. Exit")
            print("="*50)
            
            choice = input("Select option (1-9): ").strip()
            
            try:
                if choice == "1":
                    await self.test_mirror_relationships()
                elif choice == "2":
                    await self.test_monitoring_relationships()
                elif choice == "3":
                    await self.test_network_connections()
                elif choice == "4":
                    await self.test_self_healing()
                elif choice == "5":
                    await self.view_network_topology()
                elif choice == "6":
                    await self.view_mirror_topology()
                elif choice == "7":
                    await self.run_neo4j_tests("quick")
                elif choice == "8":
                    await self.run_neo4j_tests("comprehensive")
                elif choice == "9":
                    break
                else:
                    print("Invalid choice. Please select 1-9.")
                
                input("\nPress Enter to continue...")
                
            except Exception as e:
                logger.error(f"Error in demo: {e}")
                input("\nPress Enter to continue...")
    
    async def test_mirror_relationships(self):
        """Test mirror relationships"""
        print("🪞 Testing Mirror Relationships...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.create_mirror_relationship("test_primary", "test_mirror")
            await tester.get_agent_mirrors("test_primary")
    
    async def test_monitoring_relationships(self):
        """Test monitoring relationships"""
        print("👁️ Testing Monitoring Relationships...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.create_monitoring_relationship("monitor_agent", "target_agent")
    
    async def test_network_connections(self):
        """Test network connections"""
        print("🌐 Testing Network Connections...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.create_network_connection("node1", "node2", "CONNECTED_TO")
    
    async def test_self_healing(self):
        """Test self-healing"""
        print("🩺 Testing Self-Healing...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.initiate_self_healing("failing_agent")
            await tester.get_active_healing_processes()
    
    async def view_network_topology(self):
        """View network topology"""
        print("🗺️ Viewing Network Topology...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.get_network_topology()
    
    async def view_mirror_topology(self):
        """View mirror topology"""
        print("🪞 Viewing Mirror Topology...")
        from test_neo4j_relationships import Neo4jRelationshipTester
        
        async with Neo4jRelationshipTester() as tester:
            await tester.get_mirror_topology()

async def main():
    """Main launch function"""
    launcher = AegisLauncher()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, launcher.signal_handler)
    signal.signal(signal.SIGTERM, launcher.signal_handler)
    
    try:
        logger.info("🚀 Starting Aegis of Alderaan with Neo4j Features")
        
        # Start Guardian Server
        guardian_process = launcher.start_guardian_server()
        if not guardian_process:
            logger.error("❌ Failed to start Guardian Server")
            return
        
        # Wait for Guardian to start
        await asyncio.sleep(5)
        
        # Start Agent
        agent_process = launcher.start_agent()
        if not agent_process:
            logger.error("❌ Failed to start Agent")
            launcher.cleanup()
            return
        
        # Wait for services to be ready
        await launcher.wait_for_services()
        
        # Show some output from processes
        print("\n" + "="*60)
        print("RECENT GUARDIAN OUTPUT:")
        print("="*60)
        launcher.monitor_process_output(guardian_process, "Guardian", 5)
        
        print("\n" + "="*60)
        print("RECENT AGENT OUTPUT:")
        print("="*60)
        launcher.monitor_process_output(agent_process, "Agent", 5)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--quick":
                await launcher.run_neo4j_tests("quick")
            elif sys.argv[1] == "--full":
                await launcher.run_neo4j_tests("comprehensive")
            elif sys.argv[1] == "--demo":
                await launcher.interactive_demo()
        else:
            print("\n" + "🎯 AEGIS LAUNCHED SUCCESSFULLY!")
            print("Options:")
            print("  • Add --quick for quick Neo4j demo")
            print("  • Add --full for comprehensive tests")
            print("  • Add --demo for interactive demo")
            print("  • Press Ctrl+C to stop all services")
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        
    except Exception as e:
        logger.error(f"❌ Launch failed: {e}")
    finally:
        launcher.cleanup()
        logger.info("👋 Aegis shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
