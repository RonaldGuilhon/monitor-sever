"""Constants and global configuration values"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# File paths
LOG_FILE = 'server_monitor.log'
CSV_FILE = 'server_status.csv'
CONFIG_FILE = 'servers_config.json'
LOGS_FILE = 'server_logs.json'

# Default ports
DEFAULT_APP_PORT = 8080
DEFAULT_ADMIN_PORT = 4848
DEFAULT_HTTP_PORT = 80
DEFAULT_HTTPS_PORT = 443

# Timeouts (in seconds)
DEFAULT_PING_TIMEOUT = 3
DEFAULT_HTTP_TIMEOUT = 10
DEFAULT_PORT_TIMEOUT = 5

# Monitoring intervals
DEFAULT_MONITOR_INTERVAL = 30
DEFAULT_GUI_UPDATE_INTERVAL = 1000  # milliseconds

# GUI settings
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MAX_TELEMETRY_DATA_POINTS = 50
MAX_LOG_ENTRIES_PER_SERVER = 1000

# Email settings
DEFAULT_SMTP_SERVER = 'smtp.gmail.com'
DEFAULT_SMTP_PORT = 587

# Status codes
STATUS_ONLINE = 'ONLINE'
STATUS_OFFLINE = 'OFFLINE'
STATUS_HTTP_ERROR = 'HTTP_ERROR'
STATUS_PORTS_CLOSED = 'PORTS_CLOSED'
STATUS_UNKNOWN = 'UNKNOWN'

# Colors for GUI
COLORS = {
    'bg_dark': '#2b2b2b',
    'fg_light': '#ffffff',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3'
}