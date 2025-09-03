"""File utility functions"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional

def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json_file(file_path: str, default: Any = None) -> Any:
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return default or {}

def save_json_file(file_path: str, data: Any) -> bool:
    """Save data to JSON file with error handling"""
    try:
        # Ensure directory exists
        ensure_directory_exists(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def append_to_csv(file_path: str, data: Dict[str, Any], fieldnames: Optional[List[str]] = None) -> bool:
    """Append data to CSV file"""
    try:
        file_exists = os.path.exists(file_path)
        
        # Ensure directory exists
        ensure_directory_exists(os.path.dirname(file_path))
        
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            if not fieldnames:
                fieldnames = list(data.keys())
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
        return True
    except IOError:
        return False

def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except (FileNotFoundError, IOError):
        return []

def file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return os.path.exists(file_path)

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def backup_file(file_path: str, backup_suffix: str = '.bak') -> bool:
    """Create backup of file"""
    try:
        if file_exists(file_path):
            backup_path = file_path + backup_suffix
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            return True
        return False
    except IOError:
        return False