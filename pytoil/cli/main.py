"""
Main CLI module.

Author: Tom Fleet
Created: 24/02/2021
"""

import typer

from pytoil import __version__
from pytoil.cli import config, project, show, sync
from pytoil.config import CONFIG_PATH, Config

# Add all the subcommands
app = typer.Typer(name="pytoil", no_args_is_help=True)
app.add_typer(config.app, name="config")
app.add_typer(project.app, name="project")
app.add_typer(sync.app, name="sync")
app.add_typer(show.app, name="show")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


# Callback for documentation only
@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Display pytoil version.",
        callback=version_callback,
        is_eager=True,
        show_default=False,
    )
) -> None:
    """
    Helpful CLI to automate the development workflow.

    - Create and manage your local and remote projects

    - Build projects from cookiecutter templates.

    - Easily create/manage virtual environments.

    - Minimal configuration required.
    """


@app.command()
def init() -> None:
    """
    Initialise pytoil.

    Will guide user through the config setup
    interactively.
    """

    # Make config file
    if not CONFIG_PATH.exists():
        CONFIG_PATH.touch()
        default_config = Config()
        default_config.write()

        username: str = typer.prompt("GitHub username")
        token: str = typer.prompt("GitHub personal access token")
        projects_dir: str = typer.prompt("Absolute path to your projects directory")

        user_config = Config(username=username, token=token, projects_dir=projects_dir)
        user_config.write()

        typer.secho("Config written, you're good to go!", fg=typer.colors.GREEN)
    else:
        typer.secho("You're all set!", fg=typer.colors.GREEN)
