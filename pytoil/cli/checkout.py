"""
The pytoil checkout command.

Author: Tom Fleet
Created: 25/06/2021
"""

import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.exceptions import EnvironmentAlreadyExistsError
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.vscode import VSCode

app = typer.Typer()


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
    which type of environment to create (conda or standard python).

    More info can be found in the documentation.

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

    # Naively detect a "user/repo" type pattern
    # in which case fork the repo
    if "/" in project:
        owner, name = project.split("/")
        fork_repo(owner=owner, name=name, api=api, config=config)

    if repo.exists_local():
        # No environment or git stuff here, chances are if it exists locally
        # user has already done all this stuff
        checkout_local(repo=repo, code=code, config=config)

    elif repo.exists_remote(api=api):
        msg.info(f"{repo.name!r} found on GitHub. Cloning...", spaced=True)
        git.clone(url=repo.clone_url, check=True, cwd=config.projects_dir)

        env = repo.dispatch_env()

        if venv:
            if not env:
                msg.warn(
                    "Unable to auto-detect required environent. Skipping.",
                    spaced=True,
                )
            else:
                msg.info("Auto creating correct virtual environment.", spaced=True)

                try:
                    with msg.loading("Creating Environment..."):
                        env.create(packages=config.common_packages)
                except EnvironmentAlreadyExistsError:
                    msg.warn(
                        title="Environment already exists!",
                        text="No need to create a new one. Skipping.",
                    )
                finally:
                    if config.vscode:
                        code.set_workspace_python(python_path=env.executable)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.open()

    else:
        msg.warn(
            title=f"{repo.name!r} not found locally or on GitHub!",
            text=f"Does it exist? If not, create a new project with 'pytoil new {repo.name}'.",  # noqa: E501
            exits=1,
        )


def fork_repo(owner: str, name: str, api: API, config: Config) -> None:
    """
    Forks the passed repo and informs the user.

    Args:
        owner (str): Owner of the repo to be forked.
        name (str): Name of the repo to be forked.
        api (API): Configured API object.
        config (Config): Configured Config object.
    """

    if owner == config.username:
        msg.warn(
            "You don't need the '/' when checking out a repo you own!",
            spaced=True,
            exits=1,
        )

    msg.info(f"'{owner}/{name}' belongs to {owner!r}. Making you a fork.")
    try:
        api.create_fork(owner=owner, repo=name)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(err)

    # Forking happens asynchronously so we can't clone straight away
    # so just report success and exit
    msg.good(
        "Done!",
        text="Note: Forking happens asynchronously on GitHub which means "
        "it may not be available to clone right away.",
        spaced=True,
        exits=0,
    )


def checkout_local(repo: Repo, code: VSCode, config: Config) -> None:
    """
    Helper function to checkout a local repo.

    Args:
        repo (Repo): Repo to checkout.
        code (VSCode): VSCode instance to handle opening.
        config (Config): Configured Config object.
    """

    msg.info(f"{repo.name!r} available locally.", spaced=True)

    if config.vscode:
        msg.text(f"Opening {repo.name!r} in VSCode.")
        code.open()
