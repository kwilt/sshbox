import json
import os
from typing import Dict, List

def load_json_config(file_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Load and parse the JSON configuration file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, 'r') as file:
        content = file.read().strip()
        if not content:
            raise ValueError(f"Configuration file is empty: {file_path}")
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {file_path}\n{str(e)}")

def get_groups(config: Dict[str, Dict[str, Dict[str, str]]]) -> List[str]:
    """Return a list of all groups in the configuration."""
    return list(config.keys())

def get_servers_in_group(config: Dict[str, Dict[str, Dict[str, str]]], group: str) -> List[str]:
    """Return a list of servers in the specified group."""
    return list(config[group].keys())

def get_server_config(config: Dict[str, Dict[str, Dict[str, str]]], group: str, server: str) -> Dict[str, str]:
    """Return the configuration for a specific server in a group."""
    return config[group][server]
