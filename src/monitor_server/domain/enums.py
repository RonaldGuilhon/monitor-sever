"""Domain enumerations"""

from enum import Enum, auto


class ServerState(Enum):
    """Server health states"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"
    
    @property
    def is_healthy(self) -> bool:
        return self == self.ONLINE
    
    @property
    def icon(self) -> str:
        icons = {
            self.ONLINE: "✅",
            self.OFFLINE: "❌",
            self.DEGRADED: "⚠️",
            self.UNKNOWN: "❓"
        }
        return icons.get(self, "❓")


class CheckType(Enum):
    """Types of health checks"""
    PING = auto()
    PORT = auto()
    HTTP = auto()
    TCP = auto()


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    @property
    def icon(self) -> str:
        icons = {
            self.INFO: "ℹ️",
            self.WARNING: "⚠️",
            self.ERROR: "❌",
            self.CRITICAL: "🚨"
        }
        return icons.get(self, "ℹ️")
