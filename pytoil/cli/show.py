"""
CLI show command.

Author: Tom Fleet
Created: 28/02/2021
"""

from typing import List, Set

import typer

from pytoil.api import API
from pytoil.cli.utils import (
    get_local_project_list,
    get_local_project_set,
    get_remote_project_list,
    get_remote_project_set,
)
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
    config.validate()

    local_projects: List[str] = get_local_project_list(config.projects_dir)

    n_locals: int = len(local_projects)

    assert n_locals >= 0

    if n_locals > 0:

        typer.secho("\nLocal projects:\n", fg=typer.colors.BLUE, bold=True)
        for project in local_projects:
            typer.echo(f"- {project}")
    else:
        typer.secho("You don't have any local projects yet!", fg=typer.colors.YELLOW)


@app.command()
def remote() -> None:
    """
    Show all your remote projects.
    """

    config = Config.get()
    config.validate()

    api = API()

    remote_projects: List[str] = get_remote_project_list(api)

    n_remotes: int = len(remote_projects)

    assert n_remotes >= 0

    if n_remotes > 0:

        typer.secho("\nRemote projects:\n", fg=typer.colors.BLUE, bold=True)
        for project in remote_projects:
            typer.echo(f"- {project}")
    else:
        typer.secho("You don't have any remote projects yet!", fg=typer.colors.YELLOW)


# Can't call it all, keyword!
@app.command(name="all")
def all_() -> None:
    """
    Show both local and remote projects.
    """

    config = Config.get()
    config.validate()

    api = API()

    local_projects: List[str] = get_local_project_list(config.projects_dir)

    remote_projects: List[str] = get_remote_project_list(api)

    n_locals: int = len(local_projects)
    n_remotes: int = len(remote_projects)

    assert n_locals >= 0
    assert n_remotes >= 0

    # Show locals first
    if n_locals > 0:
        typer.secho("\nLocal projects:\n", fg=typer.colors.BLUE, bold=True)
        for project in local_projects:
            typer.echo(f"- {project}")
    else:
        typer.secho("You don't have any local projects yet!", fg=typer.colors.YELLOW)

    # Now remotes
    if n_remotes > 0:
        typer.secho("\nRemote projects:\n", fg=typer.colors.BLUE, bold=True)
        for project in remote_projects:
            typer.echo(f"- {project}")
    else:
        typer.secho("You don't have any remote projects yet!", fg=typer.colors.YELLOW)


@app.command()
def diff() -> None:
    """
    Show the difference in local/remote projects.

    i.e. those projects you have remotely but not locally.
    """

    # Everything below requires a valid config
    config = Config.get()
    config.validate()

    api = API()

    local_projects: Set[str] = get_local_project_set(config.projects_dir)

    remote_projects: Set[str] = get_remote_project_set(api)
    difference: Set[str] = remote_projects.difference(local_projects)

    n_diff: int = len(difference)

    # Internal correctness
    assert n_diff >= 0

    if n_diff > 0:

        typer.secho(
            "\nRemote projects that are not local:\n", fg=typer.colors.BLUE, bold=True
        )
        for project in sorted(list(difference), key=str.casefold):
            typer.echo(f"- {project}")
    else:

        typer.secho(
            "Your local and remote projects are all synced up. Nothing to show!",
            fg=typer.colors.GREEN,
        )
