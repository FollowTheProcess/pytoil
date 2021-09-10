"""
The `pytoil config` subcommand group.

Author: Tom Fleet
Created: 18/06/2021
"""

import time
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from wasabi import msg

from pytoil.config import Config, defaults

app = typer.Typer(name="config")

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


# Callback for documentation only
@app.callback()
def config() -> None:
    """
    Interact with pytoil's configuration.

    The config command group allows you to get, set, and show pytoil's configuration.
    Getting and showing obviously do not edit the config file ($HOME/.pytoil.yml).

    Setting a key value pair using the 'config set' subcommand will cause the config
    file to be updated and overwritten. You will be prompted to confirm this however.

    Currently the only config key you cannot set on the command line is
    'common_packages'. If you want to change this, you'll have to do so in the
    config file itself.
    """


@app.command()
def show() -> None:
    """
    Show pytoil's config.

    The show command allows you to easily see pytoil's current config.

    The values are taken directly from the config file where specified or
    the defaults otherwise.

    Examples:

    $ pytoil config show
    """
    config = Config.from_file()

    typer.secho("\nPytoil Config:\n", fg=typer.colors.CYAN, bold=True)

    table = Table(box=box.SIMPLE)
    table.add_column("Key", style="cyan", justify="right")
    table.add_column("Value", justify="left")

    for key, val in config.to_dict().items():
        table.add_row(f"{key}:", str(val))

    console = Console()
    console.print(table)


@app.command()
def get(
    key: str = typer.Argument(..., help="Config key to fetch the value for.")
) -> None:
    """
    Get the currently set value for a config key.

    The get command only allows valid pytoil config keys.

    Examples:

    $ pytoil config get vscode
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    config = Config.from_file().to_dict()
    # Make the key a nice colour
    config_start = typer.style(f"\n{key}: ", fg=typer.colors.CYAN)
    config_msg = config_start + f"{config.get(key)!r}\n"
    typer.secho(config_msg)


@app.command(context_settings={"allow_extra_args": True})
def set(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Config key to set the value for."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force config overwrite without confirmation.",
        show_default=False,
    ),
) -> None:
    """
    Set a config key, value pair.

    The set command allows you to set a config value.

    On confirmation, the config file ($HOME/.pytoil.yml) will be
    overwritten with the new data.

    The '--force/-f' flag can be used to force overwrite without confirmation.

    Examples:

    $ pytoil config set projects_dir "/Users/me/projects"

    $ pytoil config set vscode False --force
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    # This is how we handle setting common_packages which could be
    # any length list
    # Set max allowed args to 1 by default, but could also be None
    max_allowed_args: Optional[int] = 1

    # If user wants to set common packages, we unlock the limit for max
    # allowed args, allowing them to pass whatever they like
    if key == "common_packages":
        max_allowed_args = None

    config = Config.from_file().to_dict()

    # If the max allowed args limit is in force (not None) and the
    # length of the list of args is greater than the limit, we fail
    # This means that every other config key will behave as before
    if max_allowed_args and len(ctx.args) > max_allowed_args:
        msg.fail(
            f"Error: Expected {max_allowed_args} argument, got {ctx.args}",
            spaced=True,
            exits=1,
        )

    # Now we're good to go, we check if max_allowed_args limit is in force
    # and pop it off the ctx.args list if so because we know there will only
    # ever be 1
    if isinstance(max_allowed_args, int):
        arg = ctx.args.pop()
    else:
        # Here we know the max_allowed_args limit has been dropped so
        # we simply return the list of arguments, which is exactly
        # how we want common_packages to be encoded, happy days :)
        arg = ctx.args

    new_setting = {key: arg}

    config.update(new_setting)  # type: ignore

    new_config = Config.from_dict(config)

    if not force:
        typer.confirm(f"This will set {key!r} to {arg}. Are you sure?", abort=True)

    try:
        new_config.write()
    except Exception:
        # This should only happen if something really weird happens
        # like corrupted config file etc.
        msg.fail(
            "Uh oh! Something went wrong! Check your config file for errors.",
            spaced=True,
            exits=1,
        )
    else:
        msg.good("Config successfully updated", spaced=True)
        msg.text(f"{key!r} is now {config[key]}")  # type: ignore


@app.command()
def explain() -> None:
    """
    Print a list and description of pytoil config keys.

    Examples:

    $ pytoil config explain
    """
    console = Console()
    markdown = Markdown(defaults.CONFIG_SCHEMA, justify="center")
    console.print(markdown)
