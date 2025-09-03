#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração centralizada do sistema de monitoramento de servidores
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    
from .constants import (
    CONFIG_FILE, DEFAULT_PING_TIMEOUT, DEFAULT_HTTP_TIMEOUT, 
    DEFAULT_MONITOR_INTERVAL, DEFAULT_SMTP_SERVER, DEFAULT_SMTP_PORT,
    DEFAULT_APP_PORT, LOG_FILE, CSV_FILE
)

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
for directory in [CONFIG_DIR, DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

class Settings:
    """
    Classe para gerenciar configurações do sistema
    """
    
    def __init__(self):
        # Carregar arquivo .env se disponível
        if DOTENV_AVAILABLE:
            env_file = BASE_DIR / ".env"
            if env_file.exists():
                load_dotenv(env_file)
        
        self._config = self._load_default_config()
        self._servers = self._load_default_servers()
        self._load_from_file()
        self._load_from_env()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Carrega configurações padrão"""
        return {
            # Configurações de monitoramento
            "monitoring": {
                "interval": DEFAULT_MONITOR_INTERVAL,
                "timeout_ping": DEFAULT_PING_TIMEOUT,
                "timeout_http": DEFAULT_HTTP_TIMEOUT,
                "timeout_port": 5,
                "max_retries": 3,
                "retry_delay": 2,
            },
            
            # Configurações de alertas
            "alerts": {
                "sound_enabled": True,
                "sound_file": "alert.wav",
                "email_enabled": False,
                "email_cooldown": 300,
            },
            
            # Configurações de email
            "email": {
                "smtp_server": DEFAULT_SMTP_SERVER,
                "smtp_port": DEFAULT_SMTP_PORT,
                "use_tls": True,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": [],
            },
            
            # Configurações de logging
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size": 10485760,
                "backup_count": 5,
            },
            
            # Configurações da GUI
            "gui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "auto_refresh": True,
                "refresh_interval": 5,
                "show_notifications": True,
            },
            
            # Configurações de dados
            "data": {
                "servers_file": "servers_config.json",
                "logs_file": LOG_FILE,
                "csv_file": CSV_FILE,
                "telemetry_retention_days": 30,
                "auto_backup": True,
                "backup_interval_hours": 24,
            },
        }
    
    def _load_default_servers(self) -> list:
        """Carrega lista padrão de servidores"""
        return [
            {
                'name': 'Servidor Local',
                'host': 'localhost',
                'app_port': DEFAULT_APP_PORT,
                'admin_port': 4848,
                'health_url': f'http://localhost:{DEFAULT_APP_PORT}/health'
            },
            {
                'name': 'Servidor Produção',
                'host': '192.168.1.100',
                'app_port': DEFAULT_APP_PORT,
                'admin_port': 4848,
                'health_url': f'http://192.168.1.100:{DEFAULT_APP_PORT}/health'
            }
        ]
    
    def _load_from_file(self):
        """Carrega configurações do arquivo"""
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'config' in data:
                        self._merge_config(data['config'])
                    if 'servers' in data:
                        self._servers = data['servers']
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erro ao carregar configuração: {e}")
    
    def _load_from_env(self):
        """Carrega configurações das variáveis de ambiente"""
        env_mappings = {
            "MONITOR_INTERVAL": ("monitoring", "interval", int),
            "MONITOR_TIMEOUT_PING": ("monitoring", "timeout_ping", int),
            "MONITOR_TIMEOUT_HTTP": ("monitoring", "timeout_http", int),
            "ALERTS_SOUND_ENABLED": ("alerts", "sound_enabled", lambda x: x.lower() == 'true'),
            "ALERTS_EMAIL_ENABLED": ("alerts", "email_enabled", lambda x: x.lower() == 'true'),
            "EMAIL_SMTP_SERVER": ("email", "smtp_server", str),
            "EMAIL_SMTP_PORT": ("email", "smtp_port", int),
            "EMAIL_USE_TLS": ("email", "use_tls", lambda x: x.lower() == 'true'),
            "EMAIL_USERNAME": ("email", "username", str),
            "EMAIL_PASSWORD": ("email", "password", str),
            "EMAIL_FROM": ("email", "from_email", str),
            "EMAIL_TO": ("email", "to_emails", lambda x: [email.strip() for email in x.split(',')]),
            "LOG_LEVEL": ("logging", "level", str),
        }
        
        for env_var, (section, key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = converter(value)
                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][key] = converted_value
                except (ValueError, TypeError) as e:
                    print(f"Erro ao converter variável de ambiente {env_var}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Mescla nova configuração com a existente"""
        def merge_dict(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self._config, new_config)
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        if key is None:
            return self._config.get(section, default)
        return self._config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """Define valor de configuração"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def get_servers(self) -> list:
        """Retorna lista de servidores"""
        return self._servers.copy()
    
    def set_servers(self, servers: list):
        """Define lista de servidores"""
        self._servers = servers
    
    def save_to_file(self):
        """Salva configurações no arquivo"""
        config_data = {
            'config': self._config,
            'servers': self._servers
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar configuração: {e}")
    
    # Propriedades de conveniência para compatibilidade
    @property
    def monitoring_interval(self) -> int:
        return self.get("monitoring", "interval", DEFAULT_MONITOR_INTERVAL)
    
    @property
    def ping_timeout(self) -> int:
        return self.get("monitoring", "timeout_ping", DEFAULT_PING_TIMEOUT)
    
    @property
    def http_timeout(self) -> int:
        return self.get("monitoring", "timeout_http", DEFAULT_HTTP_TIMEOUT)

# Instância global de configurações
settings = Settings()

# Variáveis para compatibilidade com código existente
CONFIG = {
    'ping_timeout': settings.ping_timeout,
    'http_timeout': settings.http_timeout,
    'monitor_interval': settings.monitoring_interval,
    'log_file': LOG_FILE,
    'csv_file': CSV_FILE,
    'email_alerts': settings.get("alerts", "email_enabled", False),
    'sound_alerts': settings.get("alerts", "sound_enabled", True),
    'smtp_server': settings.get("email", "smtp_server", DEFAULT_SMTP_SERVER),
    'smtp_port': settings.get("email", "smtp_port", DEFAULT_SMTP_PORT),
    'email_user': settings.get("email", "username", ""),
    'email_password': settings.get("email", "password", ""),
    'alert_recipients': settings.get("email", "to_emails", [])
}

SERVERS = settings.get_servers()

def load_config():
    """Recarrega configurações (mantido para compatibilidade)"""
    global CONFIG, SERVERS, settings
    settings = Settings()
    
    # Atualiza variáveis globais para compatibilidade
    CONFIG.update({
        'ping_timeout': settings.ping_timeout,
        'http_timeout': settings.http_timeout,
        'monitor_interval': settings.monitoring_interval,
        'email_alerts': settings.get("alerts", "email_enabled", False),
        'sound_alerts': settings.get("alerts", "sound_enabled", True),
        'smtp_server': settings.get("email", "smtp_server", DEFAULT_SMTP_SERVER),
        'smtp_port': settings.get("email", "smtp_port", DEFAULT_SMTP_PORT),
        'email_user': settings.get("email", "username", ""),
        'email_password': settings.get("email", "password", ""),
        'alert_recipients': settings.get("email", "to_emails", [])
    })
    
    SERVERS = settings.get_servers()

def save_config():
    """Salva configurações (mantido para compatibilidade)"""
    settings.save_to_file()