"""
Module responsible for handling poetry environments.

Here we take advantage of poetry's new `local` config setting
to enforce the virtual environment being in the project
without altering the user's base config.

Author: Tom Fleet
Created: 13/07/2021
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from pytoil.environments import Environment
from pytoil.exceptions import PoetryNotInstalledError


class PoetryEnv(Environment):
    """
    Poetry EnvManager class.
    """

    def __init__(self, project_path: Path) -> None:
        """
        Representation of a poetry managed virtual environment.

        Most of the work here is just passed through to
        poetry via a subprocess.

        Args:
            project_path (Path): The root path to the current project.
        """
        self._project_path = project_path.resolve()

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(project_path={self.project_path!r})"

    @property
    def project_path(self) -> Path:
        return self._project_path

    @property
    def executable(self) -> Path:
        return self._project_path.joinpath(".venv/bin/python")

    @property
    def info_name(self) -> str:
        return "poetry"

    def raise_for_poetry(self) -> None:
        """
        Helper method to check for the existence of poetry.

        Basically everything in this class relies on poetry being
        installed to function correctly that's why we need this
        method.

        Raises:
            PoetryNotInstalledError: If poetry not installed
        """
        if not bool(shutil.which("poetry")):
            raise PoetryNotInstalledError(
                "Poetry not installed. Cannot install poetry based project."
            )

    def enforce_local_config(self) -> None:
        """
        Ensures any changes to poetry's config such
        as storing the virtual environment in the project
        directory as we do here, do not propegate to the
        user's global poetry config.
        """
        self.raise_for_poetry()

        subprocess.run(
            ["poetry", "config", "virtualenvs.in-project", "true", "--local"],
            check=True,
            cwd=self.project_path,
        )

    def exists(self) -> bool:
        """
        Checks whether the virtual environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then both the project and virtual environment
        must also exist and must be valid.
        """
        return self.executable.exists()

    def create(self, packages: Optional[List[str]] = None) -> None:
        """
        This method is not implemented for poetry environments.

        Use install instead as with poetry, creation and installation
        are handled together.
        """
        raise NotImplementedError

    def install(self, packages: List[str]) -> None:
        """
        Calls `poetry add` under the hood to install
        packages into the environment.

        Args:
            packages (List[str]): List of packages to install.
        """
        self.enforce_local_config()
        subprocess.run(
            ["poetry", "add", *packages, "--quiet"], check=True, cwd=self.project_path
        )

    def install_self(self) -> None:
        """
        Calls `poetry install` under the hood to install the
        current package and all it's dependencies.
        """
        self.enforce_local_config()
        subprocess.run(
            ["poetry", "install", "--quiet"],
            check=True,
            cwd=self.project_path,
            capture_output=True,
        )
