"""Network check implementations"""

import time
import socket
import platform
import subprocess
from typing import Optional
from dataclasses import dataclass

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ..domain import CheckResult, CheckType


@dataclass
class CheckConfig:
    """Configuration for network checks"""
    ping_timeout: int = 3
    http_timeout: int = 10
    port_timeout: int = 5


class NetworkChecker:
    """Performs network health checks"""
    
    def __init__(self, config: Optional[CheckConfig] = None):
        self._config = config or CheckConfig()
    
    def check_ping(self, host: str) -> CheckResult:
        """Check if host responds to ping"""
        try:
            cmd = self._get_ping_command(host)
            start_time = time.time()
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self._config.ping_timeout + 2
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                response_time_ms = self._extract_ping_time(result.stdout) or response_time_ms
                return CheckResult.ping(host=host, success=True, response_time_ms=response_time_ms)
            else:
                return CheckResult.ping(host=host, success=False, error="No response")
                
        except subprocess.TimeoutExpired:
            return CheckResult.ping(host=host, success=False, error="Timeout")
        except Exception as e:
            return CheckResult.ping(host=host, success=False, error=str(e))
    
    def check_port(self, host: str, port: int) -> CheckResult:
        """Check if a TCP port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._config.port_timeout)
            
            start_time = time.time()
            result = sock.connect_ex((host, port))
            response_time_ms = (time.time() - start_time) * 1000
            sock.close()
            
            if result == 0:
                return CheckResult.port(
                    host=host, port=port, success=True, 
                    response_time_ms=response_time_ms, status="OPEN"
                )
            else:
                return CheckResult.port(
                    host=host, port=port, success=False, 
                    status=f"Connection failed (code: {result})"
                )
                
        except Exception as e:
            return CheckResult.port(host=host, port=port, success=False, status=f"Error: {e}")
    
    def check_http(self, url: str) -> CheckResult:
        """Check HTTP endpoint"""
        try:
            response = requests.get(url, timeout=self._config.http_timeout)
            response_time_ms = response.elapsed.total_seconds() * 1000
            
            return CheckResult.http(
                url=url,
                success=200 <= response.status_code < 400,
                status_code=response.status_code,
                response_time_ms=response_time_ms
            )
            
        except Timeout:
            return CheckResult.http(url=url, success=False, error="Timeout")
        except ConnectionError:
            return CheckResult.http(url=url, success=False, error="Connection Error")
        except RequestException as e:
            return CheckResult.http(url=url, success=False, error=str(e))
    
    def _get_ping_command(self, host: str) -> list:
        """Get platform-specific ping command"""
        if platform.system().lower() == 'windows':
            return ['ping', '-n', '1', '-w', str(self._config.ping_timeout * 1000), host]
        else:
            return ['ping', '-c', '1', '-W', str(self._config.ping_timeout), host]
    
    def _extract_ping_time(self, output: str) -> Optional[float]:
        """Extract ping time from command output"""
        try:
            output_lower = output.lower()
            if 'time=' in output_lower:
                time_part = output_lower.split('time=')[1].split('ms')[0]
                return float(time_part)
        except (IndexError, ValueError):
            pass
        return None
