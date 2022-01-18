"""
The async-pytoil checkout command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio
import re

import asyncclick as click
import httpx
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.environments import Environment
from pytoil.exceptions import (
    EnvironmentAlreadyExistsError,
    ExternalToolNotInstalledException,
)
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.vscode import VSCode

# The username/repo pattern
USER_REPO_REGEX = re.compile(r"^([A-Za-z0-9_.-])+/([A-Za-z0-9_.-])+$")

# The bare 'project' pattern
PROJECT_REGEX = re.compile(r"^([A-Za-z0-9_.-])+$")


@click.command()
@click.argument("project", nargs=1)
@click.option(
    "-v",
    "--venv",
    is_flag=True,
    help="Attempt to auto-create a virtual environment.",
)
@click.pass_obj
async def checkout(config: Config, project: str, venv: bool) -> None:
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
    happens asynchronously so we give it a few seconds, then check whether or not
    your fork exists yet. If it does, all is well and we can clone it for you
    automatically. If not, (which is totally normal), we'll let you know. In
    which case just give it a few seconds then a 'pytoil checkout repo'
    will bring it down as normal.

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
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    code = VSCode(root=repo.local_path)
    git = Git()

    if bool(USER_REPO_REGEX.match(project)):
        # We've matched the "user/repo" pattern, meaning the user wants
        # to create a fork
        owner, name = project.split("/")
        if owner == config.username:
            msg.warn("You don't need the '/' when checking out a repo you own", exits=1)

        await checkout_fork(
            owner=owner,
            name=name,
            api=api,
            config=config,
            git=git,
            venv=venv,
        )

        msg.good("Done!")

    elif bool(PROJECT_REGEX.match(project)):
        # User has passed a single project
        local, remote = await asyncio.gather(
            repo.exists_local(), repo.exists_remote(api)
        )

        if local:
            await checkout_local(repo=repo, code=code, config=config, venv=venv)
        elif remote:
            await checkout_remote(
                repo=repo, code=code, config=config, venv=venv, git=git
            )
        else:
            # Unrecognised regex
            msg.fail(
                f"Argument: {project} did not match valid pattern.",
                text=(
                    "Valid pattern is 'project' for a local or remote project you own,"
                    " or 'user/project' to fork a repo you don't own."
                ),
                exits=1,
            )


async def checkout_fork(
    owner: str, name: str, api: API, config: Config, git: Git, venv: bool
) -> None:
    """
    Forks the passed repo, clones it, sets the upstream and informs
    the user along the way.
    """
    msg.info(f"'{owner}/{name}' belongs to {owner!r}")
    click.confirm(
        f"This will fork '{owner}/{name}' to your GitHub. Are you sure?", abort=True
    )

    # Check if we've already forked it, in which case the repo will already
    # exist under the user's namespace
    fork = Repo(
        owner=config.username,
        name=name,
        local_path=config.projects_dir.joinpath(name),
    )

    if await fork.exists_remote(api):
        msg.warn(
            f"Looks like you've already forked '{owner}/{name}'.",
            text=f"Use 'pytoil checkout {name}' to pull down your fork.",
            exits=1,
        )

    with msg.loading(f"Forking '{owner}/{name}'..."):
        try:
            await api.create_fork(owner=owner, repo=name)
        except httpx.HTTPStatusError as err:
            utils.handle_http_status_error(err)

        # Forking happens asynchronously
        # see https://docs.github.com/en/rest/reference/repos#create-a-fork
        # So here we naively just wait a few seconds before trying to clone the fork
        await asyncio.sleep(3)

    if not await fork.exists_remote(api):
        msg.warn(
            "Fork not available yet.",
            text=(
                "Forking happens asynchronously so this is normal. Give it a few"
                " more seconds and try checking it out again."
            ),
            exits=1,
        )

    msg.info(f"Cloning your fork: {config.username}/{name}.", spaced=True)
    # Only cloning 1 repo so makes sense to show the clone output
    await git.clone(url=fork.clone_url, cwd=config.projects_dir, silent=False)

    msg.info("Setting 'upstream' to original repo.")
    await git.set_upstream(owner=owner, repo=name, cwd=fork.local_path)

    # Automatic environment detection
    env = await fork.dispatch_env()

    # Special code instance because the argument 'project' will be the user/repo pattern
    code = VSCode(root=config.projects_dir.joinpath(name))

    if venv:
        await handle_venv_creation(env=env, config=config, code=code)

    if config.vscode:
        msg.info(f"Opening {fork.name!r} in VSCode.")
        await code.open()


async def handle_venv_creation(
    env: Environment | None, config: Config, code: VSCode
) -> None:
    """
    Handles automatic detection and creation of python virtual
    environments based on detected repo context.
    """
    if not env:
        msg.warn("Unable to auto-detect required environment. Skipping.")

    else:
        msg.info(f"Auto creating virtual environment using: {env.name!r}")
        if env.name == "conda":
            msg.text("Note: Conda environments can take a few minutes to create.")

        try:
            with msg.loading("Working..."):
                await env.install_self(silent=True)
        except ExternalToolNotInstalledException:
            msg.fail(title=f"{env.name!r} not installed", exits=1)
        except EnvironmentAlreadyExistsError:
            msg.warn(
                title="Environment already exists",
                text="No need to create a new one, Skipping.",
            )
        finally:
            # Because the first exception will exit, this is okay
            # to call as finally
            if config.vscode:
                await code.set_workspace_python(python_path=env.executable)


async def checkout_local(repo: Repo, code: VSCode, config: Config, venv: bool) -> None:
    """
    Helper to checkout a local repo.
    """
    msg.info(f"{repo.name} available locally")

    # No environment or git stuff here, chances are if it exists locally
    # user has already done all this stuff
    if venv:
        click.secho("Note: '--venv' is ignored for local projects.", fg="yellow")

    if config.vscode:
        msg.info(f"Opening {repo.name!r} in VSCode.")
        await code.open()


async def checkout_remote(
    repo: Repo, code: VSCode, config: Config, venv: bool, git: Git
) -> None:
    """
    Helper to checkout a remote repo.
    """
    msg.info(f"{repo.name} found on GitHub. Cloning...", spaced=True)
    # Only cloning 1 repo so makes sense to show output
    await git.clone(url=repo.clone_url, cwd=config.projects_dir, silent=False)

    env = await repo.dispatch_env()

    if venv:
        await handle_venv_creation(env=env, config=config, code=code)

    if config.vscode:
        msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
        await code.open()
