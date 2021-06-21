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

app = typer.Typer(name="remove", no_args_is_help=True)


# Callback for documentation only
@app.callback()
def remove() -> None:
    """
    Remove projects from your local filesystem.

    The remove command provides an easy interface for decluttering your local
    projects directory.

    You can selectively remove any number of projects or nuke the whole thing
    if you want.

    As with most programmatic deleting, the directories are deleted instantly and
    not sent to trash. As such, pytoil will prompt you for confirmation before
    doing anything.

    The "--force/-f" flag can be used to force deletion without the confirmation
    prompt. Use with caution!
    """


# Again, can't call it 'all', python keyword
@app.command(name="all")
def all_(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force delete without confirmation.",
        show_default=False,
    )
) -> None:
    """
    Delete all your projects.

    Recursively delete every subdirectory in your configured
    projects directory.

    This is really reserved for those "I'm having a really bad day" moments
    and should be treated with caution.

    You will be prompted for confirmation unless the '--force/-f' flag is used.

    Examples:

    $ pytoil remove all

    $ pytoil remove all --force
    """
    config = Config.from_file()

    local_projects = utils.get_local_projects(path=config.projects_dir)

    if not local_projects:
        msg.warn("You don't have any local projects to remove!", spaced=True, exits=1)

    if not force:
        typer.confirm(
            "This will remove ALL of your projects. Are you sure?", abort=True
        )

    # If we get here, user either used '--force' or said yes

    for project in sorted(local_projects, key=str.casefold):
        typer.secho(f"Removing project: {project!r}.", fg=typer.colors.YELLOW)
        shutil.rmtree(config.projects_dir.joinpath(project))

    msg.good("Done!", spaced=True)


@app.command()
def these(
    projects: List[str] = typer.Argument(..., help="Name of the project(s) to delete."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force delete without confirmation.",
        show_default=False,
    ),
) -> None:
    """
    Delete specified projects.

    Recursively delete the specified projects from your configured
    projects directory.

    You will be prompted for confirmation unless the '--force/-f' flag is used.

    Examples:

    $ pytoil remove these project1 project2 project

    $ pytoil remove these project1 project2 project3 --force
    """
    config = Config.from_file()

    local_projects = utils.get_local_projects(path=config.projects_dir)

    if not local_projects:
        msg.warn("You don't have any local projects to remove!", spaced=True, exits=1)

    # If user gives a project that isn't here (e.g. typo), abort
    for project in projects:
        if project not in local_projects:
            msg.warn(
                f"{project!r} not found in projects directory. Was it a typo?",
                spaced=True,
                exits=1,
            )

    if not force:
        if len(projects) <= 5:
            # A manageable length to display each one
            typer.confirm(
                f"This will remove {', '.join(projects)} from your local filesystem. Are you sure?",  # noqa: E501
                abort=True,
            )
        else:
            # Too many to show and look nice, just show a number
            typer.confirm(
                f"This will remove {len(projects)} projects from your local filesystem. Are you sure?",  # noqa: E501
                abort=True,
            )

    # If we get here, user either used '--force' or said yes to the prompt

    for project in sorted(projects, key=str.casefold):
        typer.secho(f"Removing project: {project!r}.", fg=typer.colors.YELLOW)
        shutil.rmtree(config.projects_dir.joinpath(project))

    msg.good("Done!", spaced=True)
