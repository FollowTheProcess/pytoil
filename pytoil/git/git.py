"""
Module responsible for interacting with git via
subprocesses.

Author: Tom Fleet
Created: 19/06/2021
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from pytoil.config import defaults
from pytoil.exceptions import GitNotInstalledError


class Git:
    def __init__(self, git: Optional[str] = shutil.which("git")) -> None:
        self.git = git

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(git={self.git!r})"

    def raise_for_git(self) -> None:
        if not self.git:
            raise GitNotInstalledError(
                "'git' executable not found on $PATH. Is git installed?"
            )

    def run(
        self, *args: str, check: bool = True, cwd: Path = defaults.PROJECTS_DIR
    ) -> None:
        """
        Generic method to run `git` in a subprocess.

        Pass any args to git via *args.

        e.g. 'run("clone", "https://github.com/me/repo.git")'

        Args:
            check (bool, optional): Will raise a CalledProcessError if
                something goes wrong. Defaults to True.

            cwd (Path, optional): Working directory of the subprocess.
                Defaults to defaults.PROJECTS_DIR.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.raise_for_git()

        try:
            subprocess.run([f"{self.git}", *args], check=check, cwd=cwd)
        except subprocess.CalledProcessError:
            raise

    def clone(
        self, url: str, check: bool = True, cwd: Path = defaults.PROJECTS_DIR
    ) -> None:
        """
        Convenience wrapper around `self.run` to clone a repo.

        Args:
            url (str): The clone url of the repo.

            check (bool, optional): Raise CalledProcessError on failure.
                Defaults to True.

            cwd (Path, optional): Working directory of the subprocess.
                Defaults to defaults.PROJECTS_DIR.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.run("clone", url, check=check, cwd=cwd)

    def init(self, path: Path, check: bool = True) -> None:
        """
        Convenience wrapper around `self.run` to initialise a repo.

        Args:
            path (Path): Root of the project to initialise
                the repo in.

            check (bool, optional): Raise CalledProcessError on failure.
                Defaults to True.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.run("init", check=check, cwd=path)
