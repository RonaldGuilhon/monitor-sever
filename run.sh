#!/bin/bash

# Server Monitor - Unix/Linux Shell Script
# This script provides an easy way to run the Server Monitor on Unix/Linux systems

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
Server Monitor - Unix/Linux Launcher

Usage: $0 [options]

Options:
  --mode gui|console    Application mode (default: gui)
  --config FILE         Path to configuration file
  --debug               Enable debug logging
  --install             Install dependencies
  --setup-venv          Setup virtual environment
  --help                Show this help message

Examples:
  $0                    Start GUI mode
  $0 --mode console     Start console mode
  $0 --debug            Start with debug logging
  $0 --install          Install dependencies
  $0 --setup-venv       Setup virtual environment

EOF
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created."
    else
        print_info "Virtual environment already exists."
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment setup complete."
}

# Function to install dependencies
install_deps() {
    print_info "Installing dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    pip install -r requirements.txt
    print_success "Dependencies installed successfully."
}

# Function to check Python installation
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH."
        print_info "Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected."
}

# Parse command line arguments
MODE="gui"
CONFIG_FILE=""
DEBUG_MODE=""
INSTALL_ONLY=false
SETUP_VENV_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --debug)
            DEBUG_MODE="--debug"
            shift
            ;;
        --install)
            INSTALL_ONLY=true
            shift
            ;;
        --setup-venv)
            SETUP_VENV_ONLY=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
print_info "Server Monitor Launcher"
echo

# Check Python installation
check_python

# Setup virtual environment if requested
if [ "$SETUP_VENV_ONLY" = true ]; then
    setup_venv
    exit 0
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    setup_venv
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requested or if they're missing
if [ "$INSTALL_ONLY" = true ] || [ ! -f "venv/pyvenv.cfg" ]; then
    install_deps
fi

if [ "$INSTALL_ONLY" = true ]; then
    exit 0
fi

# Validate mode
if [ "$MODE" != "gui" ] && [ "$MODE" != "console" ]; then
    print_error "Invalid mode: $MODE. Must be 'gui' or 'console'."
    exit 1
fi

# Check config file if provided
if [ -n "$CONFIG_FILE" ] && [ ! -f "$CONFIG_FILE" ]; then
    print_error "Configuration file '$CONFIG_FILE' not found."
    exit 1
fi

# Run the application
print_info "Starting Server Monitor in $MODE mode..."
echo

# Build command
CMD="python3 run.py --mode $MODE"

if [ -n "$CONFIG_FILE" ]; then
    CMD="$CMD --config '$CONFIG_FILE'"
fi

if [ -n "$DEBUG_MODE" ]; then
    CMD="$CMD $DEBUG_MODE"
fi

# Execute the command
eval $CMD

# Check exit status
if [ $? -eq 0 ]; then
    print_success "Application exited successfully."
else
    print_error "Application exited with an error."
    exit 1
fi