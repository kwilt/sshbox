import os
import click
from dotenv import load_dotenv

from .json_config import (
    load_json_config, save_json_config, get_groups, get_servers_in_group,
    create_sample_config, add_group, add_server, remove_group, remove_server,
    edit_group, edit_server
)

def select_with_click(options, prompt_text):
    click.echo(prompt_text)
    for index, option in enumerate(options, start=1):
        click.echo(f"{index}. {option}")
    
    while True:
        user_input = click.prompt("Enter the number of your choice", type=int)
        if 0 < user_input <= len(options):
            return options[user_input - 1]
        click.echo("Invalid choice. Please try again.")

def select_option(options, prompt_text):
    click.echo(prompt_text)
    for index, option in enumerate(options, start=1):
        click.echo(f"{index}. {option}")
    
    while True:
        user_input = click.prompt("Enter the number of your choice", type=int)
        if 0 < user_input <= len(options):
            return options[user_input - 1]
        click.echo("Invalid choice. Please try again.")

# Load environment variables from .env file
load_dotenv()

# Get the JSON config file path from environment variable or use a default
config_file = os.getenv('JSON_CONFIG_FILE_PATH', os.path.expanduser('~/.ssh/sshbox.json'))

try:
    # Load the JSON configuration
    configs = load_json_config(config_file)
except FileNotFoundError:
    # If the file doesn't exist, create it with sample configuration
    configs = create_sample_config()
    save_json_config(configs, config_file)
    click.echo(f"Created sample configuration file: {config_file}")
except ValueError as e:
    if "Configuration file is empty" in str(e):
        # If the file is empty, create sample configuration
        configs = create_sample_config()
        save_json_config(configs, config_file)
        click.echo(f"Created sample configuration in empty file: {config_file}")
    else:
        click.echo(f"Error loading configuration: {str(e)}", err=True)
        exit(1)

@click.group()
def cli():
    """CLI for managing SSH connections using JSON configuration."""
    pass

@cli.command()
def add():
    """Add a new group or server to the configuration."""
    choice = select_option(['group', 'server'], "Do you want to add a new group or a new server?")
    
    if choice == 'group':
        group = click.prompt("Enter the name of the new group")
        try:
            add_group(configs, group)
            click.echo(f"Group '{group}' added successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        groups = get_groups(configs)
        group = select_option(groups, "Select a group to add the server to:")
        
        server = click.prompt("Enter the name of the new server")
        hostname = click.prompt("Enter the hostname")
        username = click.prompt("Enter the username")
        port = click.prompt("Enter the port (default: 22)", default=22, type=int)
        
        server_config = {
            "hostname": hostname,
            "username": username,
            "port": port
        }
        
        try:
            add_server(configs, group, server, server_config)
            click.echo(f"Server '{server}' added successfully to group '{group}'.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    
    save_json_config(configs, config_file)

@cli.command()
def remove():
    """Remove a group or server from the configuration."""
    choice = select_option(['group', 'server'], "Do you want to remove a group or a server?")
    
    if choice == 'group':
        groups = get_groups(configs)
        group = select_option(groups, "Select a group to remove:")
        
        try:
            remove_group(configs, group)
            click.echo(f"Group '{group}' removed successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        groups = get_groups(configs)
        group = select_option(groups, "Select a group:")
        
        servers = get_servers_in_group(configs, group)
        server = select_option(servers, f"Select a server to remove:")
        
        try:
            remove_server(configs, group, server)
            click.echo(f"Server '{server}' removed successfully from group '{group}'.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    
    save_json_config(configs, config_file)

@cli.command()
def edit():
    """Edit a group or server in the configuration."""
    choice = select_option(['group', 'server'], "Do you want to edit a group or a server?")
    
    if choice == 'group':
        groups = get_groups(configs)
        old_group = select_option(groups, "Select a group to edit:")
        
        new_group = click.prompt(f"Enter the new name for group '{old_group}'")
        try:
            edit_group(configs, old_group, new_group)
            click.echo(f"Group '{old_group}' renamed to '{new_group}' successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        groups = get_groups(configs)
        group = select_option(groups, "Select a group:")
        
        servers = get_servers_in_group(configs, group)
        old_server = select_option(servers, f"Select a server to edit:")
        
        new_server = click.prompt(f"Enter the new name for server '{old_server}' (press Enter to keep the same name)", default=old_server)
        hostname = click.prompt("Enter the new hostname", default=configs[group][old_server]['hostname'])
        username = click.prompt("Enter the new username", default=configs[group][old_server]['username'])
        port = click.prompt("Enter the new port", default=configs[group][old_server].get('port', 22), type=int)
        
        new_config = {
            "hostname": hostname,
            "username": username,
            "port": port
        }
        
        try:
            edit_server(configs, group, old_server, new_server, new_config)
            click.echo(f"Server '{old_server}' in group '{group}' updated successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    
    save_json_config(configs, config_file)

@cli.command()
def remove():
    """Remove a group or server from the configuration."""
    choice = click.prompt("Do you want to remove a group or a server? (group/server)", type=click.Choice(['group', 'server']))
    
    if choice == 'group':
        groups = get_groups(configs)
        group = select_with_click(groups, "Select a group to remove:")
        if not group:
            click.echo("No group selected. Aborting.")
            return
        
        try:
            remove_group(configs, group)
            click.echo(f"Group '{group}' removed successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        groups = get_groups(configs)
        group = select_with_click(groups, "Select a group:")
        if not group:
            click.echo("No group selected. Aborting.")
            return
        
        servers = get_servers_in_group(configs, group)
        server = select_with_click(servers, f"Select a server to remove:")
        if not server:
            click.echo("No server selected. Aborting.")
            return
        
        try:
            remove_server(configs, group, server)
            click.echo(f"Server '{server}' removed successfully from group '{group}'.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    
    save_json_config(configs, config_file)

@cli.command()
def edit():
    """Edit a group or server in the configuration."""
    choice = click.prompt("Do you want to edit a group or a server? (group/server)", type=click.Choice(['group', 'server']))
    
    if choice == 'group':
        groups = get_groups(configs)
        old_group = select_with_click(groups, "Select a group to edit:")
        if not old_group:
            click.echo("No group selected. Aborting.")
            return
        
        new_group = click.prompt(f"Enter the new name for group '{old_group}'")
        try:
            edit_group(configs, old_group, new_group)
            click.echo(f"Group '{old_group}' renamed to '{new_group}' successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        groups = get_groups(configs)
        group = select_with_click(groups, "Select a group:")
        if not group:
            click.echo("No group selected. Aborting.")
            return
        
        servers = get_servers_in_group(configs, group)
        old_server = select_with_click(servers, f"Select a server to edit:")
        if not old_server:
            click.echo("No server selected. Aborting.")
            return
        
        new_server = click.prompt(f"Enter the new name for server '{old_server}' (press Enter to keep the same name)", default=old_server)
        hostname = click.prompt("Enter the new hostname", default=configs[group][old_server]['hostname'])
        username = click.prompt("Enter the new username", default=configs[group][old_server]['username'])
        port = click.prompt("Enter the new port", default=configs[group][old_server].get('port', 22), type=int)
        
        new_config = {
            "hostname": hostname,
            "username": username,
            "port": port
        }
        
        try:
            edit_server(configs, group, old_server, new_server, new_config)
            click.echo(f"Server '{old_server}' in group '{group}' updated successfully.")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    
    save_json_config(configs, config_file)

if __name__ == '__main__':
    cli()
