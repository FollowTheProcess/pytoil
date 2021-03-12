"""
Main CLI module.

Author: Tom Fleet
Created: 24/02/2021
"""

import pathlib

import typer

from pytoil import __version__
from pytoil.cli import config, project, show, sync
from pytoil.config import CONFIG_PATH, Config
from pytoil.exceptions import InvalidConfigError

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

    typer.secho("Checking for config file...\n", fg=typer.colors.BLUE, bold=True)

    # Make config file
    if not CONFIG_PATH.exists():
        typer.secho("No config file found!\n", fg=typer.colors.YELLOW)
        typer.echo("Creating fresh config file...\n")
        CONFIG_PATH.touch()
        default_config = Config()
        default_config.write()

        username: str = typer.prompt("GitHub username")
        token: str = typer.prompt("GitHub personal access token")
        projects_dir: str = typer.prompt("Absolute path to your projects directory")
        vscode: str = typer.prompt("Use VSCode to open projects with? [True|False]")

        projects_dir_path = pathlib.Path(projects_dir)

        if vscode.lower() == "true":
            vscode_bool = True
        elif vscode.lower() == "false":
            vscode_bool = False
        else:
            raise typer.BadParameter("VSCode must be a boolean value")

        user_config = Config(
            username=username,
            token=token,
            projects_dir=projects_dir_path,
            vscode=vscode_bool,
        )
        user_config.write()

        typer.secho("Config written, you're good to go!", fg=typer.colors.GREEN)
    else:
        try:
            config = Config.get()
            config.validate()
        except InvalidConfigError:
            typer.secho(
                "Something's wrong in the config file, please check it.\n",
                fg=typer.colors.RED,
            )
            typer.echo("If in doubt, simply delete it and run '$ pytoil init' again :)")
            raise typer.Abort()
        else:
            typer.secho("You're all set!", fg=typer.colors.GREEN)
