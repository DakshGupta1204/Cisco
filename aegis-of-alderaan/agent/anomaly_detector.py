# Lightweight rule-based or ML detection

"""
A                # Get latest metrics if metrics collector is available
                if self.metrics_collector and hasattr(self.metrics_collector, 'metrics_buffer'):
                    if self.metrics_collector.metrics_buffer:
                        latest_metrics = self.metrics_collector.metrics_buffer[-1]
                        print(f"Checking metrics: CPU={latest_metrics.get('cpu_percent', 0):.1f}%")  # Debug
                        anomalies = self.analyze_metrics(latest_metrics)
                        
                        # Log any detected anomalies
                        for anomaly in anomalies:
                            self.logger.warning(f"🚨 ANOMALY DETECTED: {anomaly['type']} - {anomaly['description']}")
                            print(f"🚨 ANOMALY: {anomaly['type']} - {anomaly['description']}")
                    else:
                        print("No metrics in buffer yet")  # Debugderaan - Anomaly Detector
Lightweight rule-based and ML-based anomaly detection for network security
"""

import asyncio
import logging
import numpy as np
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class AnomalyDetector:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.metrics_collector = None  # Will be set by the main agent
        self.communicator = None  # Will be set by the main agent
        
        # Historical data for baseline calculation (focused on 4 core types)
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.network_history = deque(maxlen=100)
        
        # Anomaly detection parameters
        self.baseline_window = 50  # Number of samples for baseline
        self.anomaly_threshold = 2.5  # Standard deviations from mean
        self.spike_threshold = 3.0  # Sudden spike detection
        
        # Pattern detection
        self.known_attack_patterns = self.load_attack_patterns()
        
    def set_metrics_collector(self, metrics_collector):
        """Set reference to metrics collector"""
        self.metrics_collector = metrics_collector
        
    def set_communicator(self, communicator):
        """Set reference to communicator for sending anomalies"""
        self.communicator = communicator
        
    async def start(self):
        """Start anomaly detection service"""
        self.logger.info("Starting anomaly detection")
        self.running = True
        
        while self.running:
            try:
                # Get latest metrics if metrics collector is available
                if self.metrics_collector and hasattr(self.metrics_collector, 'metrics_buffer'):
                    if self.metrics_collector.metrics_buffer:
                        latest_metrics = self.metrics_collector.metrics_buffer[-1]
                        anomalies = self.analyze_metrics(latest_metrics)  # Remove await
                        
                        # Log and send any detected anomalies
                        for anomaly in anomalies:
                            self.logger.warning(f"ANOMALY DETECTED: {anomaly['type']} - {anomaly['description']}")
                            print(f"ANOMALY: {anomaly['type']} - {anomaly['description']}")
                            
                            # Send anomaly to Guardian via communicator
                            if self.communicator:
                                try:
                                    await self.communicator.send_anomaly(anomaly)
                                    print(f"Anomaly sent to Guardian: {anomaly['type']}")
                                    self.logger.info(f"Anomaly sent to Guardian: {anomaly['type']}")
                                except Exception as e:
                                    print(f"Failed to send anomaly: {e}")
                                    self.logger.error(f"Failed to send anomaly: {e}")
                            else:
                                print(f"No communicator available to send anomaly")
                                self.logger.warning("No communicator available to send anomaly")
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f"Error in anomaly detector: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stop anomaly detection"""
        self.logger.info("Stopping anomaly detection")
        self.running = False
    
    def load_attack_patterns(self) -> Dict:
        """Load known attack patterns for detection (CPU, Memory, DDoS, Network focus)"""
        return {
            'cpu_bomb': {
                'description': 'CPU usage spike or sustained high usage',
                'indicators': ['cpu_sudden_spike', 'cpu_sustained_high'],
                'thresholds': {'cpu_percent': 10}  # Lowered for testing
            },
            'memory_leak': {
                'description': 'Gradual memory increase or high memory usage',
                'indicators': ['memory_gradual_increase', 'memory_no_release'],
                'thresholds': {'memory_percent': 85}
            },
            'ddos_attempt': {
                'description': 'DDoS attack with network traffic spikes',
                'indicators': ['network_traffic_spike', 'connection_flood'],
                'thresholds': {'network_speed_mbps': 100}
            },
            'network_anomaly': {
                'description': 'Unusual network traffic patterns and behavior',
                'indicators': ['network_pattern_change', 'traffic_burst'],
                'thresholds': {'network_speed_mbps': 500}
            }
        }
    
    def analyze_metrics(self, metrics: Dict) -> List[Dict]:
        """Analyze metrics for anomalies"""
        anomalies = []
        
        # Update historical data
        self.update_baseline(metrics)
        
        # Statistical anomaly detection
        statistical_anomalies = self.detect_statistical_anomalies(metrics)
        anomalies.extend(statistical_anomalies)
        
        # Pattern-based detection
        pattern_anomalies = self.detect_pattern_anomalies(metrics)
        anomalies.extend(pattern_anomalies)
        
        # Rule-based detection
        rule_anomalies = self.detect_rule_based_anomalies(metrics)
        anomalies.extend(rule_anomalies)
        
        return anomalies
    
    def update_baseline(self, metrics: Dict):
        """Update baseline metrics for comparison (CPU, Memory, Network only)"""
        # Use flat format for easier access
        self.cpu_history.append(metrics.get('cpu_percent', metrics.get('cpu', {}).get('percent', 0)))
        self.memory_history.append(metrics.get('memory_percent', metrics.get('memory', {}).get('percent', 0)))
        
        # Network traffic tracking for DDoS detection
        network_speed = metrics.get('network', {}).get('speed_mbps', 0)
        self.network_history.append(network_speed)
    
    def detect_statistical_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        # CPU anomaly detection
        if len(self.cpu_history) >= self.baseline_window:
            cpu_anomaly = self.check_statistical_anomaly(
                metrics.get('cpu_percent', metrics.get('cpu', {}).get('percent', 0)),
                list(self.cpu_history)[:-1],  # Exclude current value
                'cpu',
                metrics['timestamp']
            )
            if cpu_anomaly:
                anomalies.append(cpu_anomaly)
        
        # Memory anomaly detection
        if len(self.memory_history) >= self.baseline_window:
            memory_anomaly = self.check_statistical_anomaly(
                metrics.get('memory_percent', metrics.get('memory', {}).get('percent', 0)),
                list(self.memory_history)[:-1],
                'memory',
                metrics['timestamp']
            )
            if memory_anomaly:
                anomalies.append(memory_anomaly)
        
        # Network anomaly detection
        if len(self.network_history) >= self.baseline_window:
            network_anomaly = self.check_statistical_anomaly(
                metrics['network']['speed_mbps'],
                list(self.network_history)[:-1],
                'network',
                metrics['timestamp']
            )
            if network_anomaly:
                anomalies.append(network_anomaly)
        
        return anomalies
    
    def check_statistical_anomaly(self, current_value: float, history: List[float], 
                                 metric_type: str, timestamp: str) -> Optional[Dict]:
        """Check if current value is statistically anomalous"""
        if len(history) < 10:  # Need minimum history
            return None
        
        mean = np.mean(history)
        std = np.std(history)
        
        if std == 0:  # Avoid division by zero
            return None
        
        z_score = abs((current_value - mean) / std)
        
        if z_score > self.anomaly_threshold:
            severity = 'critical' if z_score > self.spike_threshold else 'warning'
            
            return {
                'type': f'{metric_type}_statistical_anomaly',
                'severity': severity,
                'current_value': current_value,
                'baseline_mean': round(mean, 2),
                'baseline_std': round(std, 2),
                'z_score': round(z_score, 2),
                'timestamp': timestamp,
                'description': f'{metric_type.title()} value {current_value} is {z_score:.1f} std devs from baseline'
            }
        
        return None
    
    def detect_pattern_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detect known attack patterns"""
        anomalies = []
        
        # CPU bomb detection
        if self.detect_cpu_bomb(metrics):
            anomalies.append({
                'type': 'cpu_bomb_detected',
                'severity': 'critical',
                'pattern': 'cpu_bomb',
                'timestamp': metrics['timestamp'],
                'description': 'High CPU usage detected (>10% threshold)',
                'indicators': ['cpu_sudden_spike']
            })
        
        # Memory leak detection
        if self.detect_memory_leak():
            anomalies.append({
                'type': 'memory_leak_detected',
                'severity': 'warning',
                'pattern': 'memory_leak',
                'timestamp': metrics['timestamp'],
                'description': 'Potential memory leak detected',
                'indicators': ['memory_gradual_increase']
            })
        
        # DDoS attempt detection
        if self.detect_ddos_attempt(metrics):
            anomalies.append({
                'type': 'ddos_attempt_detected',
                'severity': 'critical',
                'pattern': 'ddos_attempt',
                'timestamp': metrics['timestamp'],
                'description': 'Potential DDoS attempt detected',
                'indicators': ['network_traffic_spike']
            })
        
        return anomalies
    
    def detect_cpu_bomb(self, metrics: Dict) -> bool:
        """Detect CPU bomb attacks"""
        # CPU threshold check
        cpu_percent = metrics.get('cpu_percent', metrics.get('cpu', {}).get('percent', 0))
        
        # Check for high CPU usage (lowered threshold for testing)
        if cpu_percent > 10:  # Lowered to 10% for easy testing
            return True
        
        # Check for sudden spike to high CPU
        if cpu_percent > 5 and len(self.cpu_history) >= 5:
            recent_avg = np.mean(list(self.cpu_history)[-5:])
            if cpu_percent - recent_avg > 5:  # 5% jump for easier detection
                return True
        
        return False
    
    def detect_memory_leak(self) -> bool:
        """Detect gradual memory leaks (LOWERED THRESHOLDS FOR TESTING)"""
        if len(self.memory_history) < 5:  # Reduced from 20 to 5
            return False
        
        # Check for consistent upward trend
        if len(self.memory_history) >= 10:
            recent_memory = list(self.memory_history)[-5:]
            older_memory = list(self.memory_history)[-10:-5]
            
            recent_avg = np.mean(recent_memory)
            older_avg = np.mean(older_memory)
            
            # Memory increased by more than 10% over time (reduced from 20%)
            if recent_avg - older_avg > 10:
                return True
        
        # Also check for high memory usage (simple threshold)
        latest_memory = list(self.memory_history)[-1]
        if latest_memory > 70:  # 70% memory usage threshold
            return True
        
        return False
    
    def detect_ddos_attempt(self, metrics: Dict) -> bool:
        """Detect potential DDoS attempts (LOWERED THRESHOLDS FOR TESTING)"""
        network_speed = metrics['network']['speed_mbps']
        
        # Check for unusual network traffic spike (lowered threshold)
        if network_speed > 10 and len(self.network_history) >= 3:  # 10 Mbps threshold (was 100)
            recent_avg = np.mean(list(self.network_history)[-3:])  # Check last 3 samples
            if network_speed > recent_avg * 3:  # 3x increase (was 5x)
                return True
        
        # Also check for sustained high network traffic
        if network_speed > 50:  # 50 Mbps sustained traffic
            return True
        
        return False
    
    def detect_rule_based_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detect anomalies using predefined rules (CPU, Memory, DDoS, Network only)"""
        anomalies = []
        
        # High CPU usage rule (additional check)
        cpu_percent = metrics.get('cpu_percent', metrics.get('cpu', {}).get('percent', 0))
        if cpu_percent > 80:  # High CPU threshold
            anomalies.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'current_value': cpu_percent,
                'threshold': 80,
                'timestamp': metrics['timestamp'],
                'description': f'High CPU usage detected: {cpu_percent}%'
            })
        
        # High memory usage rule (LOWERED THRESHOLD FOR TESTING)
        memory_percent = metrics.get('memory_percent', metrics.get('memory', {}).get('percent', 0))
        if memory_percent > 60:  # Lowered from 85% to 60%
            anomalies.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'current_value': memory_percent,
                'threshold': 60,
                'timestamp': metrics['timestamp'],
                'description': f'High memory usage detected: {memory_percent}%'
            })
        
        # Network traffic spike rule (LOWERED THRESHOLD FOR TESTING)
        network_speed = metrics.get('network', {}).get('speed_mbps', 0)
        if network_speed > 25:  # Lowered from 500 to 25 Mbps
            anomalies.append({
                'type': 'extreme_network_traffic',
                'severity': 'critical',
                'current_value': network_speed,
                'threshold': 25,
                'timestamp': metrics['timestamp'],
                'description': f'High network traffic detected: {network_speed} Mbps'
            })
        
        return anomalies
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of detected anomalies (CPU, Memory, Network, DDoS focus)"""
        return {
            'cpu_baseline': {
                'mean': np.mean(self.cpu_history) if self.cpu_history else 0,
                'std': np.std(self.cpu_history) if self.cpu_history else 0,
                'samples': len(self.cpu_history)
            },
            'memory_baseline': {
                'mean': np.mean(self.memory_history) if self.memory_history else 0,
                'std': np.std(self.memory_history) if self.memory_history else 0,
                'samples': len(self.memory_history)
            },
            'network_baseline': {
                'mean': np.mean(self.network_history) if self.network_history else 0,
                'std': np.std(self.network_history) if self.network_history else 0,
                'samples': len(self.network_history)
            },
            'detection_config': {
                'anomaly_threshold': self.anomaly_threshold,
                'spike_threshold': self.spike_threshold,
                'baseline_window': self.baseline_window
            },
            'supported_anomaly_types': [
                'CPU usage spikes',
                'Memory leaks and high usage',
                'DDoS and network traffic anomalies',
                'Network traffic pattern analysis'
            ]
        }
