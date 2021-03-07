"""
Module responsible for managing local and remote
repos (projects).

Author: Tom Fleet
Created: 05/02/2021
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
from datetime import datetime
from typing import Dict, Optional, Set, Union

from pytoil.api import API
from pytoil.config import Config
from pytoil.exceptions import (
    GitNotInstalledError,
    InvalidRepoPathError,
    InvalidURLError,
    LocalRepoExistsError,
    RepoNotFoundError,
)

# Stupidly basic regex, I'm bad at these
REPO_REGEX = re.compile(r"https://github.com/[\w]+/[\w]+.git")
REPO_PATH_REGEX = re.compile(r"[\w]+/[\w]+")


class Repo:
    def __init__(self, name: str, owner: Optional[str] = None) -> None:
        """
        Representation of a Git/GitHub repo.

        The GitHub url is constructed from `owner` and `name` and is accesible
        through the `.url` read-only property.

        If the repo has been cloned and/or exists locally, the `.path` property
        will be set to a pathlib.Path pointing to the root of the cloned repo.

        In this sense, the `Repo` object can represent both a remote GitHub
        repo and a local project.

        Args:
            name (str): The name of the GitHub repo.

            owner (Optional[str], optional): The owner of the GitHub repo.
                Defaults to value `username` from config file.
        """
        self.owner = owner or Config.get().username
        self.name = name

        self._url: str = f"https://github.com/{self.owner}/{self.name}.git"

        # The path this repo would have were it to be cloned locally
        self._path: pathlib.Path = Config.get().projects_dir.joinpath(self.name)

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__ + f"(owner={self.owner!r}, name={self.name!r})"
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @path.setter
    def path(self, value: pathlib.Path) -> None:
        self._path = value

    @classmethod
    def from_url(cls, url: str) -> Repo:
        """
        Constructs a Repo by extracting `owner` and `name`
        from a valid GitHub Repo URL.

        Args:
            url (str): Valid GitHub Repo URL.

        Raises:
            InvalidURLError: If URL does not match valid REGEX.

        Returns:
            Repo: Repo with `owner` and `name` set from `url`.
        """

        if not REPO_REGEX.match(url):
            raise InvalidURLError(f"The URL: {url!r} is not a valid GitHub repo URL.")
        else:
            owner = url.rsplit(".git")[0].split("/")[-2]
            name = url.rsplit(".git")[0].split("/")[-1]

            return cls(name=name, owner=owner)

    @classmethod
    def from_path(cls, path: str) -> Repo:
        """
        Constructs a Repo by extracting `owner` and `name`
        from a valid shorthand repo path.

        Args:
            path (str): Valid shorthand path
                e.g. 'FollowTheProcess/pytoil'

        Raises:
            InvalidRepoPathError: If path does match valid REGEX.

        Returns:
            Repo: Repo with `owner` and `name` set from `path`.
        """

        if not REPO_PATH_REGEX.match(path):
            raise InvalidRepoPathError(
                f"The repo path: {path!r} is not a valid GitHub repo path."
            )
        else:
            owner, name = path.split("/")

            return cls(name=name, owner=owner)

    def exists_local(self) -> bool:
        """
        Determines whether or not the repo exists
        locally in configured projects folder.

        Returns:
            bool: True if repo exists locally, else False.
        """
        return self.path.exists()

    def exists_remote(self) -> bool:
        """
        Determines whether or not the repo called
        `self.name` exists under configured username.

        Returns:
            bool: True if repo exists on GitHub, else False.
        """

        api = API()
        repos: Set[str] = set(api.get_repo_names())

        return self.name in repos

    def clone(self) -> None:
        """
        Invokes git in a subprocess to clone the repo
        represented by the instance.

        Raises:
            GitNotInstalledError: If 'git' not found on $PATH.
            LocalRepoExistsError: If repo already exists in configured
                projects_dir.
            RepoNotFoundError: If repo not found on GitHub.
        """

        # Get the user config from file and validate
        config = Config.get()
        config.validate()

        # Check if git is installed
        if not bool(shutil.which("git")):
            raise GitNotInstalledError(
                """'git' executable not installed or not found on $PATH.
        Check your git installation."""
            )
        # Check if its already been cloned
        elif self.exists_local():
            raise LocalRepoExistsError(
                f"""The repo {self.name} already exists at {self.path}.
        Cannot clone a repo that already exists."""
            )
        # Check if the remote repo actually exists
        elif not self.exists_remote():
            raise RepoNotFoundError(f"Repo: {self.url} not found on GitHub")
        else:
            # If we get here, we can safely clone
            try:
                subprocess.run(
                    ["git", "clone", f"{self.url}"], check=True, cwd=config.projects_dir
                )
            except subprocess.CalledProcessError:
                raise
            else:
                # If clone succeeded, set self.path
                self.path = config.projects_dir.joinpath(self.name)

    def info(self) -> Dict[str, Union[str, int, bool]]:
        """
        Returns summary information about the repo
        from the API or Path.stat.

        Prefers the API info as it is more detailed.
        Will fall back to Path.stat only if the project
        is not available remotely.

        Returns:
            Dict[str, Union[str, int]]: Summary info.
        """

        info_dict: Dict[str, Union[str, int, bool]] = {}

        # Path.stat returns a UNIX timestamp for dates/times
        str_time_format: str = r"%Y-%m-%d %H:%M:%S"

        if self.exists_remote():
            # If remote, the API does all the work
            api = API()
            info_dict.update(api.get_repo_info(repo=self.name))
            info_dict["remote"] = True
            info_dict["local"] = self.exists_local()
        elif self.exists_local():
            # If local, we can get a bit of info from os.stat
            info_dict.update(
                {
                    "name": self.path.name,
                    "created_at": datetime.utcfromtimestamp(
                        self.path.stat().st_ctime
                    ).strftime(str_time_format),
                    "updated_at": datetime.utcfromtimestamp(
                        self.path.stat().st_mtime
                    ).strftime(str_time_format),
                    "size": self.path.stat().st_size,
                    "local": True,
                    "remote": self.exists_remote(),
                },
            )
        else:
            raise RepoNotFoundError(
                f"Repo: {self.name!r} does not exist locally or remotely."
            )

        return info_dict

    def _does_file_exist(self, file: str) -> bool:
        """
        Helper method to determine whether or not a particular file
        exists in the root of the local repo.

        Args:
            file (str): Name of the file to check for.

        Raises:
            RepoNotFoundError: If the repo does not exist locally.

        Returns:
            bool: True if file exists, else False.
        """

        if not self.exists_local():
            raise RepoNotFoundError(f"Repo: {self.path!r} not found locally.")
        else:
            return self.path.joinpath(file).exists()

    def is_setuptools(self) -> bool:
        """
        Is the project based on setuptools.

        i.e. does it contain a `setup.py` or a `setup.cfg`

        Returns:
            bool: True if project is setuptools, else False.
        """

        return self._does_file_exist("setup.cfg") or self._does_file_exist("setup.py")

    def is_conda(self) -> bool:
        """
        Is the project based on conda.

        i.e. does it contain an `environment.yml`

        Returns:
            bool: True if project is conda, else False.
        """

        return self._does_file_exist("environment.yml")

    def is_editable(self) -> bool:
        """
        Does the project support `pip install -e .`

        Must have a `setup.py` for this, `setup.cfg` on its own
        is not sufficient.

        Returns:
            bool: True if project is editable, else False.
        """

        return self._does_file_exist("setup.py")

    def is_pep517(self) -> bool:
        """
        Does the project comply with PEP517/518.

        i.e. does it have a `pyproject.toml`

        Returns:
            bool: True if project supports PEP517, else False.
        """

        return self._does_file_exist("pyproject.toml")
