#!/usr/bin/env python3
"""
Monitor Server - Instalador Automático
======================================

Este script instala automaticamente o Monitor Server em qualquer sistema
operacional (Windows, Linux, macOS) de forma portátil e eficiente.

Uso:
    python install.py [--dev] [--no-venv] [--help]

Opções:
    --dev      Instala dependências de desenvolvimento
    --no-venv  Não cria ambiente virtual (não recomendado)
    --help     Mostra esta ajuda
"""

import sys
import os
import subprocess
import platform
import argparse
from pathlib import Path
import shutil

class Colors:
    """Cores para output no terminal."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.GREEN):
    """Imprime mensagem colorida."""
    print(f"{color}{message}{Colors.END}")

def print_step(step, message):
    """Imprime passo da instalação."""
    print_colored(f"\n[{step}] {message}", Colors.BLUE + Colors.BOLD)

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print_step("1/7", "Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored("❌ Erro: Python 3.8+ é necessário!", Colors.RED)
        print_colored(f"   Versão atual: {version.major}.{version.minor}.{version.micro}", Colors.YELLOW)
        print_colored("   Baixe em: https://python.org/downloads/", Colors.YELLOW)
        return False
    
    print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK", Colors.GREEN)
    return True

def create_virtual_environment(no_venv=False):
    """Cria ambiente virtual."""
    if no_venv:
        print_colored("⚠️  Pulando criação de ambiente virtual (não recomendado)", Colors.YELLOW)
        return None
    
    print_step("2/7", "Criando ambiente virtual...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_colored("✅ Ambiente virtual já existe", Colors.GREEN)
        return venv_path
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✅ Ambiente virtual criado com sucesso", Colors.GREEN)
        return venv_path
    except subprocess.CalledProcessError:
        print_colored("❌ Erro ao criar ambiente virtual", Colors.RED)
        return None

def get_python_executable(venv_path):
    """Retorna o executável Python correto."""
    if not venv_path:
        return sys.executable
    
    system = platform.system().lower()
    if system == "windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def install_dependencies(python_exe, dev=False):
    """Instala dependências do projeto."""
    print_step("3/7", "Instalando dependências...")
    
    # Atualizar pip
    try:
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print_colored("✅ pip atualizado", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("⚠️  Aviso: Falha ao atualizar pip", Colors.YELLOW)
    
    # Instalar dependências principais
    try:
        subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_colored("✅ Dependências principais instaladas", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_colored("❌ Erro ao instalar dependências", Colors.RED)
        return False
    
    # Instalar dependências de desenvolvimento
    if dev:
        dev_requirements = Path("requirements-dev.txt")
        if dev_requirements.exists():
            try:
                subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements-dev.txt"], check=True)
                print_colored("✅ Dependências de desenvolvimento instaladas", Colors.GREEN)
            except subprocess.CalledProcessError:
                print_colored("⚠️  Aviso: Falha ao instalar dependências de dev", Colors.YELLOW)
    
    return True

def create_directories():
    """Cria diretórios necessários."""
    print_step("4/7", "Criando diretórios...")
    
    directories = ["config", "data", "logs"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print_colored(f"✅ Diretório '{dir_name}' criado", Colors.GREEN)

def setup_configuration():
    """Configura arquivos de configuração."""
    print_step("5/7", "Configurando arquivos...")
    
    # Copiar .env.template para .env se não existir
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists() and env_template.exists():
        shutil.copy2(env_template, env_file)
        print_colored("✅ Arquivo .env criado a partir do template", Colors.GREEN)
        print_colored("   📝 Edite o arquivo .env com suas configurações", Colors.YELLOW)
    elif env_file.exists():
        print_colored("✅ Arquivo .env já existe", Colors.GREEN)
    
    # Verificar servers_config.json
    config_file = Path("servers_config.json")
    example_config = Path("servers_config_example.json")
    
    if not config_file.exists() and example_config.exists():
        shutil.copy2(example_config, config_file)
        print_colored("✅ Configuração de servidores criada", Colors.GREEN)
    elif config_file.exists():
        print_colored("✅ Configuração de servidores já existe", Colors.GREEN)

def create_launcher_scripts(python_exe):
    """Cria scripts de inicialização."""
    print_step("6/7", "Criando scripts de inicialização...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Script Windows
        script_content = f'''@echo off
cd /d "%~dp0"
"{python_exe}" run.py %*
pause
'''
        with open("start.bat", "w") as f:
            f.write(script_content)
        print_colored("✅ Script start.bat criado", Colors.GREEN)
    
    else:
        # Script Unix/Linux/macOS
        script_content = f'''#!/bin/bash
cd "$(dirname "$0")"
"{python_exe}" run.py "$@"
'''
        with open("start.sh", "w") as f:
            f.write(script_content)
        os.chmod("start.sh", 0o755)
        print_colored("✅ Script start.sh criado", Colors.GREEN)

def test_installation(python_exe):
    """Testa a instalação."""
    print_step("7/7", "Testando instalação...")
    
    try:
        result = subprocess.run([str(python_exe), "-c", 
            "import sys; sys.path.insert(0, 'src'); "
            "from monitor_server.config.settings import Settings; "
            "print('✅ Instalação OK')"], 
            capture_output=True, text=True, check=True)
        print_colored("✅ Teste de instalação passou!", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored("❌ Teste de instalação falhou:", Colors.RED)
        print_colored(f"   {e.stderr}", Colors.RED)
        return False

def print_success_message(venv_path):
    """Imprime mensagem de sucesso."""
    print_colored("\n" + "="*60, Colors.GREEN + Colors.BOLD)
    print_colored("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!", Colors.GREEN + Colors.BOLD)
    print_colored("="*60, Colors.GREEN + Colors.BOLD)
    
    print_colored("\n📋 Como usar:", Colors.BLUE + Colors.BOLD)
    
    if venv_path:
        system = platform.system().lower()
        if system == "windows":
            print_colored("   • Executar: start.bat", Colors.GREEN)
            print_colored("   • Ou: venv\\Scripts\\activate && python run.py", Colors.GREEN)
        else:
            print_colored("   • Executar: ./start.sh", Colors.GREEN)
            print_colored("   • Ou: source venv/bin/activate && python run.py", Colors.GREEN)
    else:
        print_colored("   • Executar: python run.py", Colors.GREEN)
    
    print_colored("\n📝 Próximos passos:", Colors.BLUE + Colors.BOLD)
    print_colored("   1. Edite o arquivo .env com suas configurações", Colors.YELLOW)
    print_colored("   2. Configure servers_config.json com seus servidores", Colors.YELLOW)
    print_colored("   3. Execute o monitor!", Colors.YELLOW)
    
    print_colored("\n📚 Documentação:", Colors.BLUE + Colors.BOLD)
    print_colored("   • README.md - Guia geral", Colors.GREEN)
    print_colored("   • SECURITY.md - Práticas de segurança", Colors.GREEN)
    print_colored("   • docs/ - Documentação técnica", Colors.GREEN)

def main():
    """Função principal do instalador."""
    parser = argparse.ArgumentParser(description="Monitor Server - Instalador Portátil")
    parser.add_argument("--dev", action="store_true", help="Instalar dependências de desenvolvimento")
    parser.add_argument("--no-venv", action="store_true", help="Não criar ambiente virtual")
    args = parser.parse_args()
    
    print_colored("🚀 Monitor Server - Instalador Portátil", Colors.BLUE + Colors.BOLD)
    print_colored("="*50, Colors.BLUE)
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Criar ambiente virtual
    venv_path = create_virtual_environment(args.no_venv)
    if venv_path is False:
        sys.exit(1)
    
    # Obter executável Python
    python_exe = get_python_executable(venv_path)
    
    # Instalar dependências
    if not install_dependencies(python_exe, args.dev):
        sys.exit(1)
    
    # Criar diretórios
    create_directories()
    
    # Configurar arquivos
    setup_configuration()
    
    # Criar scripts
    create_launcher_scripts(python_exe)
    
    # Testar instalação
    if not test_installation(python_exe):
        sys.exit(1)
    
    # Mensagem de sucesso
    print_success_message(venv_path)

if __name__ == "__main__":
    main()