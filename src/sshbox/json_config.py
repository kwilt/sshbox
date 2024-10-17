import json
import os
from collections import OrderedDict
from typing import Dict, List, Any, Union

def load_json_config(file_path: str) -> OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]]:
    """Load and parse the JSON configuration file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, 'r') as file:
        content = file.read().strip()
        if not content:
            raise ValueError(f"Configuration file is empty: {file_path}")
        
        try:
            return json.loads(content, object_pairs_hook=lambda x: OrderedDict(x))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {file_path}\n{str(e)}")

def save_json_config(config: OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]], file_path: str) -> None:
    """Save the configuration to the JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=2)

def get_groups(config: OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]]) -> List[str]:
    """Return a list of all groups in the configuration, excluding app_settings."""
    return [key for key, value in config.items() if isinstance(value, OrderedDict) and key != "app_settings"]

def get_app_settings(config: OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]]) -> Dict[str, Any]:
    """Return the app settings from the configuration."""
    default_settings = {
        "table_colors": {
            "selection_number": "cyan",
            "hostname": "yellow",
            "group": "green"
        }
    }
    app_settings = config.get("app_settings", {})
    default_settings.update(app_settings)
    return default_settings

def set_app_settings(config: OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]], settings: Dict[str, Any]) -> None:
    """Set the app settings in the configuration."""
    config["app_settings"] = settings

def get_hosts_in_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> List[str]:
    """Return a list of hosts in the specified group."""
    return list(config[group].keys())

def get_host_config(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, host: str) -> Dict[str, Any]:
    """Return the configuration for a specific host in a group."""
    return config[group][host]

def add_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> None:
    """Add a new group to the configuration."""
    if group in config:
        raise ValueError(f"Group '{group}' already exists.")
    config[group] = OrderedDict()

def add_host(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, host: str, host_config: Dict[str, Any]) -> None:
    """Add a new host to a group in the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if host in config[group]:
        raise ValueError(f"host '{host}' already exists in group '{group}'.")
    config[group][host] = host_config

def remove_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str) -> None:
    """Remove a group from the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    del config[group]

def remove_host(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, host: str) -> None:
    """Remove a host from a group in the configuration."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if host not in config[group]:
        raise ValueError(f"host '{host}' does not exist in group '{group}'.")
    del config[group][host]

def edit_group(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], old_group: str, new_group: str) -> None:
    """Edit a group name in the configuration while preserving order."""
    if old_group not in config:
        raise ValueError(f"Group '{old_group}' does not exist.")
    if new_group in config:
        raise ValueError(f"Group '{new_group}' already exists.")
    items = list(config.items())
    for i, (key, value) in enumerate(items):
        if key == old_group:
            items[i] = (new_group, value)
            break
    config.clear()
    config.update(items)

def edit_host(config: OrderedDict[str, OrderedDict[str, Dict[str, Any]]], group: str, old_host: str, new_host: str, new_config: Dict[str, Any]) -> None:
    """Edit a host's name and configuration in a group while preserving order."""
    if group not in config:
        raise ValueError(f"Group '{group}' does not exist.")
    if old_host not in config[group]:
        raise ValueError(f"Host '{old_host}' does not exist in group '{group}'.")
    if new_host in config[group] and old_host != new_host:
        raise ValueError(f"Host '{new_host}' already exists in group '{group}'.")
    items = list(config[group].items())
    for i, (key, value) in enumerate(items):
        if key == old_host:
            items[i] = (new_host, new_config)
            break
    config[group].clear()
    config[group].update(items)

def create_sample_config() -> OrderedDict[str, Union[Dict[str, Any], OrderedDict[str, Dict[str, Any]]]]:
    """Create and return a sample configuration."""
    return OrderedDict([
        ("app_settings", {
            "table_colors": {
                "selection_number": "cyan",
                "hostname": "yellow",
                "group": "green"
            }
        }),
        ("Development", OrderedDict([
            ("web-host", {
                "hostname": "dev.example.com",
                "username": "devuser",
                "port": 22
            }),
            ("database", {
                "hostname": "db.dev.example.com",
                "username": "dbadmin",
                "port": 22
            })
        ])),
        ("Production", OrderedDict([
            ("web-host-1", {
                "hostname": "web1.example.com",
                "username": "produser",
                "port": 22
            }),
            ("web-host-2", {
                "hostname": "web2.example.com",
                "username": "produser",
                "port": 22
            }),
            ("database", {
                "hostname": "db.example.com",
                "username": "dbadmin",
                "port": 22
            })
        ]))
    ])
