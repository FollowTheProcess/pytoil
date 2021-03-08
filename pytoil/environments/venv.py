"""
Module managing VirtualEnvs

Author: Tom Fleet
Created: 07/03/2021
"""

import pathlib
import subprocess
from typing import List

import virtualenv

from pytoil.environments import BaseEnvironment
from pytoil.exceptions import MissingInterpreterError, VirtualenvAlreadyExistsError


class VirtualEnv(BaseEnvironment):
    def __init__(self, project_path: pathlib.Path) -> None:
        """
        Representation of a virtualenv.

        A VirtualEnv's `.executable` property (also a pathlib.Path) points
        to the python executable of the newly created virtualenv. This
        executable may or may not exist, and the existence check is
        the primary means of checking whether or not this virtualenv
        exists.

        Note: It is important not to resolve `.executable` as it could
        resolve back to the system python if it is a symlink.

        Args:
            project_path (pathlib.Path): The root path of the current project.
        """
        self._project_path = project_path.resolve()

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(project_path={self._project_path!r})"

    @property
    def project_path(self) -> pathlib.Path:
        return self._project_path

    @property
    def executable(self) -> pathlib.Path:
        return self._project_path.joinpath(".venv/bin/python")

    def exists(self) -> bool:
        """
        Checks whether the virtual environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then both the project and virtual environment
        must also exist and must be valid.
        """
        return self.executable.exists()

    def create(self) -> None:
        """
        Create a new virtualenv in `project_path`.

        Raises:
            VirtualenvAlreadyExistsError: If virtualenv already exists
                in `project_path`.
        """
        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"""Virtualenv with path: {self.executable}
                already exists"""
            )
        else:
            # Create a new virtualenv under the project, called ".venv"
            virtualenv.cli_run([f"{self.project_path.joinpath('.venv')}"])

    def update_seeds(self) -> None:
        """
        VirtualEnv will install 'seed' packages to a new
        environment: `pip`, `setuptools` and `wheel`.

        It is good practice to keep these packages fully up to date
        this method does exactly that by invoking pip from
        the virtualenvs executable.

        This is equivalent to running:
        `python -m pip install --upgrade pip setuptools wheel`
        from the command line with the virtualenv activated.
        """

        # Validate the executable
        if not self.exists():
            raise MissingInterpreterError(f"Interpreter: {self.executable} not found.")

        try:
            # Don't need to specify a 'cwd' because we have a resolved interpreter
            subprocess.run(
                [
                    f"{str(self.executable)}",
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "pip",
                    "setuptools",
                    "wheel",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            raise

    def install(self, packages: List[str]) -> None:
        """
        Generic `pip install` method.

        Takes a list of packages to install. All packages are passed through
        to pip so any versioning syntax will work as expected.

        Args:
            packages (List[str]): A list of valid packages to install.
            Analogous to simply calling `pip install *packages` from within
            the virtualenv. If only 1 package, still must be in a list e.g. `["black"]`.
        """

        # If we get here, method has been called correctly
        # Ensure seed packages are updated, also checks interpreter
        self.update_seeds()

        cmd: List[str] = [f"{self.executable}", "-m", "pip", "install"]

        cmd.extend(packages)

        # Run the constructed pip command
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise
