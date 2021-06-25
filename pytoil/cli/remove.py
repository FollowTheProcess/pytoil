"""
The `pytoil remove` subcommand group.

Author: Tom Fleet
Created: 18/06/2021
"""

import shutil
from typing import List

import typer
from wasabi import msg

from pytoil.cli import utils
from pytoil.config import Config

app = typer.Typer()


@app.command()
def remove(
    projects: List[str] = typer.Argument(
        None,
        help="Name of the project(s) to delete.",
        show_default=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force delete without confirmation.",
        show_default=False,
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Delete all of your local projects.",
        show_default=False,
    ),
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
    config = Config.from_file()

    local_projects = utils.get_local_projects(path=config.projects_dir)

    if not local_projects:
        msg.warn("You don't have any local projects to remove!", spaced=True, exits=1)

    if not projects and not all_:
        msg.warn(
            "If not using the '--all' flag, you must specify projects to delete.",
            exits=1,
            spaced=True,
        )

    # If user gives a project that isn't here (e.g. typo), abort
    for project in projects:
        if project not in local_projects:
            msg.warn(
                f"{project!r} not found in projects directory. Was it a typo?",
                spaced=True,
                exits=1,
            )

    to_delete = local_projects if all_ else projects

    if not force:
        if all_:
            typer.confirm(
                "This will delete ALL of your projects. Are you sure?", abort=True
            )
            # We want to delete everything
            to_delete = local_projects

        elif len(projects) <= 5:
            typer.confirm(
                f"This will delete {', '.join(projects)} from your local filesystem. Are you sure?",  # noqa: E501
                abort=True,
            )
        else:
            # Too many to print out nicely
            typer.confirm(
                f"This will delete {len(projects)} projects from your local filesystem. Are you sure?",  # noqa: E501
                abort=True,
            )

    # If we get here, user has used --force or said yes when prompted

    for project in sorted(to_delete, key=str.casefold):
        typer.secho(f"Removing project: {project!r}.", fg=typer.colors.YELLOW)
        shutil.rmtree(config.projects_dir.joinpath(project))

    msg.good("Done!", spaced=True)
