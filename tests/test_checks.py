"""Tests for network checks"""

import pytest
from unittest.mock import patch, MagicMock

from monitor_server.infrastructure.checks import NetworkChecker, CheckConfig
from monitor_server.domain import CheckType


@pytest.fixture
def checker():
    return NetworkChecker(CheckConfig(ping_timeout=1, http_timeout=2, port_timeout=1))


class TestNetworkChecker:
    def test_check_ping_success(self, checker):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Reply from 127.0.0.1: time=5ms"
            )
            
            result = checker.check_ping("127.0.0.1")
            
            assert result.success is True
            assert result.check_type == CheckType.PING
            assert result.response_time_ms > 0
    
    def test_check_ping_failure(self, checker):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="Request timeout"
            )
            
            result = checker.check_ping("192.168.1.999")
            
            assert result.success is False
    
    def test_check_port_open(self, checker):
        with patch('socket.socket') as mock_socket:
            mock_instance = MagicMock()
            mock_instance.connect_ex.return_value = 0
            mock_socket.return_value = mock_instance
            
            result = checker.check_port("localhost", 8080)
            
            assert result.success is True
            assert result.check_type == CheckType.PORT
            assert result.details["port"] == 8080
    
    def test_check_port_closed(self, checker):
        with patch('socket.socket') as mock_socket:
            mock_instance = MagicMock()
            mock_instance.connect_ex.return_value = 1
            mock_socket.return_value = mock_instance
            
            result = checker.check_port("localhost", 9999)
            
            assert result.success is False
    
    def test_check_http_success(self, checker):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_get.return_value = mock_response
            
            result = checker.check_http("http://localhost/health")
            
            assert result.success is True
            assert result.check_type == CheckType.HTTP
            assert result.details["status_code"] == 200
    
    def test_check_http_error(self, checker):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            
            result = checker.check_http("http://localhost/health")
            
            assert result.success is False
