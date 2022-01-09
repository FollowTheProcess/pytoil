"""
The async-pytoil config command group.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table, box
from wasabi import msg

from pytoil.config import Config, defaults


@click.group()
async def config() -> None:
    """
    Interact with pytoil's configuration.

    The config command group allows you to get, show and explain pytoil's configuration.
    """


@config.command()
@click.pass_obj
async def show(config: Config) -> None:
    """
    Show pytoil's config.

    The show command allows you to easily see pytoil's current config.

    The values are taken directly from the config file where specified or
    the defaults otherwise.

    Examples:

    $ pytoil config show
    """
    click.secho("\nPytoil Config:\n", fg="cyan", bold=True)

    table = Table(box=box.SIMPLE)
    table.add_column("Key", style="cyan", justify="right")
    table.add_column("Value", justify="left")

    for key, val in config.to_dict().items():
        table.add_row(f"{key}:", str(val))

    console = Console()
    console.print(table)


@config.command()
@click.argument("key", nargs=1)
@click.pass_obj
async def get(config: Config, key: str) -> None:
    """
    Get the currently set value for a config key.

    The get command will only allow valid pytoil config keys.

    Examples:

    $ pytoil config get vscode
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    config_dict = config.to_dict()
    # Make the key a nice colour
    config_start = click.style(f"{key}: ", fg="cyan")
    config_msg = config_start + f"{config_dict.get(key)!r}"
    click.secho(config_msg)


@config.command()
async def explain() -> None:
    """
    Print a list and description of pytoil config values.

    Examples:

    $ pytoil config explain
    """
    console = Console()
    markdown = Markdown(defaults.CONFIG_SCHEMA, justify="center")
    console.print(markdown)
