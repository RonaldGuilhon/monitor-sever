# Documentação da API

Este documento descreve a API interna do sistema de monitoramento de servidores, incluindo classes, métodos e interfaces disponíveis para uso programático.

## 📋 Índice

- [Core API](#core-api)
- [Configuration API](#configuration-api)
- [GUI API](#gui-api)
- [Utils API](#utils-api)
- [Exemplos de Uso](#exemplos-de-uso)

## 🔧 Core API

### ServerMonitor

Classe principal para gerenciar o monitoramento de servidores.

```python
from src.monitor_server.core import ServerMonitor

class ServerMonitor:
    def __init__(self, servers: List[Dict], config: Dict = None)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def monitor_server(self, server: Dict) -> Dict[str, Any]
    def get_server_logs(self, server_name: str) -> List[Dict]
    def save_server_logs(self) -> None
```

#### Métodos

**`__init__(servers, config=None)`**
- **Descrição**: Inicializa o monitor com lista de servidores
- **Parâmetros**:
  - `servers`: Lista de dicionários com configuração dos servidores
  - `config`: Configurações opcionais (usa padrão se None)
- **Exemplo**:
  ```python
  servers = [{
      'name': 'Web Server',
      'host': '192.168.1.100',
      'app_port': 8080,
      'admin_port': 4848,
      'health_url': 'http://192.168.1.100:8080/health'
  }]
  monitor = ServerMonitor(servers)
  ```

**`start_monitoring()`**
- **Descrição**: Inicia o monitoramento em thread separada
- **Retorno**: None
- **Exemplo**:
  ```python
  monitor.start_monitoring()
  print("Monitoramento iniciado")
  ```

**`stop_monitoring()`**
- **Descrição**: Para o monitoramento e finaliza threads
- **Retorno**: None
- **Exemplo**:
  ```python
  monitor.stop_monitoring()
  print("Monitoramento parado")
  ```

**`monitor_server(server)`**
- **Descrição**: Executa verificação completa de um servidor
- **Parâmetros**:
  - `server`: Dicionário com configuração do servidor
- **Retorno**: Dict com resultados das verificações
- **Exemplo**:
  ```python
  result = monitor.monitor_server(server)
  print(f"Status: {result['overall_status']}")
  ```

### Funções de Verificação

```python
from src.monitor_server.core.checks import (
    check_ping, check_port, check_http, check_server_health
)
```

**`check_ping(host, timeout=5)`**
- **Descrição**: Verifica conectividade ICMP
- **Parâmetros**:
  - `host`: Endereço IP ou hostname
  - `timeout`: Timeout em segundos (padrão: 5)
- **Retorno**: bool
- **Exemplo**:
  ```python
  is_reachable = check_ping('192.168.1.100')
  if is_reachable:
      print("Servidor acessível")
  ```

**`check_port(host, port, timeout=5)`**
- **Descrição**: Verifica se porta TCP está aberta
- **Parâmetros**:
  - `host`: Endereço IP ou hostname
  - `port`: Número da porta
  - `timeout`: Timeout em segundos (padrão: 5)
- **Retorno**: bool
- **Exemplo**:
  ```python
  port_open = check_port('192.168.1.100', 8080)
  if port_open:
      print("Porta 8080 está aberta")
  ```

**`check_http(url, timeout=10)`**
- **Descrição**: Verifica resposta HTTP/HTTPS
- **Parâmetros**:
  - `url`: URL completa para verificação
  - `timeout`: Timeout em segundos (padrão: 10)
- **Retorno**: Tuple[bool, float, int] (sucesso, tempo_resposta, status_code)
- **Exemplo**:
  ```python
  success, response_time, status = check_http('http://192.168.1.100:8080/health')
  if success:
      print(f"HTTP OK - {response_time:.2f}s - Status: {status}")
  ```

**`check_server_health(server, timeout_ping=5, timeout_http=10)`**
- **Descrição**: Executa verificação completa do servidor
- **Parâmetros**:
  - `server`: Dict com configuração do servidor
  - `timeout_ping`: Timeout para ping (padrão: 5)
  - `timeout_http`: Timeout para HTTP (padrão: 10)
- **Retorno**: Dict com todos os resultados
- **Exemplo**:
  ```python
  health = check_server_health(server_config)
  print(f"Status geral: {health['overall_status']}")
  print(f"Ping: {health['ping']}")
  print(f"Porta App: {health['app_port']}")
  print(f"HTTP: {health['http']}")
  ```

### AlertManager

Gerenciador de alertas e notificações.

```python
from src.monitor_server.core.alerts import AlertManager

class AlertManager:
    def __init__(self, config: Dict = None)
    def send_server_down_alert(self, server_name: str) -> bool
    def send_server_recovery_alert(self, server_name: str) -> bool
    def send_email_alert(self, subject: str, message: str) -> bool
    def play_sound_alert(self) -> bool
```

**Exemplo de Uso**:
```python
alert_manager = AlertManager()

# Alerta de servidor inativo
alert_manager.send_server_down_alert("Web Server")

# Alerta de recuperação
alert_manager.send_server_recovery_alert("Web Server")

# Alerta sonoro
alert_manager.play_sound_alert()
```

## ⚙️ Configuration API

### Settings

Classe para gerenciar configurações do sistema.

```python
from src.monitor_server.config import settings, Settings

class Settings:
    def get(self, section: str, key: str = None, default: Any = None) -> Any
    def set(self, section: str, key: str, value: Any) -> None
    def save_to_file(self) -> None
    def get_servers(self) -> List[Dict]
    def set_servers(self, servers: List[Dict]) -> None
```

**Exemplo de Uso**:
```python
# Obter configuração
interval = settings.get("monitoring", "interval")
print(f"Intervalo atual: {interval}s")

# Definir configuração
settings.set("monitoring", "interval", 60)

# Salvar alterações
settings.save_to_file()

# Propriedades de conveniência
print(f"Timeout ping: {settings.ping_timeout}s")
print(f"Timeout HTTP: {settings.http_timeout}s")
```

### Configurações Disponíveis

#### Seção: monitoring
- `interval`: Intervalo entre verificações (segundos)
- `timeout_ping`: Timeout para ping (segundos)
- `timeout_http`: Timeout para HTTP (segundos)
- `timeout_port`: Timeout para portas (segundos)
- `max_retries`: Número máximo de tentativas
- `retry_delay`: Delay entre tentativas (segundos)

#### Seção: alerts
- `sound_enabled`: Habilitar alertas sonoros (bool)
- `email_enabled`: Habilitar alertas por email (bool)
- `email_cooldown`: Cooldown entre emails (segundos)

#### Seção: email
- `smtp_server`: Servidor SMTP
- `smtp_port`: Porta SMTP
- `use_tls`: Usar TLS (bool)
- `username`: Usuário SMTP
- `password`: Senha SMTP
- `from_email`: Email remetente
- `to_emails`: Lista de destinatários

## 🖥️ GUI API

### ServerMonitorGUI

Interface gráfica principal.

```python
from src.monitor_server.gui import ServerMonitorGUI

class ServerMonitorGUI:
    def __init__(self, root=None)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def add_server(self) -> None
    def edit_server(self) -> None
    def remove_server(self) -> None
    def update_servers_display(self) -> None
```

**Exemplo de Uso**:
```python
import tkinter as tk
from src.monitor_server.gui import ServerMonitorGUI

root = tk.Tk()
app = ServerMonitorGUI(root)
root.mainloop()
```

### Diálogos Personalizados

```python
from src.monitor_server.gui.dialogs import (
    DarkMessageBox, ServerDialog, ConfigDialog
)
```

**DarkMessageBox**
```python
# Mensagem de informação
DarkMessageBox.showinfo("Título", "Mensagem")

# Mensagem de erro
DarkMessageBox.showerror("Erro", "Descrição do erro")

# Pergunta sim/não
result = DarkMessageBox.askyesno("Confirmar", "Deseja continuar?")
```

**ServerDialog**
```python
# Adicionar novo servidor
dialog = ServerDialog(parent, "Novo Servidor")
if dialog.result:
    server_data = dialog.get_server_data()
    print(f"Servidor: {server_data['name']}")
```

## 🛠️ Utils API

### File Utils

```python
from src.monitor_server.utils.file_utils import (
    ensure_directory_exists,
    load_json_file,
    save_json_file,
    append_to_csv,
    backup_file
)
```

**Funções Disponíveis**:

```python
# Garantir que diretório existe
ensure_directory_exists("/path/to/directory")

# Carregar arquivo JSON
data = load_json_file("config.json")

# Salvar arquivo JSON
save_json_file("output.json", data)

# Adicionar linha ao CSV
append_to_csv("logs.csv", ["timestamp", "server", "status"])

# Fazer backup de arquivo
backup_file("important.json")
```

### Network Utils

```python
from src.monitor_server.core.network_utils import (
    validate_url,
    format_url
)
```

**Funções Disponíveis**:

```python
# Validar URL
is_valid = validate_url("http://example.com")

# Formatar URL
formatted = format_url("example.com", 8080, "/health")
# Resultado: "http://example.com:8080/health"
```

## 📊 Exemplos de Uso

### 1. Monitoramento Básico

```python
from src.monitor_server.core import ServerMonitor
from src.monitor_server.config import settings

# Configurar servidores
servers = [
    {
        'name': 'Web Server',
        'host': '192.168.1.100',
        'app_port': 8080,
        'admin_port': 4848,
        'health_url': 'http://192.168.1.100:8080/health'
    },
    {
        'name': 'Database Server',
        'host': '192.168.1.101',
        'app_port': 5432,
        'admin_port': None,
        'health_url': None
    }
]

# Inicializar monitor
monitor = ServerMonitor(servers)

# Configurar intervalo
settings.set("monitoring", "interval", 30)

# Iniciar monitoramento
monitor.start_monitoring()

try:
    # Manter programa rodando
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop_monitoring()
    print("Monitoramento finalizado")
```

### 2. Verificação Manual

```python
from src.monitor_server.core.checks import check_server_health

server = {
    'name': 'Test Server',
    'host': 'google.com',
    'app_port': 80,
    'admin_port': 443,
    'health_url': 'https://google.com'
}

# Verificar saúde do servidor
result = check_server_health(server)

print(f"Servidor: {server['name']}")
print(f"Ping: {'✓' if result['ping'] else '✗'}")
print(f"Porta 80: {'✓' if result['app_port'] else '✗'}")
print(f"Porta 443: {'✓' if result['admin_port'] else '✗'}")
print(f"HTTP: {'✓' if result['http'] else '✗'}")
print(f"Status Geral: {result['overall_status']}")
```

### 3. Configuração Personalizada

```python
from src.monitor_server.config import settings

# Configurar timeouts
settings.set("monitoring", "timeout_ping", 3)
settings.set("monitoring", "timeout_http", 15)

# Configurar alertas por email
settings.set("alerts", "email_enabled", True)
settings.set("email", "smtp_server", "smtp.gmail.com")
settings.set("email", "smtp_port", 587)
settings.set("email", "username", "seu_email@gmail.com")
settings.set("email", "password", "sua_senha_de_app")
settings.set("email", "to_emails", ["admin@empresa.com"])

# Salvar configurações
settings.save_to_file()

print("Configurações salvas com sucesso!")
```

### 4. Interface Gráfica Personalizada

```python
import tkinter as tk
from src.monitor_server.gui import ServerMonitorGUI
from src.monitor_server.config import settings

# Configurar tema
settings.set("gui", "theme", "dark")
settings.set("gui", "window_width", 1400)
settings.set("gui", "window_height", 900)

# Criar janela principal
root = tk.Tk()
root.title("Monitor de Servidores - Empresa XYZ")

# Inicializar GUI
app = ServerMonitorGUI(root)

# Executar aplicação
root.mainloop()
```

### 5. Integração com Sistema Externo

```python
import json
import requests
from src.monitor_server.core import ServerMonitor

class CustomMonitor(ServerMonitor):
    """Monitor personalizado com integração externa"""
    
    def __init__(self, servers, webhook_url=None):
        super().__init__(servers)
        self.webhook_url = webhook_url
    
    def on_server_status_change(self, server_name, old_status, new_status):
        """Callback chamado quando status do servidor muda"""
        if self.webhook_url:
            payload = {
                'server': server_name,
                'old_status': old_status,
                'new_status': new_status,
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                requests.post(self.webhook_url, json=payload, timeout=5)
            except requests.RequestException as e:
                print(f"Erro ao enviar webhook: {e}")

# Usar monitor personalizado
monitor = CustomMonitor(
    servers=servers,
    webhook_url="https://api.empresa.com/webhooks/server-status"
)

monitor.start_monitoring()
```

## 🔍 Tratamento de Erros

### Exceções Comuns

```python
from src.monitor_server.core.checks import check_ping, check_port, check_http

try:
    # Verificações podem gerar exceções
    ping_result = check_ping("invalid-host")
except ValueError as e:
    print(f"Erro de validação: {e}")
except ConnectionError as e:
    print(f"Erro de conexão: {e}")
except TimeoutError as e:
    print(f"Timeout: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

### Logging de Erros

```python
import logging
from src.monitor_server.config import settings

# Configurar logging
logging.basicConfig(
    level=settings.log_level,
    format=settings.get("logging", "format"),
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    # Operação que pode falhar
    result = check_server_health(server)
except Exception as e:
    logger.error(f"Erro ao verificar servidor {server['name']}: {e}")
    # Continuar execução ou tomar ação apropriada
```

## 📚 Referências

- [Documentação de Desenvolvimento](DEVELOPMENT.md)
- [Guia de Configuração](../README.md#configuração)
- [Exemplos de Uso](../examples/)
- [Testes](../tests/)