"""
Aegis of Alderaan - System Utilities
Common system utility functions
"""

import os
import platform
import socket
import logging
from typing import Dict, List, Optional
from datetime import datetime

def get_system_info() -> Dict:
    """Get comprehensive system information"""
    return {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'timestamp': datetime.utcnow().isoformat()
    }

def get_network_interfaces() -> List[Dict]:
    """Get network interface information"""
    interfaces = []
    try:
        import psutil
        for interface_name, addresses in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface_name,
                'addresses': []
            }
            
            for addr in addresses:
                address_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': getattr(addr, 'netmask', None),
                    'broadcast': getattr(addr, 'broadcast', None)
                }
                interface_info['addresses'].append(address_info)
            
            interfaces.append(interface_info)
    except ImportError:
        logging.warning("psutil not available for network interface info")
    
    return interfaces

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_uptime(seconds: float) -> str:
    """Format uptime seconds to human readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def validate_config(config: Dict, required_keys: List[str]) -> bool:
    """Validate that config contains all required keys"""
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required config key: {key}")
            return False
    return True

def create_directories(paths: List[str]) -> None:
    """Create directories if they don't exist"""
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directory {path}: {e}")

def cleanup_old_files(directory: str, max_age_days: int = 7) -> int:
    """Clean up files older than max_age_days"""
    if not os.path.exists(directory):
        return 0
    
    cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
    removed_count = 0
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1
    except Exception as e:
        logging.error(f"Error cleaning up files in {directory}: {e}")
    
    return removed_count
