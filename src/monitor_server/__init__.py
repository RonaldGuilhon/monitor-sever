"""Monitor de Servidores GlassFish

Sistema completo de monitoramento de servidores GlassFish com interface gráfica
e telemetria em tempo real.
"""

__version__ = "1.0.0"
__author__ = "Monitor Server Team"
__email__ = "support@monitor-server.com"

from .core.monitor import ServerMonitor
from .gui.main_window import ServerMonitorGUI
from .config.settings import CONFIG, SERVERS

__all__ = ['ServerMonitor', 'ServerMonitorGUI', 'CONFIG', 'SERVERS']