import click
import os
import sys
import json
import subprocess
from dotenv import load_dotenv
from .json_config import load_json_config, get_groups, get_servers_in_group, get_server_config, create_sample_config

def select_with_click(options, prompt_text):
    click.echo(prompt_text)
    for idx, option in enumerate(options, start=1):
        click.echo(f"{idx}. {option}")
    
    def get_character():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    while True:
        char = get_character()
        if char.isdigit() and 0 < int(char) <= len(options):
            return options[int(char) - 1]
        elif char in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
            return None

# Load environment variables from .env file
load_dotenv()

# Get the JSON config file path from environment variable or use a default
config_file = os.getenv('JSON_CONFIG_FILE_PATH', os.path.expanduser('~/.sshbox_config.json'))

try:
    # Load the JSON configuration
    configs = load_json_config(config_file)
except FileNotFoundError:
    # If the file doesn't exist, create it with sample configuration
    configs = create_sample_config()
    with open(config_file, 'w') as f:
        json.dump(configs, f, indent=2)
    click.echo(f"Created sample configuration file: {config_file}")
except ValueError as e:
    if "Configuration file is empty" in str(e):
        # If the file is empty, create sample configuration
        configs = create_sample_config()
        with open(config_file, 'w') as f:
            json.dump(configs, f, indent=2)
        click.echo(f"Created sample configuration in empty file: {config_file}")
    else:
        click.echo(f"Error loading configuration: {str(e)}", err=True)
        sys.exit(1)

@click.group()
def cli():
    """CLI for managing SSH connections using JSON configuration."""
    pass

@cli.command()
def list_groups():
    """List all available server groups and allow selection."""
    groups = get_groups(configs)
    group = select_with_click(groups, "Select a server group:")
    if group:
        select_and_connect_to_server(group)
    else:
        click.echo("No group selected.")

def select_and_connect_to_server(group):
    """Select a server from the chosen group and initiate SSH connection."""
    servers = get_servers_in_group(configs, group)
    server = select_with_click(servers, f"Select a server from group '{group}':")
    
    if not server:
        click.echo("No server selected.")
        return

    server_config = get_server_config(configs, group, server)
    hostname = server_config['hostname']
    username = server_config['username']
    port = server_config.get('port', 22)
    
    click.echo(f"Connecting to {username}@{hostname}:{port}...")
    
    try:
        subprocess.run(['ssh', f'{username}@{hostname}', '-p', str(port)], check=True)
    except subprocess.CalledProcessError:
        click.echo("Failed to establish SSH connection.", err=True)
    except FileNotFoundError:
        click.echo("SSH client not found. Please make sure SSH is installed on your system.", err=True)

@cli.command()
@click.argument('group')
def list_servers(group):
    """List all servers in a specific group."""
    if group not in configs:
        click.echo(f"Group '{group}' not found.")
        return
    servers = get_servers_in_group(configs, group)
    click.echo(f"Servers in group '{group}':")
    for idx, server in enumerate(servers, start=1):
        click.echo(f"{idx}. {server}")

@cli.command()
@click.argument('group')
@click.argument('server')
def show_config(group, server):
    """Show configuration for a specific server in a group."""
    if group not in configs:
        click.echo(f"Group '{group}' not found.")
        return
    if server not in configs[group]:
        click.echo(f"Server '{server}' not found in group '{group}'.")
        return
    config = get_server_config(configs, group, server)
    click.echo(f"Configuration for {server} in group {group}:")
    for key, value in config.items():
        click.echo(f"{key}: {value}")

if __name__ == '__main__':
    cli()
