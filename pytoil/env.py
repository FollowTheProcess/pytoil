"""
Module responsible for the creation and management
of virtualenvs.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib
import subprocess
from typing import Optional, Union

import virtualenv

from .exceptions import (
    MissingInterpreterError,
    TargetDirDoesNotExistError,
    VirtualenvAlreadyExistsError,
)


class VirtualEnv:
    def __init__(self, basepath: pathlib.Path, name: str = ".venv") -> None:
        """
        Representation of a virtualenv.

        The path to the virtualenv directory is accessible through the
        `.path` property which returns a pathlib.Path pointing to the
        virtualenv directory.

        Once the instantiated virtualenv has been created, its `.executable`
        property (also a pathlib.Path) will point to the python executable
        of the newly created virtualenv.

        Until creation, the instantiated virtualenv's `.executable` is None.

        Args:
            basepath (pathlib.Path): The root path of the current project.
            name (str, optional): The name of the virtualenv directory.
                Defaults to ".venv".
        """
        self.basepath = basepath
        self.name = name
        self._path: pathlib.Path = self.basepath.joinpath(self.name)
        self._executable: Optional[pathlib.Path] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(basepath={self.basepath!r}, name={self.name!r})"
        )

    @property
    def path(self) -> pathlib.Path:
        """
        The path of the virtualenv folder.
        i.e the joined rootdir and name.
        """
        return self._path

    @property
    def executable(self) -> Union[pathlib.Path, None]:
        """
        The path to the virtualenv's python executable.
        """
        return self._executable

    @executable.setter
    def executable(self, value: pathlib.Path) -> None:
        self._executable = value

    def basepath_exists(self) -> bool:
        return self.basepath.exists()

    def exists(self) -> bool:
        return self.path.exists()

    def raise_for_executable(self) -> None:
        """
        Helper method analagous to requests 'raise_for_status'.

        A virtualenvs executable is only created if all the checks in
        `.create()` pass.

        This method is a convenient way of checking all those conditions
        by proxy in one step. If the property `self.executable` is not None,
        then the executable is valid.

        Raises:
            MissingInterpreterError: If `self.executable` is not found.
        """

        if not self.executable:
            raise MissingInterpreterError(
                f"""Virtualenv: {self.path!r} does not exist. Cannot install
                until it has been created. Create by using the `.create()` method."""
            )
        else:
            return None

    def create(self) -> None:
        """
        Create a new virtualenv in `basepath` with `name`
        and update the `executable` property with the newly
        created virtualenv's python.

        Raises:
            VirtualenvAlreadyExistsError: If virtualenv with `path` already exists.
            TargetDirDoesNotExistError: If basepath does not exist.
        """
        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"Virtualenv with path: {self.path!r} already exists"
            )
        elif not self.basepath_exists():
            raise TargetDirDoesNotExistError(
                f"The directory: {self.basepath!r} does not exist."
            )
        else:
            # Create a new virtualenv at `path`
            virtualenv.cli_run([f"{self.path}"])
            # Update the instance executable with the newly created one
            # resolve so can be safely invoked later
            self.executable = self.path.joinpath("bin/python").resolve()

    def update_seeds(self) -> None:
        """
        VirtualEnv will install 'seed' packages to a new
        environment: 'pip', 'setuptools' and 'wheel'.

        It is good practice to keep these packages fully up to date
        this method does exactly that by invoking pip from
        the virtualenvs executable.

        This is equivalent to running:
        'python -m pip install --upgrade pip setuptools wheel'
        from the command line with the virtualenv activated.
        """

        # Validate the executable
        self.raise_for_executable()

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
