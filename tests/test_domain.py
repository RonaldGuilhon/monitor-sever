"""Tests for domain models"""

import pytest
from datetime import datetime
from uuid import uuid4

from monitor_server.domain import (
    Server, ServerStatus, CheckResult, AlertConfig,
    ServerState, CheckType, AlertSeverity
)


class TestServerState:
    def test_is_healthy(self):
        assert ServerState.ONLINE.is_healthy is True
        assert ServerState.OFFLINE.is_healthy is False
        assert ServerState.DEGRADED.is_healthy is False
    
    def test_icon(self):
        assert ServerState.ONLINE.icon == "✅"
        assert ServerState.OFFLINE.icon == "❌"
        assert ServerState.DEGRADED.icon == "⚠️"


class TestCheckResult:
    def test_ping_success(self):
        result = CheckResult.ping(host="localhost", success=True, response_time_ms=10.5)
        
        assert result.check_type == CheckType.PING
        assert result.success is True
        assert result.response_time_ms == 10.5
        assert result.details["host"] == "localhost"
    
    def test_ping_failure(self):
        result = CheckResult.ping(host="192.168.1.1", success=False, error="Timeout")
        
        assert result.success is False
        assert result.message == "Timeout"
    
    def test_port_success(self):
        result = CheckResult.port(host="localhost", port=8080, success=True, response_time_ms=5.0)
        
        assert result.check_type == CheckType.PORT
        assert result.success is True
        assert result.details["port"] == 8080
    
    def test_http_success(self):
        result = CheckResult.http(url="http://example.com", success=True, status_code=200)
        
        assert result.check_type == CheckType.HTTP
        assert result.success is True
        assert result.details["status_code"] == 200


class TestServer:
    def test_creation(self):
        server = Server(
            name="Test Server",
            host="192.168.1.100",
            app_port=8080,
            admin_port=4848
        )
        
        assert server.name == "Test Server"
        assert server.host == "192.168.1.100"
        assert server.app_port == 8080
        assert server.enabled is True
    
    def test_to_dict(self):
        server = Server(
            name="Test",
            host="localhost",
            app_port=80,
            health_url="http://localhost/health"
        )
        
        data = server.to_dict()
        
        assert data["name"] == "Test"
        assert data["host"] == "localhost"
        assert data["app_port"] == 80
        assert data["health_url"] == "http://localhost/health"
    
    def test_from_dict(self):
        data = {
            "name": "Production",
            "host": "10.0.0.1",
            "app_port": 443,
            "admin_port": 8443,
            "tags": ["production", "critical"]
        }
        
        server = Server.from_dict(data)
        
        assert server.name == "Production"
        assert server.host == "10.0.0.1"
        assert server.app_port == 443
        assert "production" in server.tags


class TestServerStatus:
    def test_initial_state(self):
        server_id = uuid4()
        status = ServerStatus(server_id=server_id)
        
        assert status.state == ServerState.UNKNOWN
        assert status.last_check is None
        assert len(status.checks) == 0
    
    def test_avg_response_time(self):
        server_id = uuid4()
        status = ServerStatus(
            server_id=server_id,
            checks=[
                CheckResult.ping("host1", True, 10.0),
                CheckResult.ping("host2", True, 20.0),
                CheckResult.ping("host3", False, 0.0),
            ]
        )
        
        # Only successful checks should be averaged
        assert status.avg_response_time_ms == 15.0


class TestAlertConfig:
    def test_defaults(self):
        config = AlertConfig()
        
        assert config.sound_enabled is True
        assert config.email_enabled is False
        assert config.smtp_server == "smtp.gmail.com"
        assert config.smtp_port == 587
