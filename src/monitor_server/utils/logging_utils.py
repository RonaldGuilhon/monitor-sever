"""Logging utility functions"""

import logging
import os
from pathlib import Path

def setup_logging(log_file='server_monitor.log', level=logging.INFO):
    """Setup logging configuration"""
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_logger(name=None):
    """Get logger instance"""
    return logging.getLogger(name or __name__)

def log_exception(logger, message, exc_info=True):
    """Log exception with traceback"""
    logger.error(message, exc_info=exc_info)

def log_server_event(logger, server_name, event_type, message, level=logging.INFO):
    """Log server-specific event"""
    formatted_message = f"[{server_name}] {event_type}: {message}"
    logger.log(level, formatted_message)