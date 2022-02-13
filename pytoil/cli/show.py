"""
The pytoil show command group.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles.os
import asyncclick as click
import httpx
import humanize
from rich.console import Console
from rich.table import Table, box

from pytoil.api import API
from pytoil.cli import utils
from pytoil.cli.printer import printer
from pytoil.config import Config

GITHUB_TIME_FORMAT = r"%Y-%m-%dT%H:%M:%SZ"
MAX_PROJECTS = 15  # Default max to show


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

    The "--limit/-l" flag can be used if you only want to see a certain number
    of results.
    """


@show.command()
@click.option(
    "-l",
    "--limit",
    type=int,
    default=MAX_PROJECTS,
    help="Maximum number of projects to list.",
    show_default=True,
)
@click.pass_obj
async def local(config: Config, limit: int) -> None:
    """
    Show your local projects.

    Show the projects you have locally in your configured
    projects directory.

    You can limit the number of projects shown with the
    "--limit/-l" flag.

    Examples:

    $ pytoil show local

    $ pytoil show local --limit 5
    """
    console = Console()
    local_projects: set[Path] = {
        f
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    if not local_projects:
        printer.error("You don't have any local projects yet!", exits=1)

    table = Table(box=box.SIMPLE)
    table.add_column("Name", style="bold white")
    table.add_column("Created")
    table.add_column("Modified")

    stats = await asyncio.gather(
        *[aiofiles.os.stat(project) for project in local_projects]
    )

    results = {project: stat for project, stat in zip(local_projects, stats)}

    printer.title("Local Projects", spaced=False)
    console.print(
        f"[bright_black italic]\nShowing {min(limit, len(results))} out of"
        f" {len(local_projects)} local projects [/]"
    )
    for path, result in sorted(results.items(), key=lambda x: str.casefold(str(x[0])))[
        :limit
    ]:
        table.add_row(
            path.name,
            humanize.naturaltime(datetime.utcfromtimestamp(result.st_birthtime)),
            humanize.naturaltime(datetime.utcfromtimestamp(result.st_mtime)),
        )

    console.print(table)


@show.command()
@click.option(
    "-l",
    "--limit",
    type=int,
    default=MAX_PROJECTS,
    help="Maximum number of projects to list.",
    show_default=True,
)
@click.pass_obj
async def remote(config: Config, limit: int) -> None:
    """
    Show your remote projects.

    Show the projects that you own on GitHub.

    These may include some you already have locally.
    Use 'show diff' to see the difference between local and remote.

    The "-l/--limit" flag can be used to limit the number of repos
    returned.

    Examples:

    $ pytoil show remote

    $ pytoil show remote --limit 10
    """
    console = Console()
    api = API(username=config.username, token=config.token)

    try:
        repos = await api.get_repos()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not repos:
            printer.error("You don't have any projects on GitHub yet.", exits=1)
            # Return so mypy knows we've narrowed type of repos
            return

        table = Table(box=box.SIMPLE)
        table.add_column("Name", style="bold white")
        table.add_column("Size")
        table.add_column("Created")
        table.add_column("Modified")

        printer.title("Remote Projects", spaced=False)
        console.print(
            f"[bright_black italic]\nShowing {min(limit, len(repos))} out of"
            f" {len(repos)} remote projects [/]"
        )

        for repo in repos[:limit]:
            table.add_row(
                repo["name"],
                humanize.naturalsize(int(repo["diskUsage"]) * 1024),
                humanize.naturaltime(
                    datetime.strptime(repo["createdAt"], GITHUB_TIME_FORMAT)
                ),
                humanize.naturaltime(
                    datetime.strptime(repo["pushedAt"], GITHUB_TIME_FORMAT)
                ),
            )

        console.print(table)


@show.command()
@click.option(
    "-l",
    "--limit",
    type=int,
    default=MAX_PROJECTS,
    help="Maximum number of projects to list.",
    show_default=True,
)
@click.pass_obj
async def forks(config: Config, limit: int) -> None:
    """
    Show your forked projects.

    Show the projects you own on GitHub that are forks
    of other projects.

    The "-l/--limit" flag can be used to limit the number of
    repos returned.

    Examples:

    $ pytoil show forks

    $ pytoil show forks --limit 10
    """
    console = Console()
    api = API(username=config.username, token=config.token)

    try:
        forks = await api.get_forks()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not forks:
            printer.error("You don't have any forks yet.", exits=1)
            return

        table = Table(box=box.SIMPLE)
        table.add_column("Name", style="bold white")
        table.add_column("Size")
        table.add_column("Forked")
        table.add_column("Modified")
        table.add_column("Parent")

        printer.title("Forked Projects", spaced=False)
        console.print(
            f"[bright_black italic]\nShowing {min(limit, len(forks))} out of"
            f" {len(forks)} forked projects [/]"
        )

        for repo in forks[:limit]:
            table.add_row(
                repo["name"],
                humanize.naturalsize(int(repo["diskUsage"]) * 1024),
                humanize.naturaltime(
                    datetime.strptime(repo["createdAt"], GITHUB_TIME_FORMAT)
                ),
                humanize.naturaltime(
                    datetime.strptime(repo["pushedAt"], GITHUB_TIME_FORMAT)
                ),
                repo["parent"]["nameWithOwner"],
            )

        console = Console()
        console.print(table)


@show.command()
@click.option(
    "-l",
    "--limit",
    type=int,
    default=MAX_PROJECTS,
    help="Maximum number of projects to list.",
    show_default=True,
)
@click.pass_obj
async def diff(config: Config, limit: int) -> None:
    """
    Show the difference in local/remote projects.

    Show the projects that you own on GitHub but do not
    have locally.

    The "-l/--limit" flag can be used to limit the number of repos
    returned.

    Examples:

    $ pytoil show diff

    $ pytoil show diff --limit 10
    """
    console = Console()
    api = API(username=config.username, token=config.token)

    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    try:
        remote_projects = await api.get_repos()
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not remote_projects:
            printer.error("You don't have any projects on GitHub yet!", exits=1)
            return

        remote_names: set[str] = {repo["name"] for repo in remote_projects}
        diff = remote_names.difference(local_projects)

        diff_info: list[dict[str, Any]] = []
        for repo in remote_projects:
            if name := repo.get("name"):
                if name in diff:
                    diff_info.append(repo)

        if not diff:
            printer.good("Your local and remote projects are in sync!")
        else:
            table = Table(box=box.SIMPLE)
            table.add_column("Name", style="bold white")
            table.add_column("Size")
            table.add_column("Created")
            table.add_column("Modified")

            printer.title("Diff: Remote - Local", spaced=False)
            console.print(
                f"[bright_black italic]\nShowing {min(limit, len(diff_info))} out of"
                f" {len(diff_info)} projects [/]"
            )

            for repo in diff_info[:limit]:
                table.add_row(
                    repo["name"],
                    humanize.naturalsize(int(repo["diskUsage"] * 1024)),
                    humanize.naturaltime(
                        datetime.strptime(repo["createdAt"], GITHUB_TIME_FORMAT)
                    ),
                    humanize.naturaltime(
                        datetime.strptime(repo["pushedAt"], GITHUB_TIME_FORMAT)
                    ),
                )

            console = Console()
            console.print(table)
