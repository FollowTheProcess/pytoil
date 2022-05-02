"""
The pytoil remove command.


Author: Tom Fleet
Created: 21/12/2021
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
@click.option(
    "-a",
    "--all",
    "all_",
    is_flag=True,
    help="Delete all of your local projects.",
)
@click.pass_obj
async def remove(
    config: Config, projects: tuple[str, ...], force: bool, all_: bool
) -> None:
    """
    Remove projects from your local filesystem.

    The remove command provides an easy interface for decluttering your local
    projects directory.

    You can selectively remove any number of projects by passing them as
    arguments or nuke the whole lot with "--all/-a" if you want.

    As with most programmatic deleting, the directories are deleted instantly and
    not sent to trash. As such, pytoil will prompt you for confirmation before
    doing anything.

    The "--force/-f" flag can be used to force deletion without the confirmation
    prompt. Use with caution!

    Examples:

    $ pytoil remove project1 project2 project3

    $ pytoil remove project1 project2 project3 --force

    $ pytoil remove --all

    $ pytoil remove --all --force
    """
    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    if not local_projects:
        printer.error("You don't have any local projects to remove", exits=1)

    if not projects and not all_:
        printer.error(
            "If not using the '--all' flag, you must specify projects to remove.",
            exits=1,
        )

    # If user gives a project that doesn't exist (e.g. typo), abort
    for project in projects:
        if project not in local_projects:
            printer.error(
                f"{project!r} not found under {config.projects_dir}. Was it a typo?",
                exits=1,
            )

    to_delete = local_projects if all_ else projects

    if not force:
        if all_:
            question = questionary.confirm(
                "This will delete ALL of your projects. Are you sure?",
                default=False,
                auto_enter=False,
            )
        elif len(projects) <= 3:
            # Nice number to show the names
            question = questionary.confirm(
                f"This will delete {', '.join(projects)} from your local filesystem."
                " Are you sure?",
                default=False,
                auto_enter=False,
            )
        else:
            # Too many to print the names nicely
            question = questionary.confirm(
                f"This will delete {len(projects)} projects from your local filesystem."
                " Are you sure?",
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
