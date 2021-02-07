"""
Module responsible for managing local and remote
repos (projects).

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib
import shutil
import subprocess
import urllib.error
from typing import Optional, Union

from .api import API
from .config import Config
from .exceptions import GitNotInstalledError, LocalRepoExistsError


class Repo:
    def __init__(
        self,
        name: str,
        owner: Optional[str] = None,
    ) -> None:
        """
        Representation of a Git/GitHub repo.

        The GitHub url is constructed from `owner` and `name` and is accesible
        through the `.url` read-only property.

        If the repo has been cloned and exists locally, the `.path` property
        will be set to a pathlib.Path pointing to the root of the cloned repo.

        Args:
            owner (Optional[str], optional): The owner of the GitHub repo.
                Defaults to value `username` from config file.
            name (Optional[str], optional): The name of the GitHub repo.
                Defaults to None.
        """
        self.owner = owner or Config.get().username
        self.name = name

        self._url: str = f"https://github.com/{self.owner}/{self.name}.git"
        self._path: Union[pathlib.Path, None] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__ + f"(owner={self.owner!r}, name={self.name!r})"
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def path(self) -> Union[pathlib.Path, None]:
        return self._path

    @path.setter
    def path(self, value: pathlib.Path) -> None:
        self._path = value

    def exists_local(self) -> bool:
        """
        Determines whether or not the repo exists
        locally in configured projects folder.

        Returns:
            bool: True if repo exists locally, else False.
        """
        if self.path:
            return self.path.exists()
        else:
            return False

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
        except urllib.error.HTTPError as err:
            # Any HTTPError
            if err.code == 404:
                # If specifically 404 not found
                # repo doesn't exist
                return False
            else:
                # Some other HTTP error
                raise
        else:
            return True

    def clone(self) -> pathlib.Path:
        # Clone the repo 'owner'/'name' to a local folder
        # also called 'name' located in user configured
        # projects_dir
        # return pathlib.Path to root of the cloned repo
        # set self.path to this path

        config = Config.get()

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
