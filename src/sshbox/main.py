import os
import subprocess

import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .json_config import (
    add_group,
    add_host,
    create_sample_config,
    edit_group,
    edit_host,
    get_app_settings,
    get_groups,
    get_hosts_in_group,
    load_json_config,
    remove_group,
    remove_host,
    save_json_config,
)

console = Console()


def select_option(options, prompt_text, is_group=False):
    app_settings = get_app_settings(configs)
    table_colors = app_settings.get("table_colors", {})

    table = Table(
        title=prompt_text,
        title_style="bold",
        title_justify="center",
        box=box.ROUNDED,
        show_header=False,
        show_edge=True,
        min_width=len(prompt_text) + 4,  # So that word wrapping doesn't occur
        # when selecting between Host/Group using `sshbox edit/remove`
    )

    # Add two columns: one for the index, one for the option
    # Default to cyan for the selection numbers
    table.add_column(
        "Index",
        style=table_colors.get("selection_number", "cyan"),
        justify="center",
    )
    table.add_column("Option", justify="left")

    for index, option in enumerate(options, start=1):
        if option in ["Host", "Group"]:
            option_style = table_colors.get(
                "hostname" if option == "Host" else "group", "yellow"
            )
            option_text = Text(option, style=option_style)
        else:
            option_style = table_colors.get(
                "group" if is_group else "hostname", "green"
            )
            option_text = Text(option, style=option_style)
        table.add_row(f"{index}", option_text)

    console.print(table)

    while True:
        char = click.getchar()
        if char.isdigit():
            user_input = int(char)
            if 0 < user_input <= len(options):
                console.print()  # Move to a new line after selection
                return options[user_input - 1]
        console.print("\nInvalid choice. Please try again.")


# Get the JSON config file path from environment variable or use a default
config_file = os.getenv(
    "SSHBOX_CONFIG_FILE", os.path.expanduser("~/.ssh/sshbox.json")
)

try:
    # Load the JSON configuration
    configs = load_json_config(config_file)
except FileNotFoundError:
    # If the file doesn't exist, create it with sample configuration
    configs = create_sample_config()
    save_json_config(configs, config_file)
    click.echo(
        click.style(
            f"Created sample configuration file: {config_file}", fg="green"
        )
    )
except ValueError as e:
    if "Configuration file is empty" in str(e):
        # If the file is empty, create sample configuration
        configs = create_sample_config()
        save_json_config(configs, config_file)
        click.echo(
            click.style(
                f"Created sample configuration in empty file: {config_file}",
                fg="green",
            )
        )
    else:
        click.echo(
            click.style(f"Error loading configuration: {str(e)}", fg="red")
        )
        exit(1)


# If only `sshbox` is run (no arguments) treat it as an attempt to connect to a host
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CLI for managing SSH connections using JSON configuration."""
    if ctx.invoked_subcommand is None:
        connect()


def connect():
    """Connect to a selected host using SSH."""
    groups = get_groups(configs)
    group = select_option(groups, "Select Group", is_group=True)

    hosts = get_hosts_in_group(configs, group)
    host = select_option(hosts, "Select Host", is_group=False)

    host_config = configs[group][host]

    ssh_command = [
        "ssh",
        "-p",
        str(host_config["port"]),
        f"{host_config['username']}@{host_config['hostname']}",
    ]

    click.echo(f"Attempting connection to {host}...")
    subprocess.run(ssh_command)


@cli.command()
def add():
    """Add a new group or host to the configuration."""
    choice = select_option(
        ["Host", "Group"], "Add New Host Or Group?", is_group=True
    )

    if choice == "Group":
        group = click.prompt("Enter New Group")
        try:
            add_group(configs, group)
            click.echo(click.style(f"{group} added successfully", fg="green"))

            if click.confirm(f"Add Host To {group}?"):
                add_host_to_group(group)
        except ValueError as e:
            click.echo(click.style(f"Error: {str(e)}", fg="red"))
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
            "port": port,
        }

        try:
            add_host(configs, group, host, host_config)
            save_json_config(configs, config_file)
            click.echo(
                click.style(
                    f"{host} added successfully to {group}", fg="green"
                )
            )
        except ValueError as e:
            click.echo(click.style(f"Error: {str(e)}", fg="red"))
            continue

        if not click.confirm(f"Add Another Host To {group}?"):
            break


@cli.command()
def remove():
    """Remove a group or host from the configuration."""
    while True:
        choice = select_option(
            ["Host", "Group"], "Remove Host Or Group?", is_group=True
        )

        if choice == "Group":
            groups = get_groups(configs)
            group = select_option(
                groups, "Select Group For Removal", is_group=True
            )

            try:
                remove_group(configs, group)
                click.echo(
                    click.style(
                        f"Group: {group} removed successfully", fg="green"
                    )
                )
            except ValueError as e:
                click.echo(click.style(f"Error: {str(e)}", fg="red"))
        else:
            groups = get_groups(configs)
            group = select_option(groups, "Select Group")

            hosts = get_hosts_in_group(configs, group)
            host = select_option(hosts, "Select Host For Removal")

            try:
                remove_host(configs, group, host)
                click.echo(
                    click.style(
                        f"{host} removed successfully from {group}", fg="green"
                    )
                )
            except ValueError as e:
                click.echo(click.style(f"Error: {str(e)}", fg="red"))

        save_json_config(configs, config_file)

        if not click.confirm(f"Remove Another {choice}?"):
            break


@cli.command()
def edit():
    """Edit a group or host in the configuration."""
    while True:
        choice = select_option(
            ["Host", "Group"], "Edit Host Or Group?", is_group=True
        )

        if choice == "Group":
            groups = get_groups(configs)
            old_group = select_option(
                groups, "Select Group To Edit", is_group=True
            )

            new_group = click.prompt(f"Enter New Name For Group: {old_group}")
            try:
                edit_group(configs, old_group, new_group)
                click.echo(
                    click.style(
                        f"{old_group} successfully renamed to {new_group}",
                        fg="green",
                    )
                )
            except ValueError as e:
                click.echo(click.style(f"Error: {str(e)}", fg="red"))
        else:
            groups = get_groups(configs)
            group = select_option(groups, "Select Group To Edit")

            hosts = get_hosts_in_group(configs, group)
            old_host = select_option(hosts, "Select Host To Edit")

            new_host = click.prompt(
                f"Enter New Name For Host: {old_host}",
                default=old_host,
            )
            hostname = click.prompt(
                "Enter New Hostname",
                default=configs[group][old_host]["hostname"],
            )
            username = click.prompt(
                "Enter New Username",
                default=configs[group][old_host]["username"],
            )
            port = click.prompt(
                "Enter New Port",
                default=configs[group][old_host].get("port", 22),
                type=int,
            )

            new_config = {
                "hostname": hostname,
                "username": username,
                "port": port,
            }

            try:
                edit_host(configs, group, old_host, new_host, new_config)
                click.echo(
                    click.style(
                        f"{old_host} in {group} successfully updated",
                        fg="green",
                    )
                )
            except ValueError as e:
                click.echo(click.style(f"Error: {str(e)}", fg="red"))

        save_json_config(configs, config_file)

        if not click.confirm("Edit Another?"):
            break


if __name__ == "__main__":
    cli()
