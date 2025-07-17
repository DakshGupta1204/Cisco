#!/usr/bin/env python3
"""
Test script to verify admin panel button integration with backend endpoints
"""

import requests
import json
import time
from typing import Dict, Any

# Backend server URL
BASE_URL = "http://localhost:3001"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Test a specific endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text
        }
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection refused - server not running"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print("🧪 Testing Admin Panel Backend Integration")
    print("=" * 50)
    
    # Test all endpoints used by admin panel buttons
    tests = [
        # Health check
        ("GET", "/health", None, "Guardian Health Check"),
        
        # Network status (used by admin panel)
        ("GET", "/distributed/network/status", None, "Network Status"),
        
        # AI Analysis button
        ("POST", "/ai/analyze/health/test-agent", None, "AI Health Analysis"),
        
        # Healing Strategy button  
        ("POST", "/ai/healing/strategy/test-agent", None, "Get Healing Strategy"),
        
        # Coordinate Healing button
        ("POST", "/distributed/healing/coordinate", {
            "target_node": "test-agent",
            "healing_strategy": {
                "type": "restart_service",
                "priority": "high",
                "steps": ["stop_service", "clear_cache", "start_service"],
                "estimated_duration": 30
            }
        }, "Coordinate Healing"),
        
        # Attack Simulation button
        ("POST", "/simulate/attack/cpu_spike", {
            "target_agent": "test-agent",
            "intensity": "medium",
            "duration": 10
        }, "Simulate CPU Attack")
    ]
    
    results = []
    
    for method, endpoint, data, description in tests:
        print(f"\n📡 Testing: {description}")
        print(f"   {method} {endpoint}")
        
        result = test_endpoint(method, endpoint, data)
        results.append((description, result))
        
        if result["status"] == "success":
            print(f"   ✅ Status: {result['status_code']}")
            if result["status_code"] == 200:
                print(f"   📄 Response: {json.dumps(result['data'], indent=2)[:200]}...")
        else:
            print(f"   ❌ Error: {result['message']}")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    successful = 0
    for description, result in results:
        status_icon = "✅" if result["status"] == "success" and result.get("status_code") == 200 else "❌"
        print(f"{status_icon} {description}")
        if result["status"] == "success" and result.get("status_code") == 200:
            successful += 1
    
    print(f"\n📊 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    if successful == len(results):
        print("\n🎉 All admin panel buttons are properly integrated with the backend!")
    else:
        print(f"\n⚠️  {len(results) - successful} endpoints need attention")
        print("   Make sure the Guardian server is running: python guardian-server/app.py")

if __name__ == "__main__":
    main()
