"""Entry point for the monitor server application"""

import sys
import signal
from pathlib import Path

from .domain import AlertConfig
from .infrastructure import ServerRepository, NetworkChecker, AlertManager
from .infrastructure.checks import CheckConfig
from .use_cases import MonitorServersUseCase, MonitorConfig


def main():
    """Main entry point"""
    print("Starting Server Monitor v2.0.0...")
    
    # Configuration
    check_config = CheckConfig(
        ping_timeout=3,
        http_timeout=10,
        port_timeout=5
    )
    
    alert_config = AlertConfig(
        sound_enabled=True,
        email_enabled=False
    )
    
    monitor_config = MonitorConfig(
        interval_seconds=30
    )
    
    # Dependencies
    server_repo = ServerRepository("servers_config.json")
    network_checker = NetworkChecker(check_config)
    alert_manager = AlertManager(alert_config)
    
    # Use case
    monitor = MonitorServersUseCase(
        server_repository=server_repo,
        network_checker=network_checker,
        alert_manager=alert_manager,
        config=monitor_config
    )
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\nStopping monitor...")
        monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring
    servers = server_repo.get_all()
    print(f"Loaded {len(servers)} servers")
    
    for server in servers:
        print(f"  - {server.name} ({server.host})")
    
    monitor.start()
    print("Monitoring started. Press Ctrl+C to stop.")
    
    # Keep main thread alive
    try:
        while monitor.is_running:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()


if __name__ == "__main__":
    main()
