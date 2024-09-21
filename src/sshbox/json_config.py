import json
from typing import Dict, List

def load_json_config(file_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Load and parse the JSON configuration file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def get_groups(config: Dict[str, Dict[str, Dict[str, str]]]) -> List[str]:
    """Return a list of all groups in the configuration."""
    return list(config.keys())

def get_servers_in_group(config: Dict[str, Dict[str, Dict[str, str]]], group: str) -> List[str]:
    """Return a list of servers in the specified group."""
    return list(config[group].keys())

def get_server_config(config: Dict[str, Dict[str, Dict[str, str]]], group: str, server: str) -> Dict[str, str]:
    """Return the configuration for a specific server in a group."""
    return config[group][server]
