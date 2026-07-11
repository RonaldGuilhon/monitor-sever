"""Repository implementations"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..domain import Server, ServerStatus


class ServerRepository:
    """Repository for server persistence"""
    
    def __init__(self, file_path: str = "servers_config.json"):
        self._file_path = Path(file_path)
        self._servers: Dict[UUID, Server] = {}
        self._load()
    
    def _load(self):
        """Load servers from file"""
        if not self._file_path.exists():
            return
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    server = Server.from_dict(item)
                    self._servers[server.id] = server
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading servers: {e}")
    
    def _save(self):
        """Save servers to file"""
        data = [server.to_dict() for server in self._servers.values()]
        
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving servers: {e}")
    
    def get_all(self) -> List[Server]:
        return list(self._servers.values())
    
    def get_by_id(self, server_id: UUID) -> Optional[Server]:
        return self._servers.get(server_id)
    
    def get_by_name(self, name: str) -> Optional[Server]:
        for server in self._servers.values():
            if server.name == name:
                return server
        return None
    
    def add(self, server: Server) -> Server:
        self._servers[server.id] = server
        self._save()
        return server
    
    def update(self, server: Server) -> Server:
        if server.id not in self._servers:
            raise ValueError(f"Server {server.id} not found")
        self._servers[server.id] = server
        self._save()
        return server
    
    def delete(self, server_id: UUID) -> bool:
        if server_id in self._servers:
            del self._servers[server_id]
            self._save()
            return True
        return False
    
    def get_enabled(self) -> List[Server]:
        return [s for s in self._servers.values() if s.enabled]


class ConfigRepository:
    """Repository for application configuration"""
    
    def __init__(self, file_path: str = "config.json"):
        self._file_path = Path(file_path)
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        if self._file_path.exists():
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        self._config[key] = value
        self._save()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        return self._config.get(section, {})
    
    def _save(self):
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
