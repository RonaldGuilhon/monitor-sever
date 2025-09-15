# Guia de Desenvolvimento

Este documento fornece informações detalhadas para desenvolvedores que desejam contribuir ou entender a arquitetura do sistema de monitoramento de servidores.

## 🏗️ Arquitetura do Sistema

### Visão Geral

O sistema segue uma arquitetura modular baseada em camadas:

```
┌─────────────────────────────────────────┐
│                GUI Layer                │
│  (main_window, dialogs, telemetry)     │
├─────────────────────────────────────────┤
│              Core Layer                 │
│    (monitor, checks, alerts)           │
├─────────────────────────────────────────┤
│            Config Layer                 │
│      (settings, constants)             │
├─────────────────────────────────────────┤
│             Utils Layer                 │
│    (file_utils, network_utils)         │
└─────────────────────────────────────────┘
```

### Módulos Principais

#### 1. Core (`src/monitor_server/core/`)

**monitor.py**
- Classe principal `ServerMonitor`
- Gerencia o ciclo de vida do monitoramento
- Coordena verificações e alertas
- Thread-safe para execução em background

**checks.py**
- Funções de verificação de conectividade
- `check_ping()`: Verifica conectividade ICMP
- `check_port()`: Testa portas TCP
- `check_http()`: Valida endpoints HTTP/HTTPS
- `check_server_health()`: Verificação completa

**alerts.py**
- Classe `AlertManager` para gerenciar notificações
- Suporte a alertas sonoros e por email
- Sistema de cooldown para evitar spam
- Histórico de alertas

**network_utils.py**
- Utilitários de rede
- Validação de URLs
- Formatação de endereços

#### 2. GUI (`src/monitor_server/gui/`)

**main_window.py**
- Janela principal da aplicação
- Gerencia abas e layout geral
- Integração com sistema de monitoramento

**dialogs.py**
- Diálogos personalizados
- `DarkMessageBox`: Mensagens com tema escuro
- `ServerDialog`: Configuração de servidores
- `ConfigDialog`: Configurações do sistema

**telemetry.py**
- Painel de gráficos em tempo real
- Integração com matplotlib
- Visualização de métricas históricas

**logs.py**
- Painel de visualização de logs
- Filtragem e busca
- Exportação de logs

#### 3. Config (`src/monitor_server/config/`)

**settings.py**
- Classe `Settings` para configuração centralizada
- Suporte a arquivos JSON e variáveis de ambiente
- Configurações hierárquicas
- Validação de tipos

**constants.py**
- Constantes do sistema
- Valores padrão
- Caminhos de arquivos

#### 4. Utils (`src/monitor_server/utils/`)

**file_utils.py**
- Operações com arquivos
- Backup e restauração
- Manipulação de JSON/CSV

## 🔧 Padrões de Desenvolvimento

### Convenções de Código

1. **PEP 8**: Seguir as convenções de estilo Python
2. **Type Hints**: Usar anotações de tipo em todas as funções
3. **Docstrings**: Documentar todas as classes e funções públicas
4. **Logging**: Usar o sistema de logging estruturado

### Exemplo de Função Bem Documentada

```python
def check_server_health(
    server: Dict[str, Any], 
    timeout_ping: int = 5,
    timeout_http: int = 10
) -> Dict[str, Any]:
    """
    Realiza verificação completa de saúde do servidor.
    
    Args:
        server: Dicionário com configurações do servidor
        timeout_ping: Timeout para verificação de ping em segundos
        timeout_http: Timeout para verificação HTTP em segundos
    
    Returns:
        Dict contendo resultados das verificações:
        {
            'ping': bool,
            'app_port': bool,
            'admin_port': bool,
            'http': bool,
            'overall_status': str,
            'response_time': float,
            'timestamp': str
        }
    
    Raises:
        ValueError: Se configuração do servidor for inválida
        ConnectionError: Se não conseguir conectar ao servidor
    """
    # Implementação...
```

### Sistema de Logging

