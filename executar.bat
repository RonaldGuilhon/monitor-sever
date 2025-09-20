@echo off
REM ========================================
REM    Monitor de Servidores - Executar
REM ========================================
REM
REM Este arquivo permite executar o Monitor de Servidores
REM com um duplo clique, sem necessidade de linha de comando.
REM

title Monitor de Servidores

REM Define o diretório do script como diretório de trabalho
cd /d "%~dp0"

echo.
echo ========================================
echo    🖥️  Monitor de Servidores
echo ========================================
echo.
echo Iniciando aplicacao...
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.8+ em:
    echo https://python.org/downloads/
    echo.
    echo Ou execute: python install.py
    echo.
    pause
    exit /b 1
)

REM Verifica se o ambiente virtual existe
if not exist "venv" (
    echo ⚠️  Ambiente virtual nao encontrado.
    echo.
    echo Executando instalacao automatica...
    echo.
    python install.py
    if errorlevel 1 (
        echo ❌ ERRO: Falha na instalacao automatica.
        echo.
        echo Execute manualmente: python install.py
        echo.
        pause
        exit /b 1
    )
)

REM Ativa o ambiente virtual
echo ✅ Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica se as dependências estão instaladas
python -c "import tkinter, matplotlib, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ ERRO: Falha ao instalar dependencias.
        echo.
        pause
        exit /b 1
    )
)

REM Executa a aplicação principal
echo ✅ Iniciando Monitor de Servidores...
echo.
echo 💡 Dica: Feche esta janela para encerrar o programa
echo.

python main.py

REM Mensagem de encerramento
echo.
echo ========================================
echo    Monitor de Servidores Encerrado
echo ========================================
echo.
echo Obrigado por usar o Monitor de Servidores!
echo.
pause