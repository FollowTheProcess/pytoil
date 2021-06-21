"""
The `pytoil config` subcommand group.

Author: Tom Fleet
Created: 18/06/2021
"""

import time

import typer
from wasabi import msg

from pytoil.config import Config, defaults

app = typer.Typer(name="config", no_args_is_help=True)

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
    """
    config = Config.from_file()

    typer.secho("\nPytoil Config:\n", fg=typer.colors.CYAN, bold=True)

    for key, val in config.to_dict().items():
        typer.echo(f"{key}: {val!r}")


@app.command()
def get(
    key: str = typer.Argument(..., help="Config key to fetch the value for.")
) -> None:
    """
    Get the currently set value for a config key.

    The get command only allows valid pytoil config keys.
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    config = Config.from_file().to_dict()
    typer.secho(f"\n{key}: {config.get(key)!r}\n")


@app.command()
def set(
    key: str = typer.Argument(..., help="Config key to set the value for."),
    val: str = typer.Argument(..., help="Value to set for <key>."),
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
    """
    if key not in defaults.CONFIG_KEYS:
        msg.warn(f"{key!r} is not a valid pytoil config key.", exits=1)

    # Can't set a list via the command line
    if key == "common_packages":
        msg.warn("You can't set common_packages at the command line", exits=1)

    config = Config.from_file().to_dict()

    new_setting = {key: val}

    config.update(new_setting)  # type: ignore

    new_config = Config.from_dict(config)

    if not force:
        typer.confirm(f"This will set {key!r} to {val}. Are you sure?", abort=True)

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


@app.command(name="help")
def help_() -> None:
    """
    Print a list and description of pytoil config keys.
    """
    msg.divider("The '.pytoil.yml' config file")
    print(defaults.CONFIG_SCHEMA)
