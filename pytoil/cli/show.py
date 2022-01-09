"""
The pytoil show command group.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
import httpx
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config


@click.group()
async def show() -> None:
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


@show.command()
@click.option("-c", "--count", is_flag=True, help="Display a count of local projects.")
@click.pass_obj
async def local(config: Config, count: bool) -> None:
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
    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    if not local_projects:
        msg.warn("You don't have any local projects yet!", exits=1)

    click.secho("\nLocal Projects:\n", fg="cyan", bold=True)

    if count:
        click.echo(f"You have {len(local_projects)} local projects")
    else:
        for project in sorted(local_projects, key=str.casefold):
            click.echo(f"- {project}")


@show.command()
@click.option("-c", "--count", is_flag=True, help="Display a count of remote projects.")
@click.pass_obj
async def remote(config: Config, count: bool) -> None:
    """
    Show your remote projects.

    Show the projects that you own on GitHub.

    These may include some you already have locally.
    Use 'show diff' to see the difference between local and remote.

    The "--count/-c" flag can be used to show a count of remote projects.

    Examples:

    $ pytoil show remote

    $ pytoil show remote --count
    """
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)

    try:
        remotes_projects = await api.get_repo_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not remotes_projects:
            msg.warn("You don't have any projects on GitHub yet.", exits=1)

        click.secho("\nRemote Projects:\n", fg="cyan", bold=True)

        if count:
            click.echo(f"You have {len(remotes_projects)} remote projects.")
        else:
            for project in sorted(remotes_projects, key=str.casefold):
                click.echo(f"- {project}")


@show.command()
@click.option("-c", "--count", is_flag=True, help="Display a count of forked projects.")
@click.pass_obj
async def forks(config: Config, count: bool) -> None:
    """
    Show your forked projects.

    Show the projects you own on GitHub that are forks
    of other projects.

    The "--count/-c" flag can be used to show a count of forks.

    Examples:

    $ pytoil show forks

    $ pytoil show forks --count
    """
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)

    try:
        forks = await api.get_fork_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not forks:
            msg.warn("You don't have any forks yet.", exits=1)

        click.secho("\nForks:\n", fg="cyan", bold=True)

        if count:
            click.echo(f"You have {len(forks)} forks.")
        else:
            for fork in sorted(forks, key=str.casefold):
                click.echo(f"- {fork}")


@show.command(name="all")
@click.option("-c", "--count", is_flag=True, help="Display a count of all projects.")
@click.pass_obj
async def all_(config: Config, count: bool) -> None:
    """
    Show all your projects, grouped by local and remote.

    The "--count/-c" flag will show a count of local/remote projects.

    Examples:

    $ pytoil show all

    $ pytoil show all --count
    """
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)

    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    try:
        remote_projects = await api.get_repo_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        click.secho("\nLocal Projects:\n", fg="cyan", bold=True)

        if not local_projects:
            msg.warn("You don't have any local projects yet.", exits=1)
        elif count:
            click.echo(f"You have {len(local_projects)} local projects.")
        else:
            for project in sorted(local_projects, key=str.casefold):
                click.echo(f"- {project}")

        click.secho("\nRemote Projects:\n", fg="cyan", bold=True)

        if not remote_projects:
            msg.warn("You don't have any projects on GitHub yet.", exits=1)
        elif count:
            click.echo(f"You have {len(remote_projects)}.")
        else:
            for project in sorted(remote_projects, key=str.casefold):
                click.echo(f"- {project}")


@show.command()
@click.option("-c", "--count", is_flag=True, help="Display a count of the diff.")
@click.pass_obj
async def diff(config: Config, count: bool) -> None:
    """
    Show the difference in local/remote projects.

    Show the projects that you own on GitHub but do not
    have locally.

    The "--count/-c" flag will show a count of the difference.

    Examples:

    $ pytoil show diff

    $ pytoil show diff --count
    """
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)

    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    try:
        remote_projects = await api.get_repo_names()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        diff = remote_projects.difference(local_projects)
        if not diff:
            msg.good("Your local and remote projects are in sync!")
        else:
            click.secho("\nDiff: Remote - Local\n", fg="cyan", bold=True)

            if count:
                click.echo(
                    f"You have {len(diff)} projects on GitHub that aren't available"
                    " locally."
                )
            else:
                for project in sorted(diff, key=str.casefold):
                    click.echo(f"- {project}")
