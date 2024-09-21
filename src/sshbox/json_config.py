import json
import os
from collections import OrderedDict
from typing import Dict, List, Any

def load_json_config(file_path: str) -> OrderedDict[str, OrderedDict[str, Dict[str, Any]]]:
    """Load and parse the JSON configuration file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, 'r') as file:
        content = file.read().strip()
        if not content:
            raise ValueError(f"Configuration file is empty: {file_path}")
        
        try:
            return json.loads(content, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {file_path}\n{str(e)}")

def save_json_config(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], file_path: str) -> None:
    """Save the configuration to the JSON file."""
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=2)

def get_groups(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]]) -> List[str]:
    """Return a list of all groups in the configuration."""
    return list(config.keys())

def get_servers_in_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> List[str]:
    """Return a list of servers in the specified group."""
    return list(config[group].keys())

def get_server_config(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, server: str) -> Dict[str, Any]:
    """Return the configuration for a specific server in a group."""
    return config[group][server]

def add_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> None:
    """Add a new group to the configuration."""
    if group in config:
        raise ValueError(f"Group '{group}' already exists.")
    config[group] = OrderedDict()

def add_server(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, server: str, server_config: Dict[str, Any]) -> None:
    """Add a new server to a group in the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if server in config[group]:
        raise ValueError(f"Server '{server}' already exists in group '{group}'.")
    config[group][server] = server_config

def remove_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> None:
    """Remove a group from the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    del config[group]

def remove_server(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, server: str) -> None:
    """Remove a server from a group in the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if server not in config[group]:
        raise ValueError(f"Server '{server}' does not exist in group '{group}'.")
    del config[group][server]

def edit_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], old_group: str, new_group: str) -> None:
    """Edit a group name in the configuration."""
    if old_group not in config:
        raise ValueError(f"Group '{old_group}' does not exist.")
    if new_group in config:
        raise ValueError(f"Group '{new_group}' already exists.")
    config[new_group] = config.pop(old_group)

def edit_server(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, old_server: str, new_server: str, new_config: Dict[str, Any]) -> None:
    """Edit a server's name and configuration in a group."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if old_server not in config[group]:
        raise ValueError(f"Server '{old_server}' does not exist in group '{group}'.")
    if new_server in config[group] and old_server != new_server:
        raise ValueError(f"Server '{new_server}' already exists in group '{group}'.")
    del config[group][old_server]
    config[group][new_server] = new_config

def create_sample_config() -> OrderedDict[str, OrderedDict[str, Dict[str, Any]]]:
    """Create and return a sample configuration."""
    return {
        "development": {
            "web-server": {
                "hostname": "dev.example.com",
                "username": "devuser",
                "port": 22
            },
            "database": {
                "hostname": "db.dev.example.com",
                "username": "dbadmin",
                "port": 2222
            }
        },
        "production": {
            "web-server-1": {
                "hostname": "web1.example.com",
                "username": "produser",
                "port": 22
            },
            "web-server-2": {
                "hostname": "web2.example.com",
                "username": "produser",
                "port": 22
            },
            "database": {
                "hostname": "db.example.com",
                "username": "dbadmin",
                "port": 22
            }
        }
    }
