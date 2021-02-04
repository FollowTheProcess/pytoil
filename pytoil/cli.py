"""
Main CLI module.

Author: Tom Fleet
Created: 04/02/2021
"""

import typer

from . import __version__

app = typer.Typer(name="pytoil", no_args_is_help=True)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


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
) -> None:  # pragma: no cover
    """
    Helpful CLI to automate the development workflow!
    """
    if version:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


@app.command(help="Create a new development project.")
def new(
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookiecutter: bool = typer.Option(
        False,
        "--cookiecutter",
        "-c",
        help="Create a new project from a cookiecutter template.",
    ),
) -> None:
    if cookiecutter:
        typer.echo(f"Creating project: {project} with cookiecutter.")
    else:
        typer.echo(f"Creating project: {project}")


@app.command(help="Resume a development project, either locally or from GitHub.")
def resume(
    project: str = typer.Argument(..., help="Name of the project to resume.")
) -> None:
    typer.echo(f"Resuming project: {project}")
