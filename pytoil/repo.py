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
from typing import Optional

from .api import API
from .config import Config
from .exceptions import (
    APIRequestError,
    GitNotInstalledError,
    InvalidURLError,
    LocalRepoExistsError,
    RepoNotFoundError,
)

# Stupidly basic regex, I'm bad at these
REPO_REGEX = re.compile(r"https://github.com/[\w]*/[\w]*.git")


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
            owner (Optional[str], optional): The owner of the GitHub repo.
                Defaults to value `username` from config file.
            name (Optional[str], optional): The name of the GitHub repo.
                Defaults to None.
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
            raise InvalidURLError(f"The URL: {url} is not a valid GitHub repo URL.")
        else:
            owner = url.rsplit(".git")[0].split("/")[-2]
            name = url.rsplit(".git")[0].split("/")[-1]

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
        `self.name` exists under owner `self.owner`.

        Returns:
            bool: True if repo exists on GitHub, else False.
        """
        try:
            api = API()
            api.get_repo(repo=self.name)
        except APIRequestError as err:
            # Any non 200 response status
            if err.status_code == 404:
                # If specifically 404 not found
                # repo doesn't exist
                return False
            else:
                # Some other HTTP error
                raise
        else:
            return True

    def clone(self) -> pathlib.Path:
        """
        Invokes git in a subprocess to clone the repo
        represented by the instance.

        Raises:
            GitNotInstalledError: If 'git' not found on $PATH.
            LocalRepoExistsError: If repo already exists in configured
                projects_dir.
            RepoNotFoundError: If repo not found on GitHub.

        Returns:
            pathlib.Path: Path to cloned repo.
        """

        # Get the user config from file and validate
        config = Config.get()
        config.raise_if_unset()

        if not bool(shutil.which("git")):
            # Check if git is installed

            raise GitNotInstalledError(
                """'git' executable not installed or not found on $PATH.
        Check your git installation."""
            )
        elif self.exists_local():
            # Check if its already been cloned
            raise LocalRepoExistsError(
                f"""The repo {self.name} already exists at {self.path}.
        Cannot clone a repo that already exists."""
            )
        elif not self.exists_remote():
            # Check if the remote repo actually exists
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
                # If clone succeeded, set self.path and return
                self.path = config.projects_dir.joinpath(self.name)
                return self.path

    def fork(self) -> str:
        """
        Forks the repo described by the instance as long
        as the repo owner is not the current user.

        In order to fork, the user must specify class attribute `owner`
        as well as `name`.

        If the fork is successful, will return the URL of the user's
        new fork.

        i.e. if user forks "someoneelse/repo" the returned url will
        be: "https://github.com/theuser/repo.git"

        Raises:
            APIRequestError: If any HTTP error occurs during the fork.

        Returns:
            str: The URL of the user's new fork.
        """

        # Validate user config
        config = Config.get()
        config.raise_if_unset()

        api = API()

        try:
            api.fork_repo(owner=self.owner, name=self.name)
        except APIRequestError:
            raise
        else:
            # Return the URL of the users new fork
            return f"https://github.com/{config.username}/{self.name}.git"

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
