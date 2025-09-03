# Monitor Server

Um sistema avançado de monitoramento de servidores em Python com interface gráfica moderna e arquitetura modular.

## 🚀 Funcionalidades

### Monitoramento
- ✅ Verificação de conectividade (ping)
- 🔌 Monitoramento de portas TCP
- 🌐 Testes de conectividade HTTP/HTTPS
- 📊 Coleta de métricas de performance
- ⏱️ Monitoramento em tempo real

### Interface Gráfica
- 🎨 Interface moderna com tema escuro
- 📈 Gráficos de telemetria em tempo real
- 📋 Visualização de logs estruturados
- ⚙️ Configuração através da interface
- 🔔 Notificações visuais de status

### Alertas e Notificações
- 🔊 Alertas sonoros configuráveis
- 📧 Notificações por email (SMTP)
- 🚨 Alertas de servidor inativo/recuperado
- ⏰ Cooldown configurável para alertas

### Dados e Logs
- 📝 Logs estruturados em JSON
- 💾 Exportação de dados para CSV
- 📊 Retenção configurável de dados
- 🔄 Backup automático de configurações

## 📁 Estrutura do Projeto

```
monitor-server/
├── src/
│   └── monitor_server/
│       ├── core/           # Lógica principal
│       │   ├── monitor.py  # Classe principal ServerMonitor
│       │   ├── checks.py   # Funções de verificação
│       │   ├── alerts.py   # Sistema de alertas
│       │   └── network_utils.py # Utilitários de rede
│       ├── gui/            # Interface gráfica
│       │   ├── main_window.py   # Janela principal
│       │   ├── dialogs.py       # Diálogos personalizados
│       │   ├── telemetry.py     # Painel de telemetria
│       │   └── logs.py          # Painel de logs
│       ├── config/         # Configurações
│       │   ├── settings.py      # Configuração centralizada
│       │   └── constants.py     # Constantes do sistema
│       └── utils/          # Utilitários
│           └── file_utils.py    # Operações com arquivos
├── config/                 # Arquivos de configuração
├── data/                   # Dados e logs
├── logs/                   # Arquivos de log
├── scripts/                # Scripts auxiliares
└── tests/                  # Testes automatizados
```

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/monitor-server.git
   cd monitor-server
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o ambiente (opcional)**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

## 📖 Como Usar

### Interface Gráfica

1. **Iniciar o Sistema**:
   - Execute `python gui_monitor.py`
   - A interface será aberta com servidores pré-configurados

2. **Gerenciar Servidores**:
   - **➕ Adicionar**: Clique em "Adicionar Servidor" e preencha os dados
   - **➖ Remover**: Clique em "Remover Servidor" e digite o nome
   - **⚙️ Configurar**: Ajuste intervalos, timeouts e alertas

3. **Monitoramento**:
   - **▶️ Iniciar**: Clique em "Iniciar Monitoramento"
   - **⏹️ Parar**: Clique em "Parar Monitoramento"
   - Acompanhe o status em tempo real na tabela

4. **Abas Disponíveis**:
   - **📊 Status dos Servidores**: Tabela com status atual
   - **📈 Telemetria**: Gráficos de performance em tempo real
   - **📝 Logs**: Histórico de eventos e mensagens

### Configuração de Servidores

Cada servidor deve ter:
- **Nome**: Identificação única
- **Host/IP**: Endereço do servidor
- **Porta App**: Porta da aplicação (padrão: 8080)
- **Porta Admin**: Porta de administração (padrão: 4848)
- **URL Health**: URL para verificação HTTP (opcional)

### Exemplo de Configuração
```json
{
  "name": "Servidor Produção",
  "host": "192.168.1.100",
  "app_port": 8080,
  "admin_port": 4848,
  "health_url": "http://192.168.1.100:8080/health"
}
```

## ⚙️ Configurações

### Configurações Gerais
- **Intervalo de Monitoramento**: Tempo entre verificações (padrão: 30s)
- **Timeout de Ping**: Tempo limite para ping (padrão: 3s)
- **Timeout HTTP**: Tempo limite para requisições HTTP (padrão: 10s)
- **Alertas Sonoros**: Ativar/desativar beeps
- **Alertas por Email**: Ativar/desativar notificações

