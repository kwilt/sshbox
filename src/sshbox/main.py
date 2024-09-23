import os
import click
import subprocess
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich import box

from .json_config import (
    load_json_config, save_json_config, get_groups, get_hosts_in_group,
    create_sample_config, add_group, add_host, remove_group, remove_host,
    edit_group, edit_host
)

console = Console()

def select_option(options, prompt_text):
    # Get the terminal width
    terminal_width = os.get_terminal_size().columns
    
    # Set the table width to 60% of the terminal width
    table_width = int(terminal_width * 0.6)
    
    table = Table(
        title=prompt_text,
        title_style="bold",
        title_justify="center",
        width=table_width,
        expand=False,
        box=box.ROUNDED,
        show_header=False,
        show_edge=False,
    )
    
    # Determine if we're selecting a Host or a Group
    value_column_name = "Group" if "Select Group" in prompt_text else "Host"
    table.add_column(value_column_name, style="magenta", justify="center", width=table_width - 4)

    for index, option in enumerate(options, start=1):
        table.add_row(f"[cyan]{index}.[/cyan] {option}")

    # Wrap the table in an Align object to center it
    centered_table = Align.center(table)
    console.print(centered_table)

    while True:
        char = click.getchar()
        if char.isdigit():
            user_input = int(char)
            if 0 < user_input <= len(options):
                console.print()  # Move to a new line after selection
                return options[user_input - 1]
        console.print("\nInvalid choice. Please try again.")

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

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CLI for managing SSH connections using JSON configuration."""
    if ctx.invoked_subcommand is None:
        connect()

def connect():
    """Connect to a selected host using SSH."""
    groups = get_groups(configs)
    group = select_option(groups, "Select Group")

    hosts = get_hosts_in_group(configs, group)
    host = select_option(hosts, "Select Host")

    host_config = configs[group][host]

    ssh_command = [
        "ssh",
        "-p", str(host_config['port']),
        f"{host_config['username']}@{host_config['hostname']}"
    ]

    click.echo(f"Connecting to {host}...")
    subprocess.run(ssh_command)

@cli.command()
def add():
    """Add a new group or host to the configuration."""
    choice = select_option(['Host', 'Group'], "Add New Host Or Group?")

    if choice == 'Group':
        group = click.prompt("Enter New Group")
        try:
            add_group(configs, group)
            click.echo(f"'{group}' added successfully.")

            if click.confirm(f"Add Host To {group}?"):
                add_host_to_group(group)
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
    else:
        add_host_to_group()

    save_json_config(configs, config_file)

def add_host_to_group(group=None):
    """Add a new host to a group."""
    if group is None:
        groups = get_groups(configs)
        group = select_option(groups, "Select Group For New Host")

    while True:
        host = click.prompt("Enter Alias For Connection")
        hostname = click.prompt("Enter Hostname")
        username = click.prompt("Enter Username")
        port = click.prompt("Enter Port", default=22, type=int)

        host_config = {
            "hostname": hostname,
            "username": username,
            "port": port
        }

        try:
            add_host(configs, group, host, host_config)
            save_json_config(configs, config_file)
            click.echo(f"'{host}' added successfully to '{group}'")
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
            continue

        if not click.confirm(f"Add Another Host To {group}?"):
            break

@cli.command()
def remove():
    """Remove a group or host from the configuration."""
    while True:
        choice = select_option(['Host', 'Group'], "Remove Host Or Group?")

        if choice == 'Group':
            groups = get_groups(configs)
            group = select_option(groups, "Select Group For Removal")

            try:
                remove_group(configs, group)
                click.echo(f"Group '{group}' removed successfully")
            except ValueError as e:
                click.echo(f"Error: {str(e)}")
        else:
            groups = get_groups(configs)
            group = select_option(groups, "Select Group")

            hosts = get_hosts_in_group(configs, group)
            host = select_option(hosts, f"Select Host For Removal")

            try:
                remove_host(configs, group, host)
                click.echo(f"'{host}' removed successfully from '{group}'")
            except ValueError as e:
                click.echo(f"Error: {str(e)}")

        save_json_config(configs, config_file)

        if not click.confirm(f"Remove Another {choice}?"):
            break

@cli.command()
def edit():
    """Edit a group or host in the configuration."""
    while True:
        choice = select_option(['Host', 'Group'], "Edit Host Or Group?")

        if choice == 'Group':
            groups = get_groups(configs)
            old_group = select_option(groups, "Select Group To Edit")

            new_group = click.prompt(f"Enter New Name For Group: '{old_group}'")
            try:
                edit_group(configs, old_group, new_group)
                click.echo(f"'{old_group}' successfully renamed to '{new_group}'")
            except ValueError as e:
                click.echo(f"Error: {str(e)}")
        else:
            groups = get_groups(configs)
            group = select_option(groups, "Select Group To Edit")

            hosts = get_hosts_in_group(configs, group)
            old_host = select_option(hosts, f"Select Host To Edit")

            new_host = click.prompt(f"Enter New Name For Host: '{old_host}' (press Enter to keep the same name)", default=old_host)
            hostname = click.prompt("Enter New Hostname", default=configs[group][old_host]['hostname'])
            username = click.prompt("Enter New Username", default=configs[group][old_host]['username'])
            port = click.prompt("Enter New Port", default=configs[group][old_host].get('port', 22), type=int)

            new_config = {
                "hostname": hostname,
                "username": username,
                "port": port
            }

            try:
                edit_host(configs, group, old_host, new_host, new_config)
                click.echo(f"'{old_host}' in '{group}' successfully updated")
            except ValueError as e:
                click.echo(f"Error: {str(e)}")

        save_json_config(configs, config_file)

        if not click.confirm(f"Edit Another?"):
            break

if __name__ == '__main__':
    cli()
