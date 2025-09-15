# 🚀 Monitor Server - Instalação Portátil

## ✨ Por que é 100% portátil?

O **Monitor Server** foi projetado para ser **100% portátil** e funcionar em qualquer sistema sem dependências complexas ou containers.

### 🎯 Vantagens da Instalação Portátil

- ✅ **Mais rápido**: Sem overhead de virtualização
- ✅ **Menor uso de recursos**: ~50MB vs ~500MB
- ✅ **Instalação simples**: Um comando apenas
- ✅ **Sem privilégios**: Não precisa de permissões especiais

## 🔧 Instalação Rápida

### Método 1: Instalador Automático (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/monitor-server.git
cd monitor-server

# Execute o instalador
python install.py
```

### Método 2: Instalação Manual

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar
cp .env.template .env
cp servers_config_example.json servers_config.json

# 5. Executar
python run.py
```

## 🖥️ Execução

### Windows
```cmd
# Usando o script criado pelo instalador
start.bat

# Ou manualmente
venv\Scripts\activate
python run.py
```

### Linux/macOS
```bash
# Usando o script criado pelo instalador
./start.sh

# Ou manualmente
source venv/bin/activate
python run.py
```

## ⚙️ Opções do Instalador

```bash
# Instalação básica
python install.py

# Instalação com dependências de desenvolvimento
python install.py --dev

# Instalação sem ambiente virtual (não recomendado)
python install.py --no-venv

# Ver ajuda
python install.py --help
```

## 📋 Requisitos Mínimos

- **Python**: 3.8 ou superior
- **RAM**: 64MB mínimo, 128MB recomendado
- **Disco**: 50MB para instalação completa
- **Rede**: Acesso aos servidores que deseja monitorar

## 🔧 Configuração

### 1. Variáveis de Ambiente (.env)
```bash
# Copie o template
cp .env.template .env

# Edite com suas configurações
nano .env  # ou notepad .env no Windows
```

### 2. Servidores (servers_config.json)
```bash
# Copie o exemplo
cp servers_config_example.json servers_config.json

# Configure seus servidores
nano servers_config.json
```

## 🔍 Solução de Problemas

### Erro: Python não encontrado
```bash
# Instale Python 3.8+
# Windows: https://python.org/downloads/
# Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv
# CentOS/RHEL: sudo yum install python3 python3-pip
# macOS: brew install python3
```

### Erro: Permissões no Linux/macOS
```bash
# Dar permissão ao script
chmod +x start.sh

# Ou executar com bash
bash start.sh
```

### Erro: Módulo não encontrado
```bash
# Reativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstalar dependências
pip install -r requirements.txt
```

## 📊 Comparação de Performance

| Aspecto | Monitor Server |
|---------|----------------|
| **Tempo de setup** | ~30 segundos |
| **Uso de RAM** | ~50-100MB |
| **Uso de disco** | ~50MB |
| **Complexidade** | Baixa |
| **Portabilidade** | Alta |
| **Performance** | Nativa |
| **Isolamento** | Processo |

## 🎉 Conclusão

A instalação portátil é a **melhor opção** para todos os casos de uso:

- ✅ **Desenvolvimento local**
- ✅ **Servidores pequenos/médios**
- ✅ **Uso pessoal**
- ✅ **Prototipagem rápida**
- ✅ **Ambientes com recursos limitados**

O Monitor Server é **100% portátil** e não requer containers ou virtualização.

---

**💡 Dica**: Comece agora mesmo com `python install.py` - é simples e eficiente!