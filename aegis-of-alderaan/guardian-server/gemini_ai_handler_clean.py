"""
Aegis of Alderaan - Enhanced Gemini AI Handler with Advanced Self-Healing
Intelligent system analysis and healing recommendations using Gemini 2.0 Flash
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from dataclasses import dataclass

@dataclass
class HealthAnalysis:
    """Health analysis result from Gemini AI"""
    severity: str  # critical, high, medium, low
    root_cause: str
    healing_strategy: str
    mirror_recommendation: str
    estimated_recovery_time: int  # minutes
    confidence_score: float
    immediate_actions: List[str]
    preventive_measures: List[str]

@dataclass
class MirrorRecommendation:
    """Mirror node recommendation"""
    should_activate_mirror: bool
    mirror_node_id: str
    transition_strategy: str
    rollback_conditions: List[str]
    risk_assessment: str

class GeminiAIHandler:
    """Enhanced Gemini AI handler for intelligent self-healing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            self.logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
            self.enabled = False
            return
        
        try:
            # Configure Gemini 2.0 Flash
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.enabled = True
            self.logger.info("✅ Gemini 2.0 Flash AI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI: {e}")
            self.enabled = False
    
    async def analyze_node_health(self, node_data: Dict) -> HealthAnalysis:
        """Analyze node health using Gemini AI and recommend healing actions"""
        if not self.enabled:
            return self._fallback_health_analysis(node_data)
        
        try:
            prompt = self._build_health_analysis_prompt(node_data)
            
            # Generate analysis using Gemini 2.0 Flash
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse AI response
            analysis = self._parse_health_analysis(response.text, node_data)
            
            self.logger.info(f"🧠 AI health analysis completed for {node_data.get('agent_id')}: {analysis.severity}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI health analysis failed: {e}")
            return self._fallback_health_analysis(node_data)
    
    async def get_mirror_recommendation(self, node_data: Dict, available_mirrors: List[Dict]) -> MirrorRecommendation:
        """Get intelligent mirror activation recommendation"""
        if not self.enabled:
            return self._fallback_mirror_recommendation(node_data, available_mirrors)
        
        try:
            prompt = self._build_mirror_recommendation_prompt(node_data, available_mirrors)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            recommendation = self._parse_mirror_recommendation(response.text, available_mirrors)
            
            self.logger.info(f"🔍 AI mirror recommendation for {node_data.get('agent_id')}: {'Activate' if recommendation.should_activate_mirror else 'Keep original'}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"AI mirror recommendation failed: {e}")
            return self._fallback_mirror_recommendation(node_data, available_mirrors)
    
    async def generate_healing_strategy(self, node_data: Dict, health_analysis: HealthAnalysis) -> Dict:
        """Generate detailed healing strategy with step-by-step actions"""
        if not self.enabled:
            return self._fallback_healing_strategy(health_analysis)
        
        try:
            prompt = self._build_healing_strategy_prompt(node_data, health_analysis)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            strategy = self._parse_healing_strategy(response.text)
            
            self.logger.info(f"🛠️ AI healing strategy generated for {node_data.get('agent_id')}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"AI healing strategy generation failed: {e}")
            return self._fallback_healing_strategy(health_analysis)
    
    async def predict_failure_risk(self, node_data: Dict, historical_data: List[Dict]) -> Dict:
        """Predict potential failure risks using historical patterns"""
        if not self.enabled:
            return {"risk_level": "unknown", "confidence": 0.0}
        
        try:
            prompt = self._build_failure_prediction_prompt(node_data, historical_data)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            prediction = self._parse_failure_prediction(response.text)
            
            self.logger.info(f"📊 AI failure prediction for {node_data.get('agent_id')}: {prediction.get('risk_level')}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"AI failure prediction failed: {e}")
            return {"risk_level": "unknown", "confidence": 0.0}
    
    def _build_health_analysis_prompt(self, node_data: Dict) -> str:
        """Build comprehensive health analysis prompt for Gemini"""
        return f"""
        You are an expert system administrator analyzing the health of a network monitoring agent.
        
        AGENT INFORMATION:
        - Agent ID: {node_data.get('agent_id', 'unknown')}
        - Hostname: {node_data.get('hostname', 'unknown')}
        - Role: {node_data.get('role', 'unknown')}
        - Status: {node_data.get('status', 'unknown')}
        - Last Seen: {node_data.get('last_seen', 'unknown')}
        
        CURRENT METRICS:
        - CPU Usage: {node_data.get('metrics', {}).get('cpu_percent', 'N/A')}%
        - Memory Usage: {node_data.get('metrics', {}).get('memory_percent', 'N/A')}%
        - Disk Usage: {node_data.get('metrics', {}).get('disk_percent', 'N/A')}%
        - Network Connections: {node_data.get('metrics', {}).get('network_connections', 'N/A')}
        - Load Average: {node_data.get('metrics', {}).get('load_average', 'N/A')}
        
        ANOMALIES DETECTED:
        {json.dumps(node_data.get('anomalies', []), indent=2)}
        
        ERROR LOGS:
        {json.dumps(node_data.get('error_logs', []), indent=2)}
        
        HEALTH ISSUES:
        {json.dumps(node_data.get('health_issues', []), indent=2)}
        
        Please provide a comprehensive health analysis in the following JSON format:
        {{
            "severity": "critical|high|medium|low",
            "root_cause": "detailed explanation of the primary issue",
            "healing_strategy": "recommended healing approach",
            "mirror_recommendation": "should_activate|attempt_heal|monitor_closely",
            "estimated_recovery_time": minutes_as_integer,
            "confidence_score": 0.0_to_1.0,
            "immediate_actions": ["action1", "action2", "action3"],
            "preventive_measures": ["measure1", "measure2", "measure3"]
        }}
        
        Consider the following in your analysis:
        1. Resource utilization patterns
        2. Error frequency and severity
        3. Network connectivity issues
        4. Historical performance trends
        5. Critical service dependencies
        6. Recovery complexity and time requirements
        """
    
    def _build_mirror_recommendation_prompt(self, node_data: Dict, available_mirrors: List[Dict]) -> str:
        """Build mirror activation recommendation prompt"""
        return f"""
        You are an expert in distributed systems and high availability architectures.
        
        PRIMARY NODE STATUS:
        - Agent ID: {node_data.get('agent_id')}
        - Current Health: {node_data.get('health_status', 'unknown')}
        - Critical Issues: {json.dumps(node_data.get('critical_issues', []))}
        - Recovery Estimate: {node_data.get('recovery_estimate', 'unknown')} minutes
        
        AVAILABLE MIRROR NODES:
        {json.dumps(available_mirrors, indent=2)}
        
        MIRROR RELATIONSHIPS:
        {json.dumps(node_data.get('mirror_relationships', []), indent=2)}
        
        Please analyze whether to activate a mirror node and provide recommendation in JSON format:
        {{
            "should_activate_mirror": true/false,
            "mirror_node_id": "best_mirror_candidate_or_null",
            "transition_strategy": "immediate|gradual|conditional",
            "rollback_conditions": ["condition1", "condition2"],
            "risk_assessment": "low|medium|high",
            "reasoning": "detailed explanation"
        }}
        
        Consider:
        1. Primary node recovery probability and time
        2. Mirror node readiness and capacity
        3. Service continuity requirements
        4. Data consistency implications
        5. Performance impact during transition
        6. Risk of cascade failures
        """
    
    def _build_healing_strategy_prompt(self, node_data: Dict, health_analysis: HealthAnalysis) -> str:
        """Build detailed healing strategy prompt"""
        return f"""
        You are an expert system administrator creating a detailed healing strategy.
        
        NODE: {node_data.get('agent_id')}
        HEALTH ANALYSIS: {health_analysis.__dict__}
        
        Create a comprehensive healing strategy with step-by-step actions in JSON format:
        {{
            "strategy_id": "unique_identifier",
            "priority": "immediate|urgent|normal|low",
            "phases": [
                {{
                    "phase": "immediate_stabilization",
                    "actions": ["action1", "action2"],
                    "expected_duration": minutes,
                    "success_criteria": ["criteria1", "criteria2"]
                }},
                {{
                    "phase": "root_cause_resolution", 
                    "actions": ["action1", "action2"],
                    "expected_duration": minutes,
                    "success_criteria": ["criteria1", "criteria2"]
                }},
                {{
                    "phase": "system_optimization",
                    "actions": ["action1", "action2"], 
                    "expected_duration": minutes,
                    "success_criteria": ["criteria1", "criteria2"]
                }}
            ],
            "monitoring_points": ["metric1", "metric2"],
            "rollback_triggers": ["trigger1", "trigger2"],
            "estimated_total_time": total_minutes
        }}
        """
    
    def _build_failure_prediction_prompt(self, node_data: Dict, historical_data: List[Dict]) -> str:
        """Build failure prediction prompt"""
        return f"""
        You are an expert in predictive analytics for distributed systems.
        
        CURRENT NODE STATE:
        {json.dumps(node_data, indent=2)}
        
        HISTORICAL DATA (last 10 events):
        {json.dumps(historical_data[-10:], indent=2)}
        
        Analyze patterns and predict failure risk in JSON format:
        {{
            "risk_level": "critical|high|medium|low",
            "confidence": 0.0_to_1.0,
            "time_to_failure": "estimated_hours_or_null",
            "failure_indicators": ["indicator1", "indicator2"],
            "trending_metrics": ["metric1_direction", "metric2_direction"],
            "recommended_actions": ["action1", "action2"]
        }}
        """
    
    def _parse_health_analysis(self, ai_response: str, node_data: Dict) -> HealthAnalysis:
        """Parse AI response into HealthAnalysis object"""
        try:
            # Extract JSON from AI response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            
            data = json.loads(json_str)
            
            return HealthAnalysis(
                severity=data.get('severity', 'medium'),
                root_cause=data.get('root_cause', 'Unknown issue detected'),
                healing_strategy=data.get('healing_strategy', 'Standard recovery procedures'),
                mirror_recommendation=data.get('mirror_recommendation', 'monitor_closely'),
                estimated_recovery_time=data.get('estimated_recovery_time', 30),
                confidence_score=data.get('confidence_score', 0.7),
                immediate_actions=data.get('immediate_actions', ['Monitor system', 'Check logs']),
                preventive_measures=data.get('preventive_measures', ['Regular health checks'])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI health analysis: {e}")
            return self._fallback_health_analysis(node_data)
    
    def _parse_mirror_recommendation(self, ai_response: str, available_mirrors: List[Dict]) -> MirrorRecommendation:
        """Parse AI response into MirrorRecommendation object"""
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            
            data = json.loads(json_str)
            
            return MirrorRecommendation(
                should_activate_mirror=data.get('should_activate_mirror', False),
                mirror_node_id=data.get('mirror_node_id', ''),
                transition_strategy=data.get('transition_strategy', 'gradual'),
                rollback_conditions=data.get('rollback_conditions', ['Primary node recovery']),
                risk_assessment=data.get('risk_assessment', 'medium')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI mirror recommendation: {e}")
            return self._fallback_mirror_recommendation({}, available_mirrors)
    
    def _parse_healing_strategy(self, ai_response: str) -> Dict:
        """Parse AI response into healing strategy"""
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI healing strategy: {e}")
            return self._fallback_healing_strategy(None)
    
    def _parse_failure_prediction(self, ai_response: str) -> Dict:
        """Parse AI response into failure prediction"""
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI failure prediction: {e}")
            return {"risk_level": "unknown", "confidence": 0.0}
    
    def _fallback_health_analysis(self, node_data: Dict) -> HealthAnalysis:
        """Fallback health analysis when AI is unavailable"""
        metrics = node_data.get('metrics', {})
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)
        
        if cpu > 90 or memory > 90:
            severity = 'critical'
            actions = ['Restart services', 'Clear cache', 'Scale resources']
        elif cpu > 70 or memory > 70:
            severity = 'high'
            actions = ['Monitor closely', 'Optimize processes']
        else:
            severity = 'medium'
            actions = ['Regular monitoring']
        
        return HealthAnalysis(
            severity=severity,
            root_cause='High resource utilization detected',
            healing_strategy='Resource optimization and service restart',
            mirror_recommendation='monitor_closely',
            estimated_recovery_time=15,
            confidence_score=0.6,
            immediate_actions=actions,
            preventive_measures=['Resource monitoring', 'Capacity planning']
        )
    
    def _fallback_mirror_recommendation(self, node_data: Dict, available_mirrors: List[Dict]) -> MirrorRecommendation:
        """Fallback mirror recommendation when AI is unavailable"""
        # Simple rule-based fallback
        should_activate = len(node_data.get('critical_issues', [])) > 2
        mirror_id = available_mirrors[0].get('agent_id', '') if available_mirrors else ''
        
        return MirrorRecommendation(
            should_activate_mirror=should_activate,
            mirror_node_id=mirror_id,
            transition_strategy='gradual',
            rollback_conditions=['Primary node recovery', 'Mirror node failure'],
            risk_assessment='medium'
        )
    
    def _fallback_healing_strategy(self, health_analysis: Optional[HealthAnalysis]) -> Dict:
        """Fallback healing strategy when AI is unavailable"""
        return {
            "strategy_id": f"fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "priority": "normal",
            "phases": [
                {
                    "phase": "immediate_stabilization",
                    "actions": ["Check system status", "Restart failed services"],
                    "expected_duration": 5,
                    "success_criteria": ["Services responding", "No critical errors"]
                },
                {
                    "phase": "monitoring",
                    "actions": ["Monitor metrics", "Check for recurring issues"],
                    "expected_duration": 15,
                    "success_criteria": ["Stable metrics", "No new errors"]
                }
            ],
            "monitoring_points": ["cpu_usage", "memory_usage", "service_status"],
            "rollback_triggers": ["System unresponsive", "Critical service failure"],
            "estimated_total_time": 20
        }
    
    async def health_check(self) -> bool:
        """Check if Gemini AI is accessible and working"""
        if not self.enabled:
            return False
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, "Hello, respond with 'OK' if you're working."
            )
            
            return 'ok' in response.text.lower()
            
        except Exception as e:
            self.logger.error(f"Gemini AI health check failed: {e}")
            return False
