"""Server management use cases"""

from typing import List, Optional
from uuid import UUID

from ..domain import Server
from ..infrastructure.repositories import ServerRepository


class AddServerUseCase:
    """Use case for adding a server"""
    
    def __init__(self, repository: ServerRepository):
        self._repository = repository
    
    def execute(
        self,
        name: str,
        host: str,
        app_port: int = 8080,
        admin_port: int = 4848,
        health_url: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Server:
        # Check for duplicate name
        existing = self._repository.get_by_name(name)
        if existing:
            raise ValueError(f"Server with name '{name}' already exists")
        
        server = Server(
            name=name,
            host=host,
            app_port=app_port,
            admin_port=admin_port,
            health_url=health_url,
            tags=tags or []
        )
        
        return self._repository.add(server)


class UpdateServerUseCase:
    """Use case for updating a server"""
    
    def __init__(self, repository: ServerRepository):
        self._repository = repository
    
    def execute(
        self,
        server_id: UUID,
        name: Optional[str] = None,
        host: Optional[str] = None,
        app_port: Optional[int] = None,
        admin_port: Optional[int] = None,
        health_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        enabled: Optional[bool] = None
    ) -> Server:
        server = self._repository.get_by_id(server_id)
        if not server:
            raise ValueError(f"Server {server_id} not found")
        
        if name is not None:
            server.name = name
        if host is not None:
            server.host = host
        if app_port is not None:
            server.app_port = app_port
        if admin_port is not None:
            server.admin_port = admin_port
        if health_url is not None:
            server.health_url = health_url
        if tags is not None:
            server.tags = tags
        if enabled is not None:
            server.enabled = enabled
        
        return self._repository.update(server)


class DeleteServerUseCase:
    """Use case for deleting a server"""
    
    def __init__(self, repository: ServerRepository):
        self._repository = repository
    
    def execute(self, server_id: UUID) -> bool:
        server = self._repository.get_by_id(server_id)
        if not server:
            raise ValueError(f"Server {server_id} not found")
        
        return self._repository.delete(server_id)


class ListServersUseCase:
    """Use case for listing servers"""
    
    def __init__(self, repository: ServerRepository):
        self._repository = repository
    
    def execute(self, enabled_only: bool = False) -> List[Server]:
        if enabled_only:
            return self._repository.get_enabled()
        return self._repository.get_all()
