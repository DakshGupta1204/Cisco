"""
Test script for Aegis AI-Powered Self-Healing System
Tests Gemini AI integration with Neo4j graph database mirroring
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add the guardian-server to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'guardian-server'))

from gemini_ai_handler import GeminiAIHandler, HealthAnalysis, MirrorRecommendation
from db.neo4j_handler import Neo4jHandler
from db.mongo_handler import MongoHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AISystemTester:
    """Test suite for AI-powered self-healing system"""
    
    def __init__(self):
        self.gemini_ai = GeminiAIHandler()
        self.neo4j_handler = None
        self.mongo_handler = None
        
        try:
            self.neo4j_handler = Neo4jHandler()
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
        
        try:
            self.mongo_handler = MongoHandler()
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}")
    
    async def setup_test_data(self):
        """Setup test data in databases"""
        logger.info("🔧 Setting up test data...")
        
        if self.neo4j_handler:
            try:
                await self.neo4j_handler.connect()
                
                # Create test agents
                test_agents = [
                    {
                        'agent_id': 'test-agent-001',
                        'hostname': 'test-server-1',
                        'role': 'web_server',
                        'status': 'degraded'
                    },
                    {
                        'agent_id': 'test-mirror-001',
                        'hostname': 'test-mirror-1',
                        'role': 'web_server_mirror',
                        'status': 'active'
                    }
                ]
                
                for agent in test_agents:
                    await self.neo4j_handler.create_or_update_agent_node(
                        agent['agent_id'], agent
                    )
                
                # Create mirror relationship
                await self.neo4j_handler.create_mirror_relationship(
                    'test-agent-001', 'test-mirror-001'
                )
                
                # Register health issues
                await self.neo4j_handler.register_health_issue(
                    'test-agent-001', 'high_cpu', 'high',
                    {'cpu_percent': 95, 'memory_percent': 88}
                )
                
                logger.info("✅ Neo4j test data created")
                
            except Exception as e:
                logger.error(f"Failed to setup Neo4j test data: {e}")
        
        if self.mongo_handler:
            try:
                await self.mongo_handler.connect()
                
                # Create test agent data
                test_agent_data = {
                    'agent_id': 'test-agent-001',
                    'hostname': 'test-server-1',
                    'status': 'degraded',
                    'metrics': {
                        'cpu_percent': 95.2,
                        'memory_percent': 88.5,
                        'disk_percent': 67.3,
                        'network_connections': 1024,
                        'load_average': [2.5, 2.3, 2.1]
                    },
                    'anomalies': [
                        {
                            'type': 'cpu_spike',
                            'severity': 'high',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    ],
                    'error_logs': [
                        {
                            'level': 'ERROR',
                            'message': 'Out of memory error in application',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    ]
                }
                
                await self.mongo_handler.upsert_agent(test_agent_data)
                logger.info("✅ MongoDB test data created")
                
            except Exception as e:
                logger.error(f"Failed to setup MongoDB test data: {e}")
    
    async def test_ai_health_analysis(self):
        """Test AI health analysis functionality"""
        logger.info("🧠 Testing AI Health Analysis...")
        
        test_node_data = {
            'agent_id': 'test-agent-001',
            'hostname': 'test-server-1',
            'role': 'web_server',
            'status': 'degraded',
            'last_seen': datetime.utcnow().isoformat(),
            'metrics': {
                'cpu_percent': 95.2,
                'memory_percent': 88.5,
                'disk_percent': 67.3,
                'network_connections': 1024,
                'load_average': [2.5, 2.3, 2.1]
            },
            'anomalies': [
                {
                    'type': 'cpu_spike',
                    'severity': 'high',
                    'timestamp': datetime.utcnow().isoformat()
                },
                {
                    'type': 'memory_leak',
                    'severity': 'medium',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ],
            'error_logs': [
                {
                    'level': 'ERROR',
                    'message': 'Out of memory error in application',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ],
            'health_issues': [
                {
                    'type': 'high_cpu',
                    'severity': 'high'
                }
            ]
        }
        
        try:
            health_analysis = await self.gemini_ai.analyze_node_health(test_node_data)
            
            print(f"  📊 Health Analysis Results:")
            print(f"     Severity: {health_analysis.severity}")
            print(f"     Root Cause: {health_analysis.root_cause}")
            print(f"     Healing Strategy: {health_analysis.healing_strategy}")
            print(f"     Mirror Recommendation: {health_analysis.mirror_recommendation}")
            print(f"     Confidence: {health_analysis.confidence_score:.2f}")
            print(f"     Recovery Time: {health_analysis.estimated_recovery_time} minutes")
            print(f"     Immediate Actions: {', '.join(health_analysis.immediate_actions[:3])}")
            
            logger.info("✅ AI Health Analysis test completed")
            return health_analysis
            
        except Exception as e:
            logger.error(f"❌ AI Health Analysis test failed: {e}")
            return None
    
    async def test_mirror_recommendation(self):
        """Test AI mirror recommendation functionality"""
        logger.info("🔍 Testing AI Mirror Recommendation...")
        
        node_data = {
            'agent_id': 'test-agent-001',
            'health_status': 'degraded',
            'critical_issues': [
                'high_cpu_usage',
                'memory_leak',
                'service_failures'
            ],
            'recovery_estimate': 45
        }
        
        available_mirrors = [
            {
                'agent_id': 'test-mirror-001',
                'hostname': 'test-mirror-1',
                'status': 'active',
                'cpu_percent': 35.2,
                'memory_percent': 42.1,
                'capacity': 0.8
            },
            {
                'agent_id': 'test-mirror-002',
                'hostname': 'test-mirror-2',
                'status': 'standby',
                'cpu_percent': 28.7,
                'memory_percent': 39.5,
                'capacity': 0.9
            }
        ]
        
        try:
            recommendation = await self.gemini_ai.get_mirror_recommendation(
                node_data, available_mirrors
            )
            
            print(f"  🔄 Mirror Recommendation:")
            print(f"     Should Activate: {recommendation.should_activate_mirror}")
            print(f"     Mirror Node: {recommendation.mirror_node_id}")
            print(f"     Strategy: {recommendation.transition_strategy}")
            print(f"     Risk Assessment: {recommendation.risk_assessment}")
            print(f"     Rollback Conditions: {', '.join(recommendation.rollback_conditions[:2])}")
            
            logger.info("✅ AI Mirror Recommendation test completed")
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ AI Mirror Recommendation test failed: {e}")
            return None
    
    async def test_healing_strategy(self):
        """Test AI healing strategy generation"""
        logger.info("🛠️ Testing AI Healing Strategy Generation...")
        
        node_data = {
            'agent_id': 'test-agent-001',
            'hostname': 'test-server-1',
            'status': 'degraded'
        }
        
        # Mock health analysis
        health_analysis = HealthAnalysis(
            severity='high',
            root_cause='High CPU and memory usage causing service degradation',
            healing_strategy='Service restart and resource optimization',
            mirror_recommendation='should_activate',
            estimated_recovery_time=20,
            confidence_score=0.85,
            immediate_actions=['Restart Apache', 'Clear cache', 'Kill hung processes'],
            preventive_measures=['Monitor resources', 'Set up alerts']
        )
        
        try:
            strategy = await self.gemini_ai.generate_healing_strategy(
                node_data, health_analysis
            )
            
            print(f"  🎯 Healing Strategy:")
            print(f"     Strategy ID: {strategy.get('strategy_id', 'N/A')}")
            print(f"     Priority: {strategy.get('priority', 'N/A')}")
            print(f"     Total Time: {strategy.get('estimated_total_time', 'N/A')} minutes")
            
            phases = strategy.get('phases', [])
            for i, phase in enumerate(phases[:2]):  # Show first 2 phases
                print(f"     Phase {i+1}: {phase.get('phase', 'N/A')}")
                print(f"       Actions: {', '.join(phase.get('actions', [])[:2])}")
                print(f"       Duration: {phase.get('expected_duration', 'N/A')} min")
            
            logger.info("✅ AI Healing Strategy test completed")
            return strategy
            
        except Exception as e:
            logger.error(f"❌ AI Healing Strategy test failed: {e}")
            return None
    
    async def test_failure_prediction(self):
        """Test AI failure prediction functionality"""
        logger.info("📊 Testing AI Failure Prediction...")
        
        node_data = {
            'agent_id': 'test-agent-001',
            'current_metrics': {
                'cpu_percent': 75.2,
                'memory_percent': 68.5,
                'error_rate': 0.05
            }
        }
        
        # Mock historical data
        historical_data = []
        for i in range(10):
            historical_data.append({
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': 65 + (i * 2),  # Increasing trend
                'memory_percent': 55 + (i * 1.5),  # Increasing trend
                'error_rate': 0.01 + (i * 0.005)  # Increasing trend
            })
        
        try:
            prediction = await self.gemini_ai.predict_failure_risk(
                node_data, historical_data
            )
            
            print(f"  🔮 Failure Prediction:")
            print(f"     Risk Level: {prediction.get('risk_level', 'N/A')}")
            print(f"     Confidence: {prediction.get('confidence', 0):.2f}")
            print(f"     Time to Failure: {prediction.get('time_to_failure', 'N/A')}")
            
            indicators = prediction.get('failure_indicators', [])
            if indicators:
                print(f"     Indicators: {', '.join(indicators[:3])}")
            
            actions = prediction.get('recommended_actions', [])
            if actions:
                print(f"     Actions: {', '.join(actions[:2])}")
            
            logger.info("✅ AI Failure Prediction test completed")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ AI Failure Prediction test failed: {e}")
            return None
    
    async def test_neo4j_integration(self):
        """Test Neo4j graph database integration"""
        logger.info("🕸️ Testing Neo4j Integration...")
        
        if not self.neo4j_handler:
            logger.warning("⚠️ Neo4j not available, skipping integration test")
            return False
        
        try:
            # Test mirror topology
            topology = await self.neo4j_handler.get_mirror_topology()
            print(f"  📊 Mirror Topology: {len(topology)} primary nodes")
            
            # Test agent mirrors
            mirrors = await self.neo4j_handler.get_agent_mirrors('test-agent-001')
            print(f"  🔄 Available Mirrors: {len(mirrors)} mirrors found")
            
            # Test health check
            health = await self.neo4j_handler.check_mirror_health('test-agent-001')
            print(f"  ❤️ Health Check: {health.get('status', 'unknown')} status")
            
            logger.info("✅ Neo4j Integration test completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Neo4j Integration test failed: {e}")
            return False
    
    async def test_ai_system_health(self):
        """Test overall AI system health"""
        logger.info("🏥 Testing AI System Health...")
        
        try:
            # Test Gemini AI connection
            ai_healthy = await self.gemini_ai.health_check()
            print(f"  🧠 Gemini AI: {'✅ Healthy' if ai_healthy else '❌ Unhealthy'}")
            
            # Test Neo4j connection
            if self.neo4j_handler:
                neo4j_healthy = await self.neo4j_handler.health_check()
                print(f"  🕸️ Neo4j: {'✅ Healthy' if neo4j_healthy else '❌ Unhealthy'}")
            else:
                print(f"  🕸️ Neo4j: ⚠️ Not Available")
            
            # Test MongoDB connection
            if self.mongo_handler:
                mongo_healthy = await self.mongo_handler.health_check()
                print(f"  🍃 MongoDB: {'✅ Healthy' if mongo_healthy else '❌ Unhealthy'}")
            else:
                print(f"  🍃 MongoDB: ⚠️ Not Available")
            
            overall_health = ai_healthy and (not self.neo4j_handler or await self.neo4j_handler.health_check())
            
            logger.info(f"{'✅' if overall_health else '❌'} Overall AI System Health: {'Healthy' if overall_health else 'Issues Detected'}")
            return overall_health
            
        except Exception as e:
            logger.error(f"❌ AI System Health test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive AI System Test...")
        print("=" * 60)
        print("🛡️ AEGIS AI-POWERED SELF-HEALING SYSTEM TEST")
        print("=" * 60)
        
        # Test system health first
        await self.test_ai_system_health()
        print()
        
        # Setup test data
        await self.setup_test_data()
        print()
        
        # Run AI tests
        test_results = {}
        
        test_results['health_analysis'] = await self.test_ai_health_analysis()
        print()
        
        test_results['mirror_recommendation'] = await self.test_mirror_recommendation()
        print()
        
        test_results['healing_strategy'] = await self.test_healing_strategy()
        print()
        
        test_results['failure_prediction'] = await self.test_failure_prediction()
        print()
        
        test_results['neo4j_integration'] = await self.test_neo4j_integration()
        print()
        
        # Summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = 0
        
        for test_name, result in test_results.items():
            total_tests += 1
            if result:
                passed_tests += 1
                status = "✅ PASSED"
            else:
                status = "❌ FAILED"
            
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("🎉 AI Self-Healing System is ready for deployment!")
        elif success_rate >= 60:
            print("⚠️ AI Self-Healing System has some issues that need attention.")
        else:
            print("🚨 AI Self-Healing System needs significant fixes before deployment.")
        
        print("=" * 60)
        
        return success_rate
    
    async def cleanup(self):
        """Cleanup test data and connections"""
        logger.info("🧹 Cleaning up test data...")
        
        try:
            if self.neo4j_handler:
                await self.neo4j_handler.disconnect()
            
            if self.mongo_handler:
                await self.mongo_handler.disconnect()
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

async def main():
    """Main test function"""
    tester = AISystemTester()
    
    try:
        success_rate = await tester.run_comprehensive_test()
        return success_rate >= 80  # Return True if 80% or more tests pass
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        return False
        
    except Exception as e:
        logger.error(f"🚨 Test suite failed: {e}")
        return False
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    import sys
    
    print("🧪 Aegis AI Self-Healing System Test Suite")
    print("Testing Gemini 2.0 Flash AI + Neo4j Graph Database Integration")
    print()
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎊 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the logs for details.")
        sys.exit(1)