```python
import logging
from src.monitor_server.config import settings

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)

# Usar logging estruturado
logger.info("Iniciando verificação", extra={
    'server': server_name,
    'action': 'health_check',
    'timestamp': datetime.now().isoformat()
})
```

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── unit/
│   ├── test_monitor.py
│   ├── test_checks.py
│   ├── test_alerts.py
│   └── test_settings.py
├── integration/
│   ├── test_gui_integration.py
│   └── test_monitoring_flow.py
├── fixtures/
│   ├── sample_config.json
│   └── test_servers.json
└── conftest.py
```

### Exemplo de Teste Unitário

```python
import pytest
from unittest.mock import patch, MagicMock
from src.monitor_server.core.checks import check_ping

class TestPingCheck:
    """Testes para função check_ping"""
    
    @patch('subprocess.run')
    def test_ping_success_windows(self, mock_run):
        """Testa ping bem-sucedido no Windows"""
        # Arrange
        mock_run.return_value.returncode = 0
        
        # Act
        result = check_ping('192.168.1.1', timeout=5)
        
        # Assert
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_ping_failure(self, mock_run):
        """Testa ping com falha"""
        # Arrange
        mock_run.return_value.returncode = 1
        
        # Act
        result = check_ping('192.168.1.999', timeout=5)
        
        # Assert
        assert result is False
    
    def test_ping_invalid_host(self):
        """Testa ping com host inválido"""
        with pytest.raises(ValueError):
            check_ping('', timeout=5)
```

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/test_checks.py

# Com cobertura
pytest --cov=src/monitor_server --cov-report=html

# Testes de integração
pytest tests/integration/
```

## 🔄 Fluxo de Desenvolvimento

### 1. Configuração do Ambiente

```bash
# Clone e setup
git clone <repo>
cd monitor-server
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Desenvolvimento

```bash
# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Desenvolver e testar
pytest
flake8 src/
mypy src/

# Commit
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

### 3. Pull Request

1. Push da branch
2. Criar PR no GitHub
3. Aguardar review
4. Merge após aprovação

## 📊 Monitoramento e Métricas

### Coleta de Métricas

O sistema coleta as seguintes métricas:

- **Conectividade**: Status de ping (boolean)
- **Portas**: Status de portas TCP (boolean)
- **HTTP**: Status e tempo de resposta (boolean, float)
- **Uptime**: Percentual de disponibilidade
- **Latência**: Tempo de resposta médio

### Armazenamento de Dados

```python
# Estrutura de dados de telemetria
telemetry_data = {
    'server_name': str,
    'timestamp': datetime,
    'metrics': {
        'ping': {
            'status': bool,
            'response_time': float
        },
        'ports': {
            'app_port': bool,
            'admin_port': bool
        },
        'http': {
            'status': bool,
            'response_time': float,
            'status_code': int
        }
    }
}
```

## 🚀 Deploy e Distribuição

### Empacotamento

```bash
# Criar executável com PyInstaller
pyinstaller --onefile --windowed main.py

# Criar pacote wheel
python setup.py bdist_wheel

# Instalar localmente
pip install -e .
```

## 🔧 Configuração de IDE

### VSCode

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm

1. Configurar interpretador Python (venv)
2. Habilitar pytest como test runner
3. Configurar flake8 e mypy como linters
4. Configurar formatação automática com black

## 📝 Contribuindo

### Tipos de Contribuição

1. **Bug Reports**: Issues detalhados com reprodução
2. **Feature Requests**: Propostas de novas funcionalidades
3. **Code Contributions**: Pull requests com código
4. **Documentation**: Melhorias na documentação
5. **Testing**: Adição de testes

### Checklist para PR

- [ ] Código segue PEP 8
- [ ] Testes passam (pytest)
- [ ] Cobertura de testes mantida
- [ ] Documentação atualizada
- [ ] Type hints adicionados
- [ ] Changelog atualizado

## 🐛 Debug e Troubleshooting

### Logs de Debug

```python
# Habilitar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou via variável de ambiente
LOG_LEVEL=DEBUG python main.py
```

### Problemas Comuns

1. **Erro de Importação**: Verificar PYTHONPATH
2. **Timeout de Rede**: Ajustar configurações de timeout
3. **Permissões**: Executar como administrador para ping
4. **Dependências**: Reinstalar requirements.txt

### Profiling

```python
# Profiling de performance
import cProfile
cProfile.run('main_function()', 'profile_output')

# Análise de memória
from memory_profiler import profile

@profile
def monitored_function():
    # código a ser analisado
    pass
```

## 📚 Recursos Adicionais

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Matplotlib Guide](https://matplotlib.org/stable/users/index.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)