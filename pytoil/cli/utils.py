"""
Collection of useful abstractions and internal
methods to be called in various CLI commands.

Author: Tom Fleet
Created: 08/03/2021
"""


import pathlib
from typing import List, Optional, Set

from pytoil.api import API
from pytoil.environments import BaseEnvironment
from pytoil.environments.conda import CondaEnv
from pytoil.environments.venv import VirtualEnv
from pytoil.repo import Repo


def get_local_project_list(projects_dir: pathlib.Path) -> List[str]:
    """
    Returns a sorted list of local projects.

    Args:
        projects_dir (pathlib.Path): Result of Config.projects_dir.

    Returns:
        List[str]: Sorted list of local project names.
    """

    local_projects: List[str] = sorted(
        [
            f.name
            for f in projects_dir.iterdir()
            if f.is_dir() and not f.name.startswith(".")
        ],
        key=str.casefold,
    )

    return local_projects


def get_local_project_set(projects_dir: pathlib.Path) -> Set[str]:
    """
    Returns a set of local project names.

    Args:
        projects_dir (pathlib.Path): Result of Config.projects_dir.

    Returns:
        Set[str]: Set of local project names.
    """

    local_projects: Set[str] = {
        f.name
        for f in projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    return local_projects


def get_remote_project_list(api: API) -> List[str]:
    """
    Returns a sorted list of remote projects.

    Args:
        projects_dir (pathlib.Path): Result of Config.projects_dir.

    Returns:
        List[str]: Sorted list of remote project names.
    """

    remote_projects: List[str] = sorted(api.get_repo_names(), key=str.casefold)

    return remote_projects


def get_remote_project_set(api: API) -> Set[str]:
    """
    Returns a set of remote projects.

    Args:
        projects_dir (pathlib.Path): Result of Config.projects_dir.

    Returns:
        List[str]: Set of remote project names.
    """

    remote_projects: Set[str] = set(api.get_repo_names())

    return remote_projects


def env_dispatcher(repo: Repo) -> Optional[BaseEnvironment]:
    """
    Takes in a `Repo` and returns the correct environment
    object for that Repo. Or `None` if it cannot
    detect the environment.

    Therefore all usage should first check for `None`

    Args:
        repo (Repo): Input Repo

    Returns:
        Optional[BaseEnvironment]: Either the correct environment
            object if it was able to detect. Or None.
    """

    if repo.is_conda():
        return CondaEnv(name=repo.name, project_path=repo.path)
    elif repo.is_setuptools():
        return VirtualEnv(project_path=repo.path)
    else:
        return None
