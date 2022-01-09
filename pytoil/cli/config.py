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

    The config command group allows you to get, set, and show pytoil's configuration.
    Getting and showing obviously do not edit the config file ($HOME/.pytoil.yml).

    Setting a key value pair using the 'config set' subcommand will cause the config
    file to be updated and overwritten. You will be prompted to confirm this however.
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
@click.argument("key", nargs=1)
@click.argument("val", nargs=-1, required=True)
@click.option(
    "--force", "-f", is_flag=True, help="Force overwrite without confirmation."
)
@click.pass_obj
async def set(config: Config, key: str, val: tuple[str, ...], force: bool) -> None:
    """
    Set a config key, value pair.

    The set command allows you to set a config value.

    On confirmation, the config file ($HOME/.pytoil.yml) will be
    overwritten with the new data.

    The "--force/-f" flag can be used to force overwrite without confirmation.

    Examples:

    $ pytoil config set projects_dir "/Users/me/projects"

    $ pytoil config set vscode False --force
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    if key != "common_packages" and len(val) > 1:
        msg.fail(
            "Error: All config keys except 'common_packages' take a maximum of 1 value",
            exits=1,
        )

    conf = config.to_dict()

    if key == "common_packages":
        new_val = val
    else:
        new_val = val[0]  # type: ignore

    new_setting = {key: new_val}

    conf.update(new_setting)  # type: ignore

    new_config = Config.from_dict(conf)

    if not force:
        click.confirm(
            f"This will set {key!r} to {new_val!r}. Are you sure?", abort=True
        )

    try:
        await new_config.write()
    except Exception:
        # This should only happen if something really weird happens
        # like corrupted file etc.
        msg.fail(
            "Uh oh! Something went wrong, check your config file for errors.", exits=1
        )
    else:
        msg.good("Config successfully updated", spaced=True)
        msg.text(f"{key!r} is now {config[key]}")  # type: ignore


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
