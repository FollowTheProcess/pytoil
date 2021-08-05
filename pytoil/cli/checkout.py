"""
The pytoil checkout command.

Author: Tom Fleet
Created: 25/06/2021
"""

import re
import time
from typing import Optional

import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.environments.abstract import Environment
from pytoil.exceptions import (
    EnvironmentAlreadyExistsError,
    ExternalToolNotInstalledException,
)
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.vscode import VSCode

app = typer.Typer()

# The username/repo pattern
USER_REPO_REGEX = re.compile(r"^([A-Za-z0-9_.-])+/([A-Za-z0-9_.-])+$")

# The bare 'project' pattern
PROJECT_REGEX = re.compile(r"^([A-Za-z0-9_.-])+$")


@app.command()
def checkout(
    project: str = typer.Argument(
        ...,
        help="Name of the project to checkout.",
    ),
    venv: bool = typer.Option(
        False,
        "--venv",
        "-v",
        help="Attempt to auto-create a virtual environment.",
        show_default=False,
    ),
) -> None:
    """
    Checkout an existing development project.

    The checkout command lets you easily resume work on an existing project,
    whether that project is available locally in your configured projects
    directory, or if it is on GitHub.

    If pytoil finds your project locally, and you have enabled VSCode in your
    config file it will open it for you. If not, it will just tell you it already
    exists locally and where to find it.

    If your project is on your GitHub, pytoil will clone it for you and then open it
    (or tell you where it cloned it if you dont have VSCode set up).

    Finally, if checkout can't find a match after searching locally and on GitHub,
    it will prompt you to use 'pytoil new' to create a new one.

    If you pass the shorthand to someone elses repo e.g. 'someoneelse/repo' pytoil
    will detect this and automatically create a fork of this repo for you. Forking
    happens asynchronously so we can't clone your fork straight away. Give it a
    few seconds then a 'pytoil checkout repo' will bring it down as normal.

    You can also ask pytoil to automatically create a virtual environment on
    checkout with the '--venv/-v' flag. This only happens for projects pulled down
    from GitHub to avoid accidentally screwing up local projects.

    If the '--venv/-v' flag is used, pytoil will look at your project to try and detect
    which type of environment to create e.g. conda, flit, poetry, standard python etc.

    The '--venv/-v' flag will also attempt to detect if the project you're checking out
    is a python package, in which case it will install it's requirements into the
    created environment.

    More info about this can be found in the documentation.

    Examples:

    $ pytoil checkout my_project

    $ pytoil checkout my_project --venv

    $ pytoil checkout someoneelse/project
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    # Setup the objects required
    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    code = VSCode(root=repo.local_path)
    git = Git()

    if bool(USER_REPO_REGEX.match(project)):
        # We've matched the "user/repo" pattern, meaning the user
        # wants to create a fork
        owner, name = project.split("/")
        fork_repo(
            owner=owner,
            name=name,
            api=api,
            config=config,
            git=git,
            venv=venv,
        )
        msg.good("Done!", spaced=True, exits=0)

    elif bool(PROJECT_REGEX.match(project)):
        # User has just passed a single project

        if repo.exists_local():
            checkout_local(repo=repo, code=code, config=config, venv=venv)

        elif repo.exists_remote(api=api):
            msg.info(f"{repo.name!r} found on GitHub. Cloning...", spaced=True)
            git.clone(
                url=repo.clone_url, check=True, cwd=config.projects_dir, silent=False
            )

            env = repo.dispatch_env()

            if venv:
                handle_venv_creation(env=env, config=config, code=code)

            if config.vscode:
                msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
                code.open()

        else:
            msg.warn(
                title=f"{repo.name!r} not found locally or on GitHub!",
                text=f"Does it exist? If not, create a new project with 'pytoil new {repo.name}'.",  # noqa: E501
                exits=1,
            )

    else:
        # User has passed garbage
        msg.fail(
            f"Argument: {project} did not match any valid syntax.",
            text="Valid syntax is 'project' for a local or remote project you own, "
            "or 'user/project' to fork a repo you don't own.",
            exits=1,
            spaced=True,
        )


def fork_repo(
    owner: str, name: str, api: API, config: Config, git: Git, venv: bool
) -> None:
    """
    Forks the passed repo, clones it, sets the upstream
    and informs the user along the way.

    Args:
        owner (str): Owner of the repo to be forked.
        name (str): Name of the repo to be forked.
        api (API): Configured API object.
        config (Config): Configured Config object.
        git (Git): The Git object.
        venv (bool): Whether or not the user wants a virtual environment.
    """
    # TODO: Lots of duplicated code here with the rest of checkout
    # simplify this so it integrates a bit better

    if owner == config.username:
        msg.warn(
            "You don't need the '/' when checking out a repo you own!",
            spaced=True,
            exits=1,
        )

    msg.info(f"'{owner}/{name}' belongs to {owner!r}.", spaced=True)
    typer.confirm(
        f"This will fork '{owner}/{name}' to your GitHub. Are you sure?", abort=True
    )
    with msg.loading(f"Forking '{owner}/{name}'..."):
        try:
            api.create_fork(owner=owner, repo=name)
        except httpx.HTTPStatusError as err:
            utils.handle_http_status_errors(err)

        # Forking happens asynchronously
        # see https://docs.github.com/en/rest/reference/repos#create-a-fork
        # So here we naively just wait a few seconds before trying to clone the fork
        # this may need to change and there is most likely a better way of doing this
        time.sleep(3)

    # Now we check if the user's fork exists
    # If not, we report that to the user and exit
    fork = Repo(
        owner=config.username, name=name, local_path=config.projects_dir.joinpath(name)
    )
    code = VSCode(root=fork.local_path)
    if not fork.exists_remote(api=api):
        msg.warn(
            "Fork not available yet",
            text="Forking happens asynchronously so this is normal. "
            "Give it a few more seconds and try checking it out again.",
            exits=1,
        )

    # If we get here, the fork was a success
    msg.info(f"Cloning your fork: {config.username}/{name}.", spaced=True)
    git.clone(url=fork.clone_url, cwd=config.projects_dir, silent=False)

    # Set upstream
    msg.info("Setting 'upstream' to original repo.", spaced=True)
    git.set_upstream(owner=owner, repo=name, path=fork.local_path)

    env = fork.dispatch_env()

    if venv:
        handle_venv_creation(env=env, config=config, code=code)

    if config.vscode:
        msg.info(f"Opening {fork.name!r} in VSCode.")
        code.open()


def checkout_local(repo: Repo, code: VSCode, config: Config, venv: bool) -> None:
    """
    Helper function to checkout a local repo.

    Args:
        repo (Repo): Repo to checkout.
        code (VSCode): VSCode instance to handle opening.
        config (Config): Configured Config object.
        venv (bool): The value from the --venv flag.
    """

    msg.info(f"{repo.name!r} available locally.", spaced=True)

    # No environment or git stuff here, chances are if it exists locally
    # user has already done all this stuff
    if venv:
        typer.secho(
            "Note: '--venv' is ignored for local projects.",
            fg=typer.colors.YELLOW,
        )

    if config.vscode:
        msg.text(f"Opening {repo.name!r} in VSCode.")
        code.open()


def handle_venv_creation(
    env: Optional[Environment], config: Config, code: VSCode
) -> None:
    """
    Handles the automatic detection and/or creation of
    python virtual environments based on detected repo
    contents and reports to the user.

    Args:
        env (Optional[Environment]): The Environment object
        config (Config): Populated Config object.
        code (VSCode): VSCode object.
    """
    if not env:
        msg.warn(
            "Unable to auto-detect required environent. Skipping.",
            spaced=True,
        )
    else:
        msg.info(
            f"Auto creating virtual environment using: {env.info_name!r}",
            spaced=True,
        )
        if env.info_name == "conda":
            msg.text("Note: Conda environments can take up to a few minutes to create.")

        try:
            with msg.loading("Working..."):
                env.install_self()
        except ExternalToolNotInstalledException:
            msg.fail(title=f"{env.info_name!r} not installed", spaced=True, exits=1)
        except EnvironmentAlreadyExistsError:
            msg.warn(
                title="Environment already exists!",
                text="No need to create a new one. Skipping.",
            )
        finally:
            # Because the first exception will exit, this is okay
            # to call as finally
            if config.vscode:
                code.set_workspace_python(python_path=env.executable)
