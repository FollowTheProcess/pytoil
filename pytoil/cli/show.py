"""
CLI show command.

Author: Tom Fleet
Created: 28/02/2021
"""

from typing import List, Set

import typer

from pytoil.api import API
from pytoil.config import Config

app = typer.Typer(no_args_is_help=True)


# Callback for documentation only
@app.callback()
def show() -> None:
    """
    View your local/remote projects.
    """


@app.command()
def local() -> None:
    """
    Show all your local projects.
    """

    config = Config.get()
    config.raise_if_unset()

    local_projects: List[str] = sorted(
        [
            f.name
            for f in config.projects_dir.iterdir()
            if f.is_dir() and not f.name.startswith(".")
        ],
        key=str.casefold,  # casefold means sorting works independent of case
    )

    typer.secho("\nLocal projects:\n", fg=typer.colors.BLUE, bold=True)
    for project in local_projects:
        typer.echo(f"- {project}")


@app.command()
def remote() -> None:
    """
    Show all your remote projects.
    """

    config = Config.get()
    config.raise_if_unset()

    api = API()

    remote_projects: List[str] = sorted(api.get_repo_names(), key=str.casefold)

    typer.secho("\nRemote projects:\n", fg=typer.colors.BLUE, bold=True)
    for project in remote_projects:
        typer.echo(f"- {project}")


# Can't call it all, keyword!
@app.command(name="all")
def all_() -> None:
    """
    Show both local and remote projects.
    """

    config = Config.get()
    config.raise_if_unset()

    api = API()

    local_projects: List[str] = sorted(
        [
            f.name
            for f in config.projects_dir.iterdir()
            if f.is_dir() and not f.name.startswith(".")
        ],
        key=str.casefold,  # casefold means sorting works independent of case
    )

    remote_projects: List[str] = sorted(api.get_repo_names(), key=str.casefold)

    # Show locals first
    typer.secho("\nLocal projects:\n", fg=typer.colors.BLUE, bold=True)
    for project in local_projects:
        typer.echo(f"- {project}")

    # Now remotes
    typer.secho("\nRemote projects:\n", fg=typer.colors.BLUE, bold=True)
    for project in remote_projects:
        typer.echo(f"- {project}")


@app.command()
def diff() -> None:
    """
    Show the difference in local/remote projects.

    i.e. those projects you have remotely but not locally.
    """

    # Everything below requires a valid config
    config = Config.get()
    config.raise_if_unset()

    api = API()

    local_projects: Set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    remote_projects: Set[str] = set(api.get_repo_names())

    difference: Set[str] = remote_projects.difference(local_projects)

    # Internal correctness
    assert len(difference) >= 0

    if len(difference) > 0:

        typer.secho(
            "\nRemote projects that are not local:\n", fg=typer.colors.BLUE, bold=True
        )
        for project in sorted(list(difference), key=str.casefold):
            typer.echo(f"- {project}")
    else:

        typer.secho(
            "You already have all your remote projects locally. Nothing to show!",
            fg=typer.colors.GREEN,
        )
