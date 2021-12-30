"""
The async-pytoil config command group.


Author: Tom Fleet
Created: 21/12/2021
"""

import time
from typing import Tuple

import asyncclick as click
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table, box
from wasabi import msg

from pytoil.config import Config, defaults

# If the file doesn't exist, let's make a default one nicely
# This will check if the config file exists
# every time the `pytoil` command is run so should
# eliminate those nasty FileNotFoundErrors
if not defaults.CONFIG_FILE.exists():
    msg.warn("No pytoil config file detected!")

    with msg.loading("Making you a starter file..."):
        Config.helper().write()
        time.sleep(1)

    msg.good(f"Your file is now available at {defaults.CONFIG_FILE}", spaced=True)
    msg.text("Try running pytoil again!", spaced=True, exits=0)


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
async def show() -> None:
    """
    Show pytoil's config.

    The show command allows you to easily see pytoil's current config.

    The values are taken directly from the config file where specified or
    the defaults otherwise.

    Examples:

    $ pytoil config show
    """
    config = await Config.from_file()

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
async def get(key: str) -> None:
    """
    Get the currently set value for a config key.

    The get command will only allow valid pytoil config keys.

    Examples:

    $ pytoil config get vscode
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    config = await Config.from_file()
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
async def set(key: str, val: Tuple[str, ...], force: bool) -> None:
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

    conf = await Config.from_file()
    config = conf.to_dict()

    if key == "common_packages":
        new_val = val
    else:
        new_val = val[0]  # type: ignore

    new_setting = {key: new_val}

    config.update(new_setting)  # type: ignore

    new_config = Config.from_dict(config)

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
