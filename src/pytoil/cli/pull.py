"""
The pytoil pull command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio

import asyncclick as click
import httpx
import questionary

from pytoil.api import API
from pytoil.cli import utils
from pytoil.cli.printer import printer
from pytoil.config import Config
from pytoil.git import Git
from pytoil.repo import Repo


@click.command()
@click.argument("projects", nargs=-1)
@click.option("-f", "--force", is_flag=True, help="Force pull without confirmation.")
@click.option("-a", "--all", "all_", is_flag=True, help="Pull down all your projects.")
@click.pass_obj
async def pull(
    config: Config, projects: tuple[str, ...], force: bool, all_: bool
) -> None:
    """
    Pull down your remote projects.

    The pull command provides easy methods for pulling down remote projects.

    It is effectively a nice wrapper around git clone but you don't have to
    worry about urls or what your cwd is, pull will grab your remote projects
    by name and clone them to your configured projects directory.

    You can also use pull to batch clone multiple repos, even all of them ("--all/-a")
    if you're into that sorta thing.

    If more than 1 repo is passed (or if "--all/-a" is used) pytoil will pull
    the repos concurrently, speeding up the process.

    Any remote project that already exists locally will be skipped and none of
    your local projects are changed in any way. pytoil will only pull down
    those projects that don't already exist locally.

    It's very possible to accidentally clone a lot of repos when using pull so
    you will be prompted for confirmation before pytoil does anything.

    The "--force/-f" flag can be used to override this confirmation prompt if
    desired.

    Examples:

    $ pytoil pull project1 project2 project3

    $ pytoil pull project1 project2 project3 --force

    $ pytoil pull --all

    $ pytoil pull --all --force
    """
    if not projects and not all_:
        printer.error(
            "If not using the '--all' flag, you must specify projects to pull.", exits=1
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
        if not remote_projects:
            printer.error("You don't have any remote projects to pull.", exits=1)

        specified_remotes = remote_projects if all_ else set(projects)

        # Check for typos
        for project in projects:
            if project not in remote_projects:
                printer.error(
                    f"{project!r} not found on GitHub. Was it a typo?", exits=1
                )

        diff = specified_remotes.difference(local_projects)
        if not diff:
            printer.good("Your local and remote projects are in sync!", exits=0)

        if not force:
            if len(diff) <= 3:
                message = f"This will pull down {', '.join(diff)}. Are you sure?"
            else:
                # Too many to show nicely
                message = f"This will pull down {len(diff)} projects. Are you sure?"

            confirmed: bool = await questionary.confirm(
                message, default=False, auto_enter=False
            ).ask_async()

            if not confirmed:
                printer.warn("Aborted", exits=1)

        # Now we're good to go
        to_clone = [
            Repo(
                owner=config.username,
                name=project,
                local_path=config.projects_dir.joinpath(project),
            )
            for project in diff
        ]
        git = Git()
        await asyncio.gather(
            *[clone_and_report(repo, git, config) for repo in to_clone]
        )


async def clone_and_report(repo: Repo, git: Git, config: Config) -> None:
    await git.clone(url=repo.clone_url, cwd=config.projects_dir)
    printer.good(f"Cloned {repo.name!r}")
