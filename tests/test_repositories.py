"""Tests for repositories"""

import pytest
import tempfile
import os
from pathlib import Path

from monitor_server.infrastructure.repositories import ServerRepository, ConfigRepository
from monitor_server.domain import Server


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def server_repo(temp_dir):
    config_file = temp_dir / "servers.json"
    return ServerRepository(str(config_file))


class TestServerRepository:
    def test_empty_repository(self, server_repo):
        servers = server_repo.get_all()
        assert len(servers) == 0
    
    def test_add_server(self, server_repo):
        server = Server(name="Test", host="localhost", app_port=8080)
        
        result = server_repo.add(server)
        
        assert result.name == "Test"
        assert len(server_repo.get_all()) == 1
    
    def test_get_by_name(self, server_repo):
        server = Server(name="MyServer", host="10.0.0.1")
        server_repo.add(server)
        
        found = server_repo.get_by_name("MyServer")
        
        assert found is not None
        assert found.host == "10.0.0.1"
    
    def test_get_by_id(self, server_repo):
        server = Server(name="Test", host="localhost")
        added = server_repo.add(server)
        
        found = server_repo.get_by_id(added.id)
        
        assert found is not None
        assert found.name == "Test"
    
    def test_update_server(self, server_repo):
        server = Server(name="Old Name", host="localhost")
        added = server_repo.add(server)
        
        added.name = "New Name"
        server_repo.update(added)
        
        found = server_repo.get_by_id(added.id)
        assert found.name == "New Name"
    
    def test_delete_server(self, server_repo):
        server = Server(name="ToDelete", host="localhost")
        added = server_repo.add(server)
        
        result = server_repo.delete(added.id)
        
        assert result is True
        assert len(server_repo.get_all()) == 0
    
    def test_persistence(self, temp_dir):
        config_file = temp_dir / "servers.json"
        
        # Create and add server
        repo1 = ServerRepository(str(config_file))
        server = Server(name="Persistent", host="192.168.1.1")
        repo1.add(server)
        
        # Create new repo instance (should load from file)
        repo2 = ServerRepository(str(config_file))
        
        assert len(repo2.get_all()) == 1
        assert repo2.get_by_name("Persistent") is not None
    
    def test_get_enabled(self, server_repo):
        server1 = Server(name="Enabled", host="localhost", enabled=True)
        server2 = Server(name="Disabled", host="localhost", enabled=False)
        
        server_repo.add(server1)
        server_repo.add(server2)
        
        enabled = server_repo.get_enabled()
        
        assert len(enabled) == 1
        assert enabled[0].name == "Enabled"


class TestConfigRepository:
    def test_empty_config(self, temp_dir):
        config_file = temp_dir / "config.json"
        repo = ConfigRepository(str(config_file))
        
        assert repo.get("nonexistent") is None
        assert repo.get("nonexistent", "default") == "default"
    
    def test_set_and_get(self, temp_dir):
        config_file = temp_dir / "config.json"
        repo = ConfigRepository(str(config_file))
        
        repo.set("key", "value")
        
        assert repo.get("key") == "value"
    
    def test_get_section(self, temp_dir):
        config_file = temp_dir / "config.json"
        repo = ConfigRepository(str(config_file))
        
        repo.set("monitoring", {"interval": 30})
        
        section = repo.get_section("monitoring")
        assert section["interval"] == 30
