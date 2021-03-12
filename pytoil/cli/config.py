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

    vscode (bool): Whether to use vscode or not.
    """


@app.command()
def show() -> None:
    """
    Display currently set configuration.
    """

    # Get config but don't raise on UNSET
    try:
        config = Config.get()
    except FileNotFoundError:
        typer.secho("No config file yet!", fg=typer.colors.YELLOW)
        typer.echo("Run '$ pytoil init' to automatically generate one.")
    else:
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
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    vscode: str = typer.Option(
        None, "--vscode", "-v", help="Set pytoil to use vscode.", case_sensitive=False
    ),
) -> None:
    """
    Set a config parameter.

    Examples

    $ pytoil config set --username my_username

    $ pytoil config set --token my_token

    $ pytoil config set --vscode True
    """

    # Get any existing config
    # but don't validate
    try:
        config = Config.get()
    except FileNotFoundError:
        typer.secho("No config file yet!", fg=typer.colors.YELLOW)
        typer.echo("Run '$ pytoil init' to automatically generate one.")
    else:

        # I'm not keen on this, it feels messy
        if username:
            config.username = username
        elif token:
            config.token = token
        elif projects_dir:
            config.projects_dir = projects_dir
        elif vscode:  # pragma: no cover
            # If we use vscode as a boolean option it doesn't quite work right
            # also for some reason coverage doesn't recognise this as being called
            # during tests but it is in tests/cli/test_config.py so we exclude it
            if vscode.lower() == "true":
                config.vscode = True
            elif vscode.lower() == "false":
                config.vscode = False
            else:
                raise typer.BadParameter("vscode must be a boolean value.")

        # Write the updated config
        config.write()

        typer.secho("\nConfig updated successfully!", fg=typer.colors.GREEN)
        typer.secho("\nNew Config:\n", fg=typer.colors.BLUE, bold=True)
        config.show()
