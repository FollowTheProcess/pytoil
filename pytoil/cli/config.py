"""
CLI config command.

Author: Tom Fleet
Created: 24/02/2021
"""

from typing import Tuple

import typer

from pytoil.config import Config

app = typer.Typer(no_args_is_help=True)


# Callback for documentation only
@app.callback()
def config() -> None:
    """
    Interact with pytoil's configuration.

    pytoil's config file is ~/.pytoil.yml.

    Schema:

    username (str): Users GitHub username.

    token (str): Users GitHub personal access token.

    projects_dir (str): Absolute path to where you keep your projects.
    """


@app.command()
def show() -> None:
    """
    Display currently set configuration.
    """

    # Get config but don't raise on UNSET
    config = Config.get()

    typer.secho("\nCurrent pytoil config:", fg=typer.colors.BLUE, bold=True)
    typer.echo("")
    config_dict = config.to_dict()

    for key, val in config_dict.items():
        typer.echo(f"{key}: {val}")


@app.command()
def set(
    item: Tuple[str, str] = typer.Argument(..., help="Space-separated key, value pair.")
) -> None:
    """
    Set a valid config key, value pair.

    If the change is valid, it is immediately written to the config file.

    Examples:

    $ pytoil config set token mynewtoken

    $ pytoil config set username myusername

    $ pytoil config set projects_dir /Users/me/projects
    """

    # Get config but don't raise on UNSET
    config = Config.get()

    old_config_dict = config.to_dict()
    key, val = item

    if key not in old_config_dict.keys():
        typer.secho(
            f"Key: {key!r} is not a valid pytoil config key.", fg=typer.colors.RED
        )
        raise typer.Abort()

    new_config_dict = old_config_dict.copy()
    new_config_dict.update({key: val})

    new_config = Config(**new_config_dict)
    new_config.write()

    typer.secho(
        f"Configuration updated: {key!r} is now {val!r}.", fg=typer.colors.GREEN
    )
