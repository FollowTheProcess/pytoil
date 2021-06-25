"""
The `pytoil show` subcommand group.

Author: Tom Fleet
Created: 18/06/2021
"""


import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config

app = typer.Typer(name="show")


# Callback for documentation only
@app.callback()
def show() -> None:
    """
    View your local/remote projects.

    The show command provides an easy way of listing of the projects you have locally
    in your configured development directory and/or of those you have on GitHub
    (known in pytoil-land as 'remote' projects).

    Local projects will be the names of subdirectories in your configured projects
    directory.

    The remote projects listed here will be those owned by you on GitHub.
    """


@app.command()
def local() -> None:
    """
    Show your local projects.

    Show the projects you have locally in your configured
    projects directory.

    Examples:

    $ pytoil show local
    """
    config = Config.from_file()
    local_projects = utils.get_local_projects(path=config.projects_dir)

    if not local_projects:
        msg.warn("You don't have any local projects yet!", exits=0)

    typer.secho("\nLocal Projects:\n", fg=typer.colors.CYAN, bold=True)

    for project in sorted(local_projects, key=str.casefold):
        typer.echo(f"- {project}")


@app.command()
def remote() -> None:
    """
    Show your remote projects.

    Show the projects that you own on GitHub.

    These mayinclude some you already have locally.
    Use 'show diff' to see the difference between local and remote.

    Examples:

    $ pytoil show remote
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    try:
        with msg.loading("Fetching your remote projects..."):
            remote_projects = api.get_repo_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if not remote_projects:
            msg.warn("You dont have any projects on GitHub yet!", exits=0)

        typer.secho("\nRemote Projects:\n", fg=typer.colors.CYAN, bold=True)

        for project in sorted(remote_projects, key=str.casefold):
            typer.echo(f"- {project}")


# Can't call it 'all', python keyword
@app.command(name="all")
def all_() -> None:
    """
    Show all your projects, grouped by local and remote.

    Examples:

    $ pytoil show all
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    try:
        with msg.loading("Fetching your projects..."):
            local_projects = utils.get_local_projects(path=config.projects_dir)
            remote_projects = api.get_repo_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        typer.secho("\nLocal Projects:\n", fg=typer.colors.CYAN, bold=True)

        if not local_projects:
            msg.warn("You don't have any local projects yet!")
        else:
            for project in sorted(local_projects, key=str.casefold):
                typer.echo(f"- {project}")

        typer.secho("\nRemote Projects:\n", fg=typer.colors.CYAN, bold=True)

        if not remote_projects:
            msg.warn("You don't have any projects on GitHub yet!")
        else:
            for project in sorted(remote_projects, key=str.casefold):
                typer.echo(f"- {project}")


@app.command()
def diff() -> None:
    """
    Show the difference in local/remote projects.

    Show the projects that you own on GitHub but do not
    have locally.

    Examples:

    $ pytoil show diff
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    try:
        with msg.loading("Calculating difference..."):
            local_projects = utils.get_local_projects(path=config.projects_dir)
            remote_projects = api.get_repo_names()

            diff = remote_projects.difference(local_projects)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if not diff:
            msg.info("Your local and remote projects are in sync!")
            msg.good("Nothing to show!", exits=0)

        typer.secho("\nDiff: Remote - Local\n", fg=typer.colors.CYAN, bold=True)

        for project in sorted(diff, key=str.casefold):
            typer.echo(f"- {project}")
