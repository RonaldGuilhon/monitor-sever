"""Monitor servers use case"""

import time
import threading
from typing import Callable, Optional, List
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field

from ..domain import Server, ServerStatus, CheckResult, ServerState
from ..infrastructure.checks import NetworkChecker, CheckConfig
from ..infrastructure.alerts import AlertManager
from ..infrastructure.repositories import ServerRepository


@dataclass
class MonitorConfig:
    """Monitoring configuration"""
    interval_seconds: int = 30
    max_history_per_server: int = 1000


@dataclass
class ServerHistory:
    """Historical data for a server"""
    server_id: str
    status_history: deque = field(default_factory=lambda: deque(maxlen=100))
    check_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    last_state: Optional[ServerState] = None
    
    def add_status(self, state: ServerState):
        self.status_history.append((datetime.now(), state))
        self.last_state = state
    
    def add_check(self, result: CheckResult):
        self.check_history.append((datetime.now(), result))


class MonitorServersUseCase:
    """Use case for monitoring servers"""
    
    def __init__(
        self,
        server_repository: ServerRepository,
        network_checker: NetworkChecker,
        alert_manager: AlertManager,
        config: Optional[MonitorConfig] = None
    ):
        self._repository = server_repository
        self._checker = network_checker
        self._alert_manager = alert_manager
        self._config = config or MonitorConfig()
        
        self._is_running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._history: dict[str, ServerHistory] = {}
        self._callbacks: List[Callable] = []
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    def add_callback(self, callback: Callable[[str, ServerStatus], None]):
        """Add callback for status updates"""
        self._callbacks.append(callback)
    
    def start(self):
        """Start monitoring"""
        if self._is_running:
            return
        
        self._is_running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ServerMonitor"
        )
        self._monitor_thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self._is_running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
    
    def get_status(self, server_id: str) -> Optional[ServerStatus]:
        """Get current status for a server"""
        return self._history.get(server_id, ServerHistory(server_id=server_id)).last_state
    
    def get_all_status(self) -> dict[str, ServerStatus]:
        """Get status for all servers"""
        return {
            sid: hist.last_state 
            for sid, hist in self._history.items()
        }
    
    def get_history(self, server_id: str, limit: int = 50) -> List:
        """Get history for a server"""
        hist = self._history.get(server_id, ServerHistory(server_id=server_id))
        return list(hist.status_history)[-limit:]
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._is_running:
            try:
                servers = self._repository.get_enabled()
                
                for server in servers:
                    if not self._is_running:
                        break
                    
                    self._check_server(server)
                
                time.sleep(self._config.interval_seconds)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def _check_server(self, server: Server):
        """Check a single server"""
        # Initialize history if needed
        if server.id not in self._history:
            self._history[server.id] = ServerHistory(server_id=server.id)
        
        history = self._history[server.id]
        previous_state = history.last_state
        
        # Perform checks
        checks = []
        
        # Ping check
        ping_result = self._checker.check_ping(server.host)
        checks.append(ping_result)
        
        # Port checks (only if ping succeeds)
        if ping_result.success:
            app_port_result = self._checker.check_port(server.host, server.app_port)
            checks.append(app_port_result)
            
            if server.admin_port:
                admin_port_result = self._checker.check_port(server.host, server.admin_port)
                checks.append(admin_port_result)
        
        # HTTP check (only if ping and app port succeed)
        if ping_result.success and server.health_url:
            http_result = self._checker.check_http(server.health_url)
            checks.append(http_result)
        
        # Determine state
        current_state = self._determine_state(checks)
        
        # Update status
        server.status = ServerStatus(
            server_id=server.id,
            state=current_state,
            last_check=datetime.now(),
            checks=checks
        )
        
        history.add_status(current_state)
        for check in checks:
            history.add_check(check)
        
        # Handle alerts
        if previous_state and previous_state != current_state:
            self._handle_state_change(server, previous_state, current_state)
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(server.id, server.status)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _determine_state(self, checks: List[CheckResult]) -> ServerState:
        """Determine server state from check results"""
        if not checks:
            return ServerState.UNKNOWN
        
        # Find ping result
        ping_check = next((c for c in checks if c.check_type.value == 1), None)
        if ping_check and not ping_check.success:
            return ServerState.OFFLINE
        
        # Find HTTP result
        http_check = next((c for c in checks if c.check_type.value == 3), None)
        if http_check and not http_check.success:
            return ServerState.DEGRADED
        
        # Find port results
        port_checks = [c for c in checks if c.check_type.value == 2]
        if port_checks and not any(c.success for c in port_checks):
            return ServerState.DEGRADED
        
        # All checks passed
        if all(c.success for c in checks):
            return ServerState.ONLINE
        
        return ServerState.DEGRADED
    
    def _handle_state_change(self, server: Server, previous: ServerState, current: ServerState):
        """Handle server state change"""
        if not previous.is_healthy and current.is_healthy:
            self._alert_manager.notify_server_recovery(server, previous)
        elif previous.is_healthy and not current.is_healthy:
            self._alert_manager.notify_server_down(server, current)
