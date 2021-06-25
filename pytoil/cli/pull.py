"""
The `pytoil pull` subcommand group.

Author: Tom Fleet
Created: 18/06/2021
"""

from typing import List, Set

import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.git import Git
from pytoil.repo import Repo

app = typer.Typer()


@app.command()
def pull(
    projects: List[str] = typer.Argument(
        None,
        help="Name of the project(s) to pull down.",
        show_default=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force pull without confirmation.",
        show_default=False,
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Pull down all of your projects.",
        show_default=False,
    ),
) -> None:
    """
    Pull down your remote projects.

    The pull command provides easy methods for pulling down remote projects.

    It is effectively a nice wrapper around git clone but you don't have to
    worry about urls or what your cwd is, pull will grab your remote projects
    by name and clone them to your configured projects directory.

    You can also use pull to batch clone multiple repos, even all of them ("--all/-a")
    if you're into that sorta thing.

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
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    if not projects and not all_:
        msg.warn(
            "If not using the '--all' flag, you must specify projects to pull.",
            exits=1,
            spaced=True,
        )

    try:
        not_found = False
        with msg.loading("Calculating difference..."):
            local_projects = utils.get_local_projects(path=config.projects_dir)
            remote_projects = api.get_repo_names()

            specified_remotes = remote_projects if all_ else set(projects)

            for project in projects:
                if project not in remote_projects:
                    not_found = True
                    not_found_project = project
                    break
                break

        if not_found:
            # If we don't break out of the with block
            # the spinner will go forever
            msg.warn(
                f"{not_found_project!r} not found on GitHub. Was it a typo?",
                spaced=True,
                exits=1,
            )

        diff = specified_remotes.difference(local_projects)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        pull_diff(
            diff=diff, remotes=remote_projects, force=force, config=config, git=Git()
        )


def pull_diff(
    diff: Set[str], remotes: Set[str], force: bool, config: Config, git: Git
) -> None:
    """
    Helper function to help the pull CLI command with repeated logic.

    Args:
        diff (Set[str]): The difference to clone.
        remotes (Set[str]): Set of remote projects.
        force (bool): The value for the '--force' flag.
        config (Config): The Config object.
    """

    if not diff:
        msg.info("Your local and remote projects are in sync.")
        msg.good("Nothing to pull!", exits=0)

    if not remotes:
        msg.warn("You don't have any remote projects to pull!", spaced=True, exits=1)

    if not force:
        if len(diff) <= 5:
            # A managable length to display each one
            typer.confirm(
                f"This will pull down {', '.join(diff)}. Are you sure?", abort=True
            )
        else:
            # Too many to show to look nice, just show number
            typer.confirm(
                f"This will pull down {len(diff)} projects. Are you sure?", abort=True
            )

    # If we get here, we're good to go

    for project in diff:
        # Make a Repo object for each
        repo = Repo(
            owner=config.username,
            name=project,
            local_path=config.projects_dir.joinpath(project),
        )

        msg.info(f"Cloning {project!r}", spaced=True)
        git.clone(url=repo.clone_url, cwd=config.projects_dir)

    msg.good("Done!", spaced=True)
