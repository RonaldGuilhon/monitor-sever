#!/usr/bin/env python3
"""
Server Monitor - Main Entry Point

This script provides a convenient way to start the Server Monitor application
with different modes and options.

Usage:
    python run.py [--mode gui|console] [--config CONFIG_FILE] [--help]

Examples:
    python run.py                    # Start GUI mode (default)
    python run.py --mode gui         # Start GUI mode explicitly
    python run.py --mode console     # Start console mode
    python run.py --config custom.json  # Use custom config file
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def setup_environment():
    """Setup environment variables and paths."""
    # Ensure data directories exist
    base_dir = Path(__file__).parent
    data_dirs = ['data', 'logs', 'config']
    
    for dir_name in data_dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
    
    # Set environment variables if not already set
    if not os.getenv('MONITOR_CONFIG_DIR'):
        os.environ['MONITOR_CONFIG_DIR'] = str(base_dir / 'config')
    
    if not os.getenv('MONITOR_DATA_DIR'):
        os.environ['MONITOR_DATA_DIR'] = str(base_dir / 'data')
    
    if not os.getenv('MONITOR_LOGS_DIR'):
        os.environ['MONITOR_LOGS_DIR'] = str(base_dir / 'logs')

def main():
    """Main entry point for the Server Monitor application."""
    parser = argparse.ArgumentParser(
        description='Server Monitor - Network and Service Monitoring Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Start GUI mode (default)
  %(prog)s --mode gui               Start GUI mode explicitly
  %(prog)s --mode console           Start console mode
  %(prog)s --config custom.json     Use custom configuration file
  %(prog)s --version                Show version information

For more information, see the README.md file.
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['gui', 'console'], 
        default='gui',
        help='Application mode (default: gui)'
    )
    
    parser.add_argument(
        '--config', 
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--version', 
        action='version',
        version='Server Monitor v1.0.0'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Set debug mode if requested
    if args.debug:
        os.environ['MONITOR_LOG_LEVEL'] = 'DEBUG'
    
    # Set custom config file if provided
    if args.config:
        if not os.path.exists(args.config):
            print(f"Error: Configuration file '{args.config}' not found.")
            sys.exit(1)
        os.environ['MONITOR_CONFIG_FILE'] = args.config
    
    try:
        if args.mode == 'gui':
            print("Starting Server Monitor GUI...")
            from monitor_server.gui.main_window import main as gui_main
            gui_main()
        elif args.mode == 'console':
            print("Starting Server Monitor Console...")
            from monitor_server.console import main as console_main
            console_main()
    
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()