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
    """
    Wrapper around the user installed `git`.
    """

    def __init__(self, git: Optional[str] = shutil.which("git")) -> None:
        """
        A handy wrapper around the user installed `git`.

        Args:
            git (Optional[str], optional): The path to the `git` binary
                primarily used for separation of concerns during testing.
                Defaults to shutil.which("git").
        """
        self.git = git

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(git={self.git!r})"

    def raise_for_git(self) -> None:
        """
        Raises an exception if the user does not have
        git installed.
        """
        if not self.git:
            raise GitNotInstalledError(
                "'git' executable not found on $PATH. Is git installed?"
            )

    def run(
        self,
        *args: str,
        check: bool = True,
        cwd: Path = defaults.PROJECTS_DIR,
        silent: bool = False,
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

            silent (bool): Whether to suppress showing the clone output.
                Defaults to False.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.raise_for_git()

        try:
            subprocess.run(
                [f"{self.git}", *args], check=check, cwd=cwd, capture_output=silent
            )
        except subprocess.CalledProcessError:
            raise

    def clone(
        self,
        url: str,
        check: bool = True,
        cwd: Path = defaults.PROJECTS_DIR,
        silent: bool = True,
    ) -> None:
        """
        Convenience wrapper around `self.run` to clone a repo.

        Args:
            url (str): The clone url of the repo.

            check (bool, optional): Raise CalledProcessError on failure.
                Defaults to True.

            cwd (Path, optional): Working directory of the subprocess.
                Defaults to defaults.PROJECTS_DIR.

            silent (bool): Whether to suppress showing the clone output.
                Defaults to True.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.run("clone", url, check=check, cwd=cwd, silent=silent)

    def init(self, path: Path, check: bool = True, silent: bool = False) -> None:
        """
        Convenience wrapper around `self.run` to initialise a repo.

        Args:
            path (Path): Root of the project to initialise
                the repo in.

            check (bool, optional): Raise CalledProcessError on failure.
                Defaults to True.

            silent (bool): Whether to suppress showing the clone output.
                Defaults to False.

        Raises:
            subprocess.CalledProcessError: If the subprocess command fails.
        """

        self.run("init", check=check, cwd=path, silent=silent)

    def set_upstream(
        self,
        owner: str,
        repo: str,
        path: Path,
        check: bool = True,
        silent: bool = False,
    ) -> None:
        """
        Sets the upstream repo for a local repo, e.g. on a cloned fork.

        Note difference between origin and upstream, origin of a cloned fork
        would be user/forked_repo where as upstream would be
        original_user/forked_repo.

        Args:
            owner (str): Owner of the upstream repo.
            repo (str): Name of the upstream repo.
            path (Path): Root of the project where the local git
                repo is.
            check (bool, optional): Raise CalledProcessError on failure.
                Defaults to True.
            silent (bool): Whether to suppress showing the clone output.
            Defaults to True.
        """
        base_url = "https://github.com"
        constructed_upstream = f"{base_url}/{owner}/{repo}.git"
        self.run(
            "remote",
            "add",
            "upstream",
            constructed_upstream,
            check=check,
            cwd=path,
            silent=silent,
        )
