import click
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the SSH config file path from environment variable
config_file = os.getenv('SSH_CONFIG_FILE_PATH')

if not config_file:
    raise ValueError("The SSH_CONFIG_FILE_PATH environment variable is not set.")

# Define a function to parse the SSH config file
def parse_ssh_config(file_path):
    """Parse the SSH config file and return a dictionary of configurations."""
    config_dict = {}
    with open(file_path, 'r') as file:
        current_host = None
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('Host '):
                current_host = line.split(' ')[1]
                config_dict[current_host] = {}
            elif current_host and ' ' in line:
                key, value = line.split(' ', 1)
                config_dict[current_host][key] = value
    return config_dict

# Define a Click command to display and select SSH configurations
@click.command()
def select_ssh_config():
    """A CLI to select and display SSH configuration entries."""
    # Parse the SSH config file
    configs = parse_ssh_config(config_file)

    if not configs:
        click.echo("No configurations found.")
        return

    # Display the configuration options
    click.echo("Select a configuration:")
    for idx, host in enumerate(configs.keys(), start=1):
        click.echo(f"{idx}. {host}")

    try:
        choice = int(click.prompt("Enter the number of your choice"))
        if choice < 1 or choice > len(configs):
            click.echo("Invalid choice.")
            return
    except ValueError:
        click.echo("Please enter a valid number.")
        return

    selected_host = list(configs.keys())[choice - 1]
    click.echo(f"\nSelected Configuration for {selected_host}:")
    for key, value in configs[selected_host].items():
        click.echo(f"{key}: {value}")

if __name__ == '__main__':
    select_ssh_config()
