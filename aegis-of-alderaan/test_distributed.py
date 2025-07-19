#!/usr/bin/env python3
"""
Aegis of Alderaan - Distributed System Tester
Tests JWT authentication and peer connections
"""

import requests
import json
import time
import sys
from datetime import datetime

class DistributedSystemTester:
    def __init__(self, guardian_ip="localhost", guardian_port=3001):
        self.guardian_url = f"http://{guardian_ip}:{guardian_port}"
        self.test_results = []
        
    def log_test(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status} {test_name}: {message}"
        print(log_entry)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": timestamp
        })
        
    def test_guardian_health(self):
        """Test Guardian server health"""
        try:
            response = requests.get(f"{self.guardian_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                self.log_test("Guardian Health", True, f"Services: {list(services.keys())}")
                return True
            else:
                self.log_test("Guardian Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Guardian Health", False, str(e))
            return False
    
    def test_token_generation(self):
        """Test JWT token generation"""
        try:
            node_info = {
                "node_id": "test-peer-001",
                "hostname": "test-computer",
                "ip_address": "192.168.1.100",
                "node_type": "peer",
                "capabilities": ["metrics_collection", "health_monitoring"]
            }
            
            response = requests.post(
                f"{self.guardian_url}/distributed/node-token",
                json=node_info,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    self.test_token = token  # Store for next test
                    self.log_test("Token Generation", True, f"Token length: {len(token)}")
                    return True
                else:
                    self.log_test("Token Generation", False, "No token in response")
                    return False
            else:
                self.log_test("Token Generation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Token Generation", False, str(e))
            return False
    
    def test_token_validation(self):
        """Test JWT token validation"""
        if not hasattr(self, 'test_token'):
            self.log_test("Token Validation", False, "No token available from previous test")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.test_token}"}
            response = requests.get(
                f"{self.guardian_url}/distributed/nodes",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Token Validation", True, f"Nodes: {data.get('data', {}).get('total_nodes', 0)}")
                return True
            else:
                self.log_test("Token Validation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Token Validation", False, str(e))
            return False
    
    def test_peer_registration(self):
        """Test peer node registration"""
        if not hasattr(self, 'test_token'):
            self.log_test("Peer Registration", False, "No token available")
            return False
            
        try:
            peer_info = {
                "node_id": "test-peer-001",
                "hostname": "test-computer",
                "ip_address": "192.168.1.100",
                "port": 3002,
                "jwt_token": self.test_token,
                "capabilities": ["metrics_collection", "health_monitoring"],
                "system_metrics": {
                    "cpu_percent": 25.5,
                    "memory_percent": 45.2,
                    "disk_usage": 60.1,
                    "network_connections": 15
                }
            }
            
            headers = {"Authorization": f"Bearer {self.test_token}"}
            response = requests.post(
                f"{self.guardian_url}/distributed/register",
                json=peer_info,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Peer Registration", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Peer Registration", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Peer Registration", False, str(e))
            return False
    
    def test_distributed_topology(self):
        """Test distributed network topology"""
        if not hasattr(self, 'test_token'):
            self.log_test("Distributed Topology", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.test_token}"}
            response = requests.get(
                f"{self.guardian_url}/distributed/topology",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                topology = data.get('data', {})
                nodes = topology.get('network_topology', {}).get('total_nodes', 0)
                health = topology.get('system_health', {}).get('overall_health', 'unknown')
                self.log_test("Distributed Topology", True, f"Nodes: {nodes}, Health: {health}")
                return True
            else:
                self.log_test("Distributed Topology", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Distributed Topology", False, str(e))
            return False
    
    def test_broadcast_message(self):
        """Test message broadcasting"""
        if not hasattr(self, 'test_token'):
            self.log_test("Broadcast Message", False, "No token available")
            return False
            
        try:
            message_data = {
                "type": "test_broadcast",
                "data": {
                    "test_id": "test-001",
                    "message": "Hello from distributed tester!"
                }
            }
            
            headers = {"Authorization": f"Bearer {self.test_token}"}
            response = requests.post(
                f"{self.guardian_url}/distributed/broadcast",
                json=message_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                recipients = data.get('recipients', 0)
                self.log_test("Broadcast Message", True, f"Sent to {recipients} recipients")
                return True
            else:
                self.log_test("Broadcast Message", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Broadcast Message", False, str(e))
            return False
    
    def test_ai_endpoints(self):
        """Test AI-powered endpoints"""
        try:
            # Test AI health analysis
            response = requests.post(
                f"{self.guardian_url}/ai/analyze/health/test-agent-001",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_enabled = data.get('ai_enabled', False)
                analysis = data.get('analysis', {})
                confidence = analysis.get('confidence_score', 0)
                self.log_test("AI Health Analysis", True, f"AI: {ai_enabled}, Confidence: {confidence}")
                return True
            else:
                self.log_test("AI Health Analysis", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Health Analysis", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Aegis Distributed System Tests")
        print("=" * 50)
        
        tests = [
            self.test_guardian_health,
            self.test_token_generation,
            self.test_token_validation,
            self.test_peer_registration,
            self.test_distributed_topology,
            self.test_broadcast_message,
            self.test_ai_endpoints
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            success = test()
            if success:
                passed += 1
            else:
                failed += 1
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 50)
        print(f"🧪 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Distributed system is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return failed == 0
    
    def generate_test_report(self):
        """Generate detailed test report"""
        report = f"""# Aegis Distributed System Test Report

**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Guardian URL:** {self.guardian_url}

## Test Results Summary

| Test | Status | Message |
|------|--------|---------|
"""
        
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            report += f"| {result['test']} | {status_icon} | {result['message']} |\n"
        
        passed = sum(1 for r in self.test_results if r['success'])
        failed = sum(1 for r in self.test_results if not r['success'])
        
        report += f"""
## Summary
- **Total Tests:** {len(self.test_results)}
- **Passed:** {passed}
- **Failed:** {failed}
- **Success Rate:** {(passed / len(self.test_results) * 100):.1f}%

## Recommendations

{'🎉 **All systems operational!** Your distributed network is ready for production use.' if failed == 0 else '⚠️ **Issues detected.** Please review failed tests and check system configuration.'}

### Next Steps
1. Verify all computers are connected to the same network
2. Ensure JWT tokens are properly distributed to peer computers
3. Check firewall settings allow communication on ports 3001 and 3002
4. Monitor system health through the admin panel

---
*Generated by Aegis Distributed System Tester*
"""
        
        with open("distributed_test_report.md", "w") as f:
            f.write(report)
        
        print("📊 Test report saved to: distributed_test_report.md")

def main():
    if len(sys.argv) > 1:
        guardian_ip = sys.argv[1]
    else:
        guardian_ip = input("Enter Guardian IP address (or press Enter for localhost): ").strip()
        if not guardian_ip:
            guardian_ip = "localhost"
    
    print(f"🎯 Testing Guardian at: {guardian_ip}:3001")
    
    tester = DistributedSystemTester(guardian_ip)
    success = tester.run_all_tests()
    tester.generate_test_report()
    
    if success:
        print("\n🚀 Your distributed system is ready!")
        print(f"🎛️  Admin Panel: http://{guardian_ip}:3000/admin")
        print(f"🔗 API Docs: http://{guardian_ip}:3001/docs")
    else:
        print("\n🔧 Please fix the issues and run the test again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
