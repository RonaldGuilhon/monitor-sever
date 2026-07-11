"""Domain models - Core business entities"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from .enums import ServerState, CheckType


@dataclass(frozen=True)
class CheckResult:
    """Result of a single health check"""
    check_type: CheckType
    success: bool
    response_time_ms: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def ping(cls, host: str, success: bool, response_time_ms: float = 0.0, 
             error: Optional[str] = None) -> 'CheckResult':
        return cls(
            check_type=CheckType.PING,
            success=success,
            response_time_ms=response_time_ms,
            message=error or ("OK" if success else "No response"),
            details={"host": host}
        )
    
    @classmethod
    def port(cls, host: str, port: int, success: bool, response_time_ms: float = 0.0,
             status: str = "OPEN") -> 'CheckResult':
        return cls(
            check_type=CheckType.PORT,
            success=success,
            response_time_ms=response_time_ms,
            message=status,
            details={"host": host, "port": port}
        )
    
    @classmethod
    def http(cls, url: str, success: bool, status_code: int = 0, 
             response_time_ms: float = 0.0, error: Optional[str] = None) -> 'CheckResult':
        return cls(
            check_type=CheckType.HTTP,
            success=success,
            response_time_ms=response_time_ms,
            message=error or f"HTTP {status_code}",
            details={"url": url, "status_code": status_code}
        )


@dataclass
class ServerStatus:
    """Current status of a server"""
    server_id: UUID
    state: ServerState = ServerState.UNKNOWN
    last_check: Optional[datetime] = None
    checks: List[CheckResult] = field(default_factory=list)
    consecutive_failures: int = 0
    uptime_seconds: float = 0.0
    
    @property
    def ping_result(self) -> Optional[CheckResult]:
        for check in self.checks:
            if check.check_type == CheckType.PING:
                return check
        return None
    
    @property
    def app_port_result(self) -> Optional[CheckResult]:
        for check in self.checks:
            if check.check_type == CheckType.PORT:
                return check
        return None
    
    @property
    def http_result(self) -> Optional[CheckResult]:
        for check in self.checks:
            if check.check_type == CheckType.HTTP:
                return check
        return None
    
    @property
    def avg_response_time_ms(self) -> float:
        if not self.checks:
            return 0.0
        times = [c.response_time_ms for c in self.checks if c.success]
        return sum(times) / len(times) if times else 0.0


@dataclass
class Server:
    """Server entity"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    host: str = ""
    app_port: int = 8080
    admin_port: int = 4848
    health_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    
    # Runtime status (not persisted)
    status: ServerStatus = field(default_factory=lambda: ServerStatus(server_id=uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "host": self.host,
            "app_port": self.app_port,
            "admin_port": self.admin_port,
            "health_url": self.health_url,
            "tags": self.tags,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Server':
        return cls(
            name=data.get("name", ""),
            host=data.get("host", ""),
            app_port=data.get("app_port", 8080),
            admin_port=data.get("admin_port", 4848),
            health_url=data.get("health_url"),
            tags=data.get("tags", []),
            enabled=data.get("enabled", True)
        )


@dataclass
class AlertConfig:
    """Alert configuration"""
    sound_enabled: bool = True
    email_enabled: bool = False
    email_cooldown_seconds: int = 300
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    username: str = ""
    password: str = ""
    from_email: str = ""
    to_emails: List[str] = field(default_factory=list)
