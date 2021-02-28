"""
Main CLI module.

Author: Tom Fleet
Created: 24/02/2021
"""

import typer

from pytoil import __version__
from pytoil.cli import config, project, show, sync

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
