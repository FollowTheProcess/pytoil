"""
The pytoil checkout command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

import click
import httpx
import questionary
from thefuzz import process

from pytoil import editor
from pytoil.api import API
from pytoil.cli import utils
from pytoil.cli.printer import printer
from pytoil.exceptions import (
    EnvironmentAlreadyExistsError,
    ExternalToolNotInstalledError,
)
from pytoil.git import Git
from pytoil.repo import Repo

if TYPE_CHECKING:
    from pytoil.config import Config
    from pytoil.environments import Environment


# The username/repo pattern
USER_REPO_REGEX = re.compile(r"^([A-Za-z0-9_.-])+/([A-Za-z0-9_.-])+$")

# The bare 'project' pattern
PROJECT_REGEX = re.compile(r"^([A-Za-z0-9_.-])+$")

FUZZY_SCORE_CUTOFF = 75


@click.command()
@click.argument("project", nargs=1)
@click.option(
    "-v",
    "--venv",
    is_flag=True,
    help="Attempt to auto-create a virtual environment.",
)
@click.pass_obj
def checkout(config: Config, project: str, venv: bool) -> None:
    """
    Checkout an existing development project.

    The checkout command lets you easily resume work on an existing project,
    whether that project is available locally in your configured projects
    directory, or if it is on GitHub.

    If pytoil finds your project locally, and you have specified an editor in your
    config file it will open it for you. If not, it will just tell you it already
    exists locally and where to find it.

    If your project is on your GitHub, pytoil will clone it for you and then open it
    (or tell you where it cloned it if you dont have an editor set up).

    Finally, if checkout can't find a match after searching locally and on GitHub,
    it will prompt you to use 'pytoil new' to create a new one.

    If you pass the shorthand to someone elses repo e.g. 'someoneelse/repo' pytoil
    will detect this and ask you whether you want to create a fork or clone the original.
    Forking happens asynchronously so we give it a few seconds, then check whether or not
    your fork exists yet. If it does, all is well and we can clone it for you
    automatically. If not, (which is totally normal), we'll let you know. In
    which case just give it a few seconds then a 'pytoil checkout repo'
    will bring it down as normal.

    If you pick "clone" then it just clones the original for you.

    You can also ask pytoil to automatically create a virtual environment on
    checkout with the '--venv/-v' flag. This only happens for projects pulled down
    from GitHub to avoid accidentally screwing up local projects.

    If the '--venv/-v' flag is used, pytoil will look at your project to try and detect
    which type of environment to create e.g. conda, flit, poetry, standard python etc.

    The '--venv/-v' flag will also attempt to detect if the project you're checking out
    is a python package, in which case it will install it's requirements into the
    created environment.

    More info about this can be found in the documentation. Use `pytoil docs` to go there.

    Examples:
    $ pytoil checkout my_project

    $ pytoil checkout my_project --venv

    $ pytoil checkout someoneelse/project
    """
    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    git = Git()

    if bool(USER_REPO_REGEX.match(project)):
        # We've matched the "user/repo" pattern, meaning the user wants
        # to create a fork
        owner, name = project.split("/")
        if owner == config.username:
            printer.warn(
                "You don't need the '/' when checking out a repo you own", exits=1
            )

        checkout_fork(
            owner=owner,
            name=name,
            api=api,
            config=config,
            git=git,
            venv=venv,
        )

        printer.good("Done!")

    elif bool(PROJECT_REGEX.match(project)):
        if repo.exists_local():
            checkout_local(repo=repo, config=config, venv=venv)
        elif repo.exists_remote(api):
            checkout_remote(repo=repo, config=config, venv=venv, git=git)
        else:
            printer.error(f"{project!r} not found locally or on GitHub.")
            local_projects: set[str] = {
                f.name
                for f in config.projects_dir.iterdir()
                if f.is_dir() and not f.name.startswith(".")
            }
            try:
                remote_projects = api.get_repo_names()
            except httpx.HTTPStatusError as err:
                utils.handle_http_status_error(err)
            else:
                all_projects = local_projects.union(remote_projects)

                best_match: tuple[str, int] = process.extractOne(
                    query=project, choices=all_projects, score_cutoff=FUZZY_SCORE_CUTOFF
                )
                if best_match:
                    best_match_name, _ = best_match
                    printer.note(f"Did you mean {best_match_name}?", exits=1)

    else:
        # Unrecognised regex
        printer.error(f"{project!r} did not match valid pattern.")
        printer.note('Valid patterns are "user/repo" or "repo".', exits=1)


def checkout_fork(
    owner: str,
    name: str,
    api: API,
    config: Config,
    git: Git,
    venv: bool,
) -> None:
    """
    Forks the passed repo, clones it, sets the upstream and informs
    the user along the way.
    """
    # Check if we've already forked it, in which case the repo will already
    # exist under the user's namespace
    fork = Repo(
        owner=config.username,
        name=name,
        local_path=config.projects_dir.joinpath(name),
    )
    original = Repo(
        owner=owner, name=name, local_path=config.projects_dir.joinpath(name)
    )

    if not original.exists_remote(api=api):
        printer.error(f"{owner}/{name} not found on GitHub. Was it a typo?", exits=1)

    printer.info(f"{owner}/{name} belongs to {owner}")
    choice: str = questionary.select(
        "Fork project or clone the original?", choices=("fork", "clone")
    ).ask()

    if fork.exists_remote(api):
        printer.warn(f"Looks like you've already forked {owner}/{name}")
        printer.note(f"Use pytoil checkout {name} to pull down your fork.", exits=1)

    if choice == "fork":
        with printer.progress() as p:
            p.add_task(f"[bold white]Forking {owner}/{name}")
            try:
                api.create_fork(owner=owner, repo=name)
            except httpx.HTTPStatusError as err:
                utils.handle_http_status_error(err)

            # Forking happens asynchronously
            # see https://docs.github.com/en/rest/reference/repos#create-a-fork
            # So here we naively just wait a few seconds before trying to clone the fork
            time.sleep(3)

        if not fork.exists_remote(api):
            printer.warn("Fork not available yet.")
            printer.note(
                "Forking happens asynchronously so this is normal. Give it a few"
                " more seconds and try checking it out again.",
                exits=1,
            )

        printer.info(f"Cloning your fork: {config.username}/{name}.", spaced=True)
        # Only cloning 1 repo so makes sense to show the clone output
        git.clone(url=fork.clone_url, cwd=config.projects_dir, silent=False)

        printer.info("Setting 'upstream' to original repo.")
        git.set_upstream(owner=owner, repo=name, cwd=fork.local_path)

        # Automatic environment detection
        env = fork.dispatch_env(config=config)

        if venv:
            handle_venv_creation(env=env)

        if config.specifies_editor():
            printer.sub_info(f"Opening {fork.name} with {config.editor}")
            editor.launch(path=config.projects_dir.joinpath(name), binary=config.editor)
    elif choice == "clone":
        checkout_remote(repo=original, config=config, venv=venv, git=git)
    else:
        # We'll only get here if the user hits ctrl + c or something so just abort
        printer.error("Aborting", exits=1)


def handle_venv_creation(env: Environment | None) -> None:
    """
    Handles automatic detection and creation of python virtual
    environments based on detected repo context.
    """
    if not env:
        printer.warn("Unable to auto-detect required environment. Skipping.")

    else:
        printer.info(
            f"Auto creating virtual environment using: {env.name}", spaced=True
        )
        if env.name == "conda":
            printer.note("Conda environments can take a few minutes to create.")

        try:
            with printer.progress() as p:
                p.add_task("[bold white]Working")
                env.install_self(silent=True)
        except ExternalToolNotInstalledError:
            printer.error(f"{env.name} not installed", exits=1)
        except EnvironmentAlreadyExistsError:
            printer.warn("Environment already exists. Skipping.")


def checkout_local(repo: Repo, config: Config, venv: bool) -> None:
    """
    Helper to checkout a local repo.
    """
    printer.info(f"{repo.name} available locally.")

    # No environment or git stuff here, chances are if it exists locally
    # user has already done all this stuff
    if venv:
        printer.note("The --venv flag is ignored for local projects.")

    if config.specifies_editor():
        printer.sub_info(f"Opening {repo.name} with {config.editor}")
        editor.launch(path=repo.local_path, binary=config.editor)


def checkout_remote(repo: Repo, config: Config, venv: bool, git: Git) -> None:
    """
    Helper to checkout a remote repo.
    """
    printer.info(f"{repo.owner}/{repo.name} found on GitHub. Cloning...", spaced=True)
    # Only cloning 1 repo so makes sense to show output
    git.clone(url=repo.clone_url, cwd=config.projects_dir, silent=False)

    env = repo.dispatch_env(config=config)

    if venv:
        handle_venv_creation(env=env)

    if config.specifies_editor():
        printer.info(f"Opening {repo.name} with {config.editor}", spaced=True)
        editor.launch(path=repo.local_path, binary=config.editor)
