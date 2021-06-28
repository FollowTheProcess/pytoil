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

    The "--count/-c" flag can be used if you just want to see a count.
    """


@app.command()
def local(
    count: bool = typer.Option(
        False,
        "--count",
        "-c",
        help="Display a count of local projects.",
        show_default=False,
    )
) -> None:
    """
    Show your local projects.

    Show the projects you have locally in your configured
    projects directory.

    If the "--count/-c" flag is used, you will simply be
    shown the count of local projects.

    Examples:

    $ pytoil show local

    $ pytoil show local --count
    """
    config = Config.from_file()
    local_projects = utils.get_local_projects(path=config.projects_dir)

    if not local_projects:
        msg.warn("You don't have any local projects yet!", exits=0)

    typer.secho("\nLocal Projects:\n", fg=typer.colors.CYAN, bold=True)

    if count:
        typer.echo(f"You have {len(local_projects)} local projects")
    else:
        for project in sorted(local_projects, key=str.casefold):
            typer.echo(f"- {project}")


@app.command()
def remote(
    count: bool = typer.Option(
        False,
        "--count",
        "-c",
        help="Display a count of remote projects.",
        show_default=False,
    )
) -> None:
    """
    Show your remote projects.

    Show the projects that you own on GitHub.

    These mayinclude some you already have locally.
    Use 'show diff' to see the difference between local and remote.

    The "--count/-c" flag can be used to show a count of remote projects.

    Examples:

    $ pytoil show remote

    $ pytoil show remote --count
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

        if count:
            typer.echo(f"You have {len(remote_projects)} remote projects.")
        else:
            for project in sorted(remote_projects, key=str.casefold):
                typer.echo(f"- {project}")


# Can't call it 'all', python keyword
@app.command(name="all")
def all_(
    count: bool = typer.Option(
        False,
        "--count",
        "-c",
        help="Display a count of all projects.",
        show_default=False,
    )
) -> None:
    """
    Show all your projects, grouped by local and remote.

    The "--count/-c" flag will show a count of local/remote projects.

    Examples:

    $ pytoil show all

    $ pytoil show all --count
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    try:
        with msg.loading("Fetching your projects..."):
            local_projects = utils.get_local_projects(path=config.projects_dir)
            remote_projects = api.get_repo_names()
            n_locals = len(local_projects)
            n_remotes = len(remote_projects)
            total = n_locals + n_remotes
            local_pct = n_locals / total * 100
            remote_pct = n_remotes / total * 100

    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        typer.secho("\nLocal Projects:\n", fg=typer.colors.CYAN, bold=True)

        if not local_projects:
            msg.warn("You don't have any local projects yet!", exits=0)
        elif count:
            typer.echo(
                f"You have {n_locals} local projects. {local_pct:.2f}% of total."
            )
        else:
            for project in sorted(local_projects, key=str.casefold):
                typer.echo(f"- {project}")

        typer.secho("\nRemote Projects:\n", fg=typer.colors.CYAN, bold=True)

        if not remote_projects:
            msg.warn("You don't have any projects on GitHub yet!", exits=0)
        elif count:
            typer.echo(
                f"You have {n_remotes} remote projects. {remote_pct:.2f}% of total."
            )
        else:
            for project in sorted(remote_projects, key=str.casefold):
                typer.echo(f"- {project}")


@app.command()
def diff(
    count: bool = typer.Option(
        False,
        "--count",
        "-c",
        help="Display a count of the diff.",
        show_default=False,
    )
) -> None:
    """
    Show the difference in local/remote projects.

    Show the projects that you own on GitHub but do not
    have locally.

    The "--count/-c" flag will show a count of the difference.

    Examples:

    $ pytoil show diff

    $ pytoil show diff --count
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

        if count:
            typer.echo(
                f"You have {len(diff)} projects on GitHub that aren't available locally."  # noqa: E501
            )
        else:
            for project in sorted(diff, key=str.casefold):
                typer.echo(f"- {project}")
