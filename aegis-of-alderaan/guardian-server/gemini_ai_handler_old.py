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
                        "topP": 0.8
                    }
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        analysis = result['candidates'][0]['content']['parts'][0]['text']
                        return self._parse_ai_analysis(analysis)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Gemini API error: {response.status} - {error_text}")
                        return {"error": f"API request failed: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"Error analyzing system health with Gemini: {e}")
            return {"error": str(e)}
    
    async def generate_healing_strategy(self, agent_id: str, health_issues: List[Dict], system_context: Dict) -> Dict:
        """
        Generate intelligent healing strategy using Gemini 2.0 Flash
        """
        if not self.api_key:
            return {"strategy": "fallback", "actions": ["restart_services"], "confidence": 0.5}
        
        try:
            prompt = self._create_healing_strategy_prompt(agent_id, health_issues, system_context)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 800,
                        "topP": 0.9
                    }
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        strategy = result['candidates'][0]['content']['parts'][0]['text']
                        return self._parse_healing_strategy(strategy)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Gemini API error: {response.status} - {error_text}")
                        return {"strategy": "fallback", "actions": ["restart_services"], "confidence": 0.3}
                        
        except Exception as e:
            self.logger.error(f"Error generating healing strategy with Gemini: {e}")
            return {"strategy": "fallback", "actions": ["restart_services"], "confidence": 0.3}
    
    async def analyze_attack_patterns(self, attack_data: List[Dict], network_topology: Dict) -> Dict:
        """
        Analyze attack patterns and suggest defensive strategies
        """
        if not self.api_key:
            return {"threat_level": "medium", "recommendations": ["basic_monitoring"]}
        
        try:
            prompt = self._create_attack_analysis_prompt(attack_data, network_topology)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 1200,
                        "topP": 0.85
                    }
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        analysis = result['candidates'][0]['content']['parts'][0]['text']
                        return self._parse_attack_analysis(analysis)
                    else:
                        return {"threat_level": "medium", "recommendations": ["basic_monitoring"]}
                        
        except Exception as e:
            self.logger.error(f"Error analyzing attack patterns: {e}")
            return {"threat_level": "medium", "recommendations": ["basic_monitoring"]}
    
    def _create_health_analysis_prompt(self, agent_id: str, metrics: Dict, anomalies: List[Dict]) -> str:
        """Create prompt for health analysis"""
        return f"""
You are an expert system administrator analyzing the health of a network monitoring agent.

AGENT ID: {agent_id}

CURRENT METRICS:
{json.dumps(metrics, indent=2)}

DETECTED ANOMALIES:
{json.dumps(anomalies, indent=2)}

Please analyze this data and provide:
1. Overall health status (healthy, degraded, critical, failed)
2. Root cause analysis of any issues
3. Severity assessment (low, medium, high, critical)
4. Recommended actions for remediation
5. Whether the node should be replaced with a mirror (yes/no)
6. Confidence level in your analysis (0-100%)

Respond in JSON format:
{{
  "health_status": "healthy|degraded|critical|failed",
  "root_cause": "description of the main issue",
  "severity": "low|medium|high|critical", 
  "recommended_actions": ["action1", "action2"],
  "mirror_replacement_needed": true/false,
  "confidence": 85,
  "reasoning": "explanation of your analysis"
}}
"""

    def _create_healing_strategy_prompt(self, agent_id: str, health_issues: List[Dict], system_context: Dict) -> str:
        """Create prompt for healing strategy generation"""
        return f"""
You are an AI system healing expert. Generate an optimal healing strategy for a compromised network agent.

AGENT ID: {agent_id}

HEALTH ISSUES:
{json.dumps(health_issues, indent=2)}

SYSTEM CONTEXT:
{json.dumps(system_context, indent=2)}

Generate a comprehensive healing strategy that includes:
1. Primary healing approach (repair, restart, replace, mirror_takeover)
2. Step-by-step actions to execute
3. Estimated time to recovery
4. Risk assessment
5. Rollback plan if healing fails
6. Mirror node activation requirements

Respond in JSON format:
{{
  "strategy": "repair|restart|replace|mirror_takeover",
  "actions": [
    {{"step": 1, "action": "description", "timeout": 30}},
    {{"step": 2, "action": "description", "timeout": 60}}
  ],
  "estimated_recovery_time": 120,
  "risk_level": "low|medium|high",
  "rollback_plan": ["action1", "action2"],
  "mirror_activation_required": true/false,
  "confidence": 90,
  "reasoning": "explanation of chosen strategy"
}}
"""

    def _create_attack_analysis_prompt(self, attack_data: List[Dict], network_topology: Dict) -> str:
        """Create prompt for attack pattern analysis"""
        return f"""
You are a cybersecurity expert analyzing attack patterns against a distributed network monitoring system.

ATTACK DATA:
{json.dumps(attack_data, indent=2)}

NETWORK TOPOLOGY:
{json.dumps(network_topology, indent=2)}

Analyze the attack patterns and provide:
1. Threat level assessment
2. Attack vector identification
3. Targeted vulnerabilities
4. Defensive recommendations
5. Network hardening suggestions
6. Mirror node deployment strategy

Respond in JSON format:
{{
  "threat_level": "low|medium|high|critical",
  "attack_vectors": ["vector1", "vector2"],
  "targeted_vulnerabilities": ["vuln1", "vuln2"],
  "defensive_recommendations": ["defense1", "defense2"],
  "network_hardening": ["hardening1", "hardening2"],
  "mirror_deployment_strategy": "description",
  "confidence": 85,
  "reasoning": "detailed analysis"
}}
"""

    def _parse_ai_analysis(self, analysis_text: str) -> Dict:
        """Parse AI analysis response"""
        try:
            # Extract JSON from the response
            start = analysis_text.find('{')
            end = analysis_text.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = analysis_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {
                    "health_status": "degraded",
                    "root_cause": "Unable to parse AI analysis",
                    "severity": "medium",
                    "recommended_actions": ["manual_review"],
                    "mirror_replacement_needed": False,
                    "confidence": 50,
                    "reasoning": "AI response parsing failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing AI analysis: {e}")
            return {
                "health_status": "degraded",
                "root_cause": "AI analysis parsing error",
                "severity": "medium", 
                "recommended_actions": ["manual_review"],
                "mirror_replacement_needed": False,
                "confidence": 30,
                "reasoning": f"Parse error: {str(e)}"
            }
    
    def _parse_healing_strategy(self, strategy_text: str) -> Dict:
        """Parse healing strategy response"""
        try:
            start = strategy_text.find('{')
            end = strategy_text.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = strategy_text[start:end]
                return json.loads(json_str)
            else:
                return {
                    "strategy": "restart",
                    "actions": [{"step": 1, "action": "restart_services", "timeout": 60}],
                    "estimated_recovery_time": 60,
                    "risk_level": "medium",
                    "rollback_plan": ["manual_intervention"],
                    "mirror_activation_required": False,
                    "confidence": 50,
                    "reasoning": "Fallback strategy due to parsing error"
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing healing strategy: {e}")
            return {
                "strategy": "restart",
                "actions": [{"step": 1, "action": "restart_services", "timeout": 60}],
                "estimated_recovery_time": 60,
                "risk_level": "high",
                "rollback_plan": ["manual_intervention"],
                "mirror_activation_required": True,
                "confidence": 30,
                "reasoning": f"Parse error: {str(e)}"
            }
    
    def _parse_attack_analysis(self, analysis_text: str) -> Dict:
        """Parse attack analysis response"""
        try:
            start = analysis_text.find('{')
            end = analysis_text.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = analysis_text[start:end]
                return json.loads(json_str)
            else:
                return {
                    "threat_level": "medium",
                    "attack_vectors": ["unknown"],
                    "targeted_vulnerabilities": ["unidentified"],
                    "defensive_recommendations": ["enhanced_monitoring"],
                    "network_hardening": ["firewall_update"],
                    "mirror_deployment_strategy": "deploy_additional_mirrors",
                    "confidence": 50,
                    "reasoning": "Fallback analysis due to parsing error"
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing attack analysis: {e}")
            return {
                "threat_level": "high",
                "attack_vectors": ["parse_error"],
                "targeted_vulnerabilities": ["system_analysis"],
                "defensive_recommendations": ["manual_review"],
                "network_hardening": ["immediate_assessment"],
                "mirror_deployment_strategy": "emergency_mirror_activation",
                "confidence": 20,
                "reasoning": f"Parse error: {str(e)}"
            }

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        if not self.api_key:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                
                payload = {
                    "contents": [{
                        "parts": [{"text": "Hello, respond with 'OK' if you're working."}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 10
                    }
                }
                
                async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Gemini health check failed: {e}")
            return False
