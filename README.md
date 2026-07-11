# Server Monitor v2.0

Advanced server monitoring system with clean architecture, built with Python.

## Architecture

```
src/monitor_server/
├── domain/              # Business logic and entities
│   ├── enums.py        # ServerState, CheckType, AlertSeverity
│   └── models.py       # Server, ServerStatus, CheckResult, AlertConfig
├── infrastructure/      # External implementations
│   ├── repositories.py # ServerRepository, ConfigRepository
│   ├── checks.py       # NetworkChecker (ping, port, HTTP)
│   └── alerts.py       # AlertManager, SoundAlertHandler, EmailAlertHandler
├── use_cases/          # Application business logic
│   ├── monitor.py      # MonitorServersUseCase
│   └── server_management.py  # CRUD operations
├── presentation/       # User interfaces (GUI, CLI)
└── __main__.py         # Entry point
```

### Design Patterns

- **Clean Architecture**: Clear separation of concerns
- **Repository Pattern**: Abstract data persistence
- **Strategy Pattern**: Pluggable alert handlers
- **Dataclasses**: Immutable domain models
- **Dependency Injection**: Loose coupling between layers

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/your-user/monitor-server.git
cd monitor-server

# Install with development dependencies
pip install -e ".[dev]"

# Or install with GUI dependencies
pip install -e ".[dev,gui]"
```

### Run

```bash
# Run the monitor
python -m monitor_server

# Or using make
make run
```

### Configuration

Edit `servers_config.json`:

```json
[
  {
    "name": "Production Server",
    "host": "192.168.1.100",
    "app_port": 8080,
    "admin_port": 4848,
    "health_url": "http://192.168.1.100/health",
    "tags": ["production"]
  }
]
```

## Features

- **Ping monitoring**: Check host reachability
- **Port monitoring**: TCP port status (app, admin)
- **HTTP health checks**: Endpoint monitoring
- **Alerts**: Sound and email notifications
- **History**: Track status changes over time
- **Docker**: Containerized deployment

## Development

```bash
# Run tests
make test

# Run linter
make lint

# Format code
make format

# Type check
make typecheck

# Run all checks
make pre-commit
```

## Docker

```bash
# Build image
docker build -t server-monitor .

# Run container
docker-compose up -d

# Stop
docker-compose down
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=monitor_server --cov-report=html

# Run specific tests
pytest tests/test_domain.py
```

## License

MIT License
