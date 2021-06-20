"""
Module responsible for creating and managing
python virtual environments through the std lib `venv` module.

Author: Tom Fleet
Created: 20/06/2021
"""

import subprocess
import venv
from pathlib import Path
from typing import List, Optional

from pytoil.environments import Environment
from pytoil.exceptions import MissingInterpreterError


class Venv(Environment):
    def __init__(self, project_path: Path) -> None:
        """
        Representation of a virtualenv.

        A VirtualEnv's `.executable` property (also a Path) points
        to the python executable of the newly created virtualenv. This
        executable may or may not exist, and the existence check is
        the primary means of checking whether or not this virtualenv
        exists.

        Note: It is important not to resolve `.executable` as it could
        resolve back to the system python if it is a symlink.

        Args:
            project_root (Path): The root path of the current project.
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
        Create the virtual environment in the project.

        If packages are specified here, these will be installed
        once the environment is created.

        Args:
            packages (Optional[List[str]], optional): Packages to install immediately
                after environment creation. Defaults to None.
        """
        # `clear` will ensure any existing venv is destroyed first rather
        # than causing an error
        # TODO: `create()` has an `upgrade_deps` arg to do what `update_seeds` does but
        # it's only in python 3.9
        # Add this in later
        venv.create(
            env_dir=self.project_path.joinpath(".venv"), clear=True, with_pip=True
        )

        # Update core deps
        self.update_seeds()

        # Install any specified packages
        if packages:
            self.install(packages=packages)

    def update_seeds(self) -> None:
        """
        Venv will install 'seed' packages to a new
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
            # We don't need to specify a cwd here because `self.executable` is
            # an absolute path
            subprocess.run(
                [
                    f"{self.executable}",
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--quiet",
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
                the virtualenv. If only 1 package, still must be in a list e.g.
                `["black"]`.
        """

        cmd: List[str] = [f"{self.executable}", "-m", "pip", "install", "--quiet"]

        cmd.extend(packages)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise
