import pytest
from collections import OrderedDict
from ..src.sshbox.json_config import (
    load_json_config,
    save_json_config,
    get_groups,
    get_hosts_in_group,
    add_group,
    add_host,
    remove_group,
    remove_host,
    edit_group,
    edit_host,
    create_sample_config
)

@pytest.fixture
def sample_config():
    return create_sample_config()

def test_get_groups(sample_config):
    groups = get_groups(sample_config)
    assert set(groups) == {"Production", "Development", "Testing"}

def test_get_hosts_in_group(sample_config):
    hosts = get_hosts_in_group(sample_config, "Production")
    assert set(hosts) == {"web-server", "db-server"}

def test_add_group(sample_config):
    add_group(sample_config, "Staging")
    assert "Staging" in get_groups(sample_config)

def test_add_host(sample_config):
    add_host(sample_config, "Development", "new-host", {"hostname": "new-host.example.com", "port": 22})
    assert "new-host" in get_hosts_in_group(sample_config, "Development")

def test_remove_group(sample_config):
    remove_group(sample_config, "Testing")
    assert "Testing" not in get_groups(sample_config)

def test_remove_host(sample_config):
    remove_host(sample_config, "Production", "web-server")
    assert "web-server" not in get_hosts_in_group(sample_config, "Production")

def test_edit_group(sample_config):
    edit_group(sample_config, "Development", "Dev")
    assert "Dev" in get_groups(sample_config)
    assert "Development" not in get_groups(sample_config)

def test_edit_host(sample_config):
    edit_host(sample_config, "Production", "db-server", "database-server", {"hostname": "db.example.com", "port": 2222})
    hosts = get_hosts_in_group(sample_config, "Production")
    assert "database-server" in hosts
    assert "db-server" not in hosts

def test_load_and_save_config(tmp_path):
    config_file = tmp_path / "test_config.json"
    original_config = create_sample_config()
    
    save_json_config(original_config, str(config_file))
    loaded_config = load_json_config(str(config_file))
    
    assert loaded_config == original_config
