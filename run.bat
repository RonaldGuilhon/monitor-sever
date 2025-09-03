@echo off
REM Server Monitor - Windows Batch Script
REM This script provides an easy way to run the Server Monitor on Windows

setlocal enabledelayedexpansion

REM Set the script directory as the working directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\tkinter" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Parse command line arguments
set MODE=gui
set CONFIG_FILE=
set DEBUG_MODE=

:parse_args
if "%1"=="" goto run_app
if "%1"=="--mode" (
    set MODE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--config" (
    set CONFIG_FILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--debug" (
    set DEBUG_MODE=--debug
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)
shift
goto parse_args

:run_app
echo Starting Server Monitor in %MODE% mode...
echo.

REM Run the application
if "%CONFIG_FILE%"=="" (
    python run.py --mode %MODE% %DEBUG_MODE%
) else (
    python run.py --mode %MODE% --config "%CONFIG_FILE%" %DEBUG_MODE%
)

if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)

goto end

:show_help
echo Server Monitor - Windows Launcher
echo.
echo Usage: %0 [options]
echo.
echo Options:
echo   --mode gui^|console    Application mode (default: gui)
echo   --config FILE         Path to configuration file
echo   --debug               Enable debug logging
echo   --help                Show this help message
echo.
echo Examples:
echo   %0                    Start GUI mode
echo   %0 --mode console     Start console mode
echo   %0 --debug            Start with debug logging
echo.
pause

:end
endlocal