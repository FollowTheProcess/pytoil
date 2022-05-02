"""
The pytoil keep command.


Author: Tom Fleet
Created: 06/02/2022
"""

from __future__ import annotations

import asyncio
import functools
import shutil

import asyncclick as click
import questionary

from pytoil.cli.printer import printer
from pytoil.config import Config


@click.command()
@click.argument("projects", nargs=-1)
@click.option("-f", "--force", is_flag=True, help="Force delete without confirmation.")
@click.pass_obj
async def keep(config: Config, projects: tuple[str, ...], force: bool) -> None:
    """
    Remove all but the specified projects.

    The keep command lets you delete all projects from your local
    projects directory whilst keeping the specified ones untouched.

    It is effectively the inverse of `pytoil remove`.

    As with most programmatic deleting, the directories are deleted instantly and
    not sent to trash. As such, pytoil will prompt you for confirmation before
    doing anything.

    The "--force/-f" flag can be used to force deletion without the confirmation
    prompt. Use with caution!

    Examples:

    $ pytoil keep project1 project2 project3

    $ pytoil keep project1 project2 project3 --force
    """
    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    if not local_projects:
        printer.error("You don't have any local projects to remove", exits=1)

    # If user gives a project that doesn't exist (e.g. typo), abort
    for project in projects:
        if project not in local_projects:
            printer.error(
                f"{project!r} not found under {config.projects_dir}. Was it a typo?",
                exits=1,
            )

    specified = set(projects)
    to_delete = local_projects.difference(specified)

    if not force:
        if len(to_delete) <= 3:
            # Nice number to show the names
            question = questionary.confirm(
                f"This will delete {', '.join(to_delete)} from your local filesystem."
                " Are you sure?",
                default=False,
                auto_enter=False,
            )
        else:
            # Too many to print the names nicely
            question = questionary.confirm(
                f"This will delete {len(to_delete)} projects from your local"
                " filesystem. Are you sure?",
                default=False,
                auto_enter=False,
            )

        confirmed: bool = await question.ask_async()

        if not confirmed:
            printer.warn("Aborted", exits=1)

    # If we get here, user has used --force or said yes when prompted
    # Go async!
    await asyncio.gather(*[remove_and_report(config, project) for project in to_delete])


async def remove_and_report(config: Config, project: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor=None,
        func=functools.partial(
            shutil.rmtree,
            path=config.projects_dir.joinpath(project),
            ignore_errors=True,
        ),
    )
    printer.good(f"Deleted {project}")
