"""
Assorted helper functions for the pytoil CLI.

Author: Tom Fleet
Created: 19/06/2021
"""

from pathlib import Path
from typing import List, Set

import httpx
from cookiecutter.main import cookiecutter
from wasabi import msg

from pytoil.api import API
from pytoil.config import Config
from pytoil.environments import Conda, Environment, Venv
from pytoil.exceptions import (
    CargoNotInstalledError,
    EnvironmentAlreadyExistsError,
    GoNotInstalledError,
)
from pytoil.git.git import Git
from pytoil.repo import Repo
from pytoil.starters import GoStarter, PythonStarter, RustStarter, Starter


def get_local_projects(path: Path) -> Set[str]:
    """
    Returns all the projects (directories) under
    `path`.
    """

    return {f.name for f in path.iterdir() if f.is_dir() and not f.name.startswith(".")}


def warn_if_no_api_creds(config: Config) -> None:
    """
    Will print a helpful warning message and exit the program
    if username or token are not filled out in the config file.
    """

    if not config.can_use_api():
        msg.warn(
            "You must fill set your username and token to use API features!",
            spaced=True,
            exits=1,
        )


def pre_new_checks(repo: Repo, api: API) -> None:
    """
    Checks whether the repo already exists either locally
    or remotely, prints helpful warning messages and exits
    the program if True.
    """

    is_local = repo.exists_local()

    try:
        is_remote = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        handle_http_status_errors(error=err)
    else:

        if is_local:
            msg.warn(
                title=f"{repo.name!r} already exists locally!",
                text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
                spaced=True,
                exits=1,
            )
        elif is_remote:
            msg.warn(
                title=f"{repo.name!r} already exists on GitHub!",
                text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
                spaced=True,
                exits=1,
            )


def make_new_project(
    repo: Repo, git: Git, cookie: str, starter: str, use_git: bool, config: Config
) -> None:
    """
    Create a new development project either from a cookiecutter
    template or from scratch.
    """
    # Can't use starter and cookiecutter at the same time
    if starter != Starter.none and cookie:
        msg.warn(
            "'--cookie' and '--starter' are mutually exclusive.",
            exits=1,
        )

    if cookie:
        # We don't initialise a git repo for cookiecutters
        # some templates have hooks which do this, mine do!
        msg.info(f"Creating {repo.name!r} from cookiecutter: {cookie!r}.")
        cookiecutter(template=cookie, output_dir=config.projects_dir)

    elif starter == "go":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        go_st = GoStarter(path=config.projects_dir, name=repo.name)
        try:
            go_st.generate(username=config.username)
        except GoNotInstalledError:
            msg.fail("Error: Go not installed.", spaced=True, exits=1)
        if use_git:
            git.init(path=repo.local_path, check=True)

    elif starter == "python":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        py_st = PythonStarter(path=config.projects_dir, name=repo.name)
        py_st.generate()
        if use_git:
            git.init(path=repo.local_path, check=True)

    elif starter == "rust":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        rs_st = RustStarter(path=config.projects_dir, name=repo.name)
        try:
            rs_st.generate()
        except CargoNotInstalledError:
            msg.fail("Error: Cargo not installed.", spaced=True, exits=1)

    else:
        msg.info(f"Creating {repo.name!r} at {repo.local_path}.")
        # Make an empty dir and git repo
        repo.local_path.mkdir(parents=True)
        if use_git:
            git.init(path=repo.local_path, check=True)


def create_virtualenv(repo: Repo, packages: List[str]) -> Environment:
    """
    Creates and returns new virtual environment with packages and reports
    to user.
    """

    msg.info(
        f"Creating virtual environment for {repo.name!r}",
        text=f"Including packages: {', '.join(packages)}",
        spaced=True,
    )
    env = Venv(project_path=repo.local_path)
    with msg.loading("Working..."):
        env.create(packages=packages)

    return env


def create_condaenv(repo: Repo, packages: List[str]) -> Environment:
    """
    Creates and returns new conda environment with packages and reports
    to user.
    """
    msg.info(
        f"Creating conda environment for {repo.name!r}",
        text=f"Including packages: {', '.join(packages)}",
        spaced=True,
    )
    env = Conda(name=repo.name, project_path=repo.local_path)
    try:
        with msg.loading("Working..."):
            env.create(packages=packages)
    except EnvironmentAlreadyExistsError:
        msg.warn(
            f"Conda environment {env.name!r} already exists!", spaced=True, exits=1
        )

    return env


def handle_http_status_errors(error: httpx.HTTPStatusError) -> None:
    """
    Handles a variety of possible HTTP Status errors, print's nicer output
    to the user, and exits the program if necessary.

    Call this in an except block on CLI commands accessing the
    GitHub API.

    Args:
        error (httpx.HTTPStatusError): The error to be handled.
    """
    code = error.response.status_code

    if code == 401:
        msg.fail(
            title="HTTP Error: 401 - Unauthorized",
            text="This usually means something is wrong with your token!",
            exits=1,
        )
    elif code == 404:
        msg.fail(
            title="HTTP Error: 404 - Not Found",
            text="This usually means something is up with the GitHub API.",
            exits=1,
        )
    elif code == 500:
        msg.fail(
            title="HTTP Error: 500 - Internal Server Error",
            text="This usually means GitHub is not happy.",
            exits=1,
        )
