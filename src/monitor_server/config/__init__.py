#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de configuração do sistema de monitoramento de servidores
"""

from .constants import *
from .settings import (
    CONFIG, SERVERS, load_config, save_config, 
    settings, Settings, BASE_DIR, CONFIG_DIR, DATA_DIR, LOGS_DIR
)

__all__ = [
    # Constants
    'CONFIG_FILE', 'LOG_FILE', 'CSV_FILE', 'SOUND_FILE',
    'DEFAULT_PING_TIMEOUT', 'DEFAULT_HTTP_TIMEOUT', 'DEFAULT_MONITOR_INTERVAL',
    'DEFAULT_SMTP_SERVER', 'DEFAULT_SMTP_PORT', 'DEFAULT_APP_PORT',
    
    # Settings (compatibilidade)
    'CONFIG', 'SERVERS', 'load_config', 'save_config',
    
    # Nova API de configuração
    'settings', 'Settings',
    
    # Diretórios
    'BASE_DIR', 'CONFIG_DIR', 'DATA_DIR', 'LOGS_DIR'
]