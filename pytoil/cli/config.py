"""
CLI config command.

Author: Tom Fleet
Created: 24/02/2021
"""

import pathlib

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
    config.show()


@app.command()
def set(
    username: str = typer.Option(None, "--username", "-u", help="Set GitHub username."),
    token: str = typer.Option(
        None, "--token", "-t", help="Set Github personal access token."
    ),
    projects_dir: pathlib.Path = typer.Option(
        None,
        "--projects-dir",
        "-p",
        help="Set projects directory.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    vscode: bool = typer.Option(
        None, "--vscode", "-v", help="Set pytoil to use vscode."
    ),
) -> None:
    """
    Set a config parameter.

    Examples

    $ pytoil config set --username my_username
    """

    # Get any existing config
    # but don't validate
    config = Config.get()

    # I'm not keen on this, it feels messy
    if username:
        config.username = username
    elif token:
        config.token = token
    elif projects_dir:
        config.projects_dir = projects_dir
    elif vscode:
        config.vscode = vscode
    else:
        typer.secho("unrecognised parameter", fg=typer.colors.RED)
        raise typer.Abort()

    # Write the updated config
    config.write()

    typer.secho("Config updated", fg=typer.colors.GREEN)
    typer.secho("\nNew Config:\n", fg=typer.colors.BLUE, bold=True)
    config.show()
