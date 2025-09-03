"""Network connectivity check functions"""

import time
import socket
import platform
import subprocess

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ..config import CONFIG
from ..utils import get_logger

logger = get_logger(__name__)

def check_ping(host):
    """Check if host responds to ping and return response time"""
    try:
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-n', '1', '-w', str(CONFIG['ping_timeout'] * 1000), host]
        else:
            cmd = ['ping', '-c', '1', '-W', str(CONFIG['ping_timeout']), host]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=CONFIG['ping_timeout'] + 2)
        response_time = (time.time() - start_time) * 1000  # in ms
        
        if result.returncode == 0:
            # Try to extract real ping time from output
            output = result.stdout.lower()
            if 'time=' in output:
                try:
                    time_part = output.split('time=')[1].split('ms')[0]
                    response_time = float(time_part)
                except:
                    pass  # use calculated time
            
            return {
                'success': True,
                'response_time': round(response_time, 1)
            }
        else:
            return {
                'success': False,
                'response_time': 0,
                'error': 'No response'
            }
    except (subprocess.TimeoutExpired, Exception) as e:
        logger.error(f"Ping error for {host}: {e}")
        return {
            'success': False,
            'response_time': 0,
            'error': str(e)
        }

def check_port(host, port, timeout=5):
    """Check if a specific port is open and return details"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        response_time = (time.time() - start_time) * 1000  # in ms
        sock.close()
        
        if result == 0:
            return {
                'success': True,
                'port': port,
                'response_time': round(response_time, 1),
                'status': 'OPEN'
            }
        else:
            return {
                'success': False,
                'port': port,
                'response_time': 0,
                'status': 'CLOSED',
                'error': f'Connection failed (code: {result})'
            }
    except Exception as e:
        logger.error(f"Error checking port {port} on {host}: {e}")
        return {
            'success': False,
            'port': port,
            'response_time': 0,
            'status': 'ERROR',
            'error': str(e)
        }

def check_http(url, timeout=None):
    """Check HTTP response from a URL"""
    if timeout is None:
        timeout = CONFIG['http_timeout']
    
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'status_code': response.status_code,
            'success': 200 <= response.status_code < 400,
            'response_time': response.elapsed.total_seconds(),
            'url': url
        }
    except Timeout:
        return {
            'status_code': 0, 
            'success': False, 
            'response_time': timeout, 
            'error': 'Timeout',
            'url': url
        }
    except ConnectionError:
        return {
            'status_code': 0, 
            'success': False, 
            'response_time': 0, 
            'error': 'Connection Error',
            'url': url
        }
    except RequestException as e:
        return {
            'status_code': 0, 
            'success': False, 
            'response_time': 0, 
            'error': str(e),
            'url': url
        }

def check_multiple_ports(host, ports, timeout=5):
    """Check multiple ports on a host"""
    results = {}
    for port in ports:
        results[port] = check_port(host, port, timeout)
    return results

def check_server_health(server_config):
    """Comprehensive server health check"""
    host = server_config['host']
    name = server_config['name']
    
    # Basic connectivity
    ping_result = check_ping(host)
    
    # Port checks
    ports_to_check = []
    if 'app_port' in server_config:
        ports_to_check.append(server_config['app_port'])
    if 'admin_port' in server_config:
        ports_to_check.append(server_config['admin_port'])
    
    port_results = {}
    if ping_result['success'] and ports_to_check:
        port_results = check_multiple_ports(host, ports_to_check)
    
    # HTTP health check
    http_result = None
    if ping_result['success'] and 'health_url' in server_config:
        if 'app_port' not in server_config or port_results.get(server_config['app_port'], {}).get('success', False):
            http_result = check_http(server_config['health_url'])
    
    return {
        'name': name,
        'host': host,
        'ping': ping_result,
        'ports': port_results,
        'http': http_result,
        'timestamp': time.time()
    }