### Configuração de Email
Para receber alertas por email, configure:
- **Servidor SMTP**: Ex: smtp.gmail.com
- **Porta SMTP**: Ex: 587
- **Usuário**: Seu email
- **Senha**: Senha do email ou senha de app
- **Destinatários**: Lista de emails para receber alertas

### Exemplo Gmail
```python
CONFIG = {
    'email_alerts': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_user': 'seu-email@gmail.com',
    'email_password': 'sua-senha-de-app',
    'alert_recipients': ['admin@empresa.com', 'suporte@empresa.com']
}
```

## 📁 Estrutura de Arquivos

```
monitor-sever/
├── monitor.py              # Módulo principal de monitoramento
├── gui_monitor.py          # Interface gráfica completa
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── monitor.log            # Logs do sistema (gerado automaticamente)
├── monitor_history.csv    # Histórico em CSV (gerado automaticamente)
└── servers_config.json    # Configuração de servidores (gerado automaticamente)
```

## 📊 Status dos Servidores

### Indicadores Visuais
- **✅ ONLINE**: Servidor totalmente funcional
- **⚠️ HTTP_ERROR**: Servidor responde mas com erro HTTP
- **⚠️ PORTS_CLOSED**: Ping OK mas portas fechadas
- **❌ OFFLINE**: Servidor não responde ao ping

### Cores na Interface
- **🟢 Verde**: Servidor online
- **🟡 Amarelo**: Servidor com problemas
- **🔴 Vermelho**: Servidor offline

## 📈 Telemetria

O painel de telemetria oferece 4 gráficos em tempo real:

1. **Status de Conectividade**: Histórico de ping
2. **Tempo de Resposta HTTP**: Performance das requisições
3. **Disponibilidade das Portas**: Status das portas App e Admin
4. **Histórico de Status**: Percentual de uptime geral

## 📝 Logs e Histórico

### Arquivo de Log (monitor.log)
```
2024-01-15 10:30:15 - INFO - ✅ Servidor Local (localhost) - Ping: True | App: True | Admin: True | HTTP: 200 (0.05s)
2024-01-15 10:30:45 - INFO - ❌ Servidor Produção (192.168.1.100) - Ping: False | App: False | Admin: False
```

### Arquivo CSV (monitor_history.csv)
```csv
Timestamp,Server,Host,Ping,App_Port,Admin_Port,HTTP,Status
2024-01-15 10:30:15,Servidor Local,localhost,True,True,True,200 (0.05s),ONLINE
2024-01-15 10:30:45,Servidor Produção,192.168.1.100,False,False,False,,OFFLINE
```

## 🔧 Personalização

### Adicionar Novos Tipos de Verificação
Edite o arquivo `monitor.py` e adicione novas funções:

```python
def check_custom_service(self, host, port):
    """Verificação personalizada"""
    # Sua lógica aqui
    return True/False
```

### Modificar Intervalos
Altere as configurações no início do `monitor.py`:

```python
CONFIG = {
    'monitor_interval': 60,  # 60 segundos
    'ping_timeout': 5,       # 5 segundos
    'http_timeout': 15,      # 15 segundos
}
```

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Erro de Importação do matplotlib**:
   ```bash
   pip install matplotlib
   ```

2. **Ping não funciona no Windows**:
   - Execute como Administrador
   - Verifique se o Windows Defender não está bloqueando

3. **Alertas de email não funcionam**:
   - Verifique as configurações SMTP
   - Para Gmail, use senha de app em vez da senha normal
   - Ative "Acesso a apps menos seguros" se necessário

4. **Interface gráfica não abre**:
   - Verifique se o tkinter está instalado: `python -m tkinter`
   - No Linux: `sudo apt-get install python3-tk`

### Logs de Debug
Para mais informações de debug, verifique:
- Console da aplicação
- Arquivo `monitor.log`
- Aba "Logs" na interface gráfica

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte os logs para diagnóstico
- Verifique a seção de solução de problemas

---

**Desenvolvido com ❤️ para monitoramento eficiente de servidores GlassFish**