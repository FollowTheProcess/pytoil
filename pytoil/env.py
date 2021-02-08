"""
Module responsible for the creation and management
of virtualenvs.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib
from typing import Optional, Union

import virtualenv

from .exceptions import TargetDirDoesNotExistError, VirtualenvAlreadyExistsError


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

    def create(self) -> None:
        """
        Create a new virtualenv in `basepath` with `name`
        and update the `executable` property with the newly
        created virtualenv's python.

        Raises:
            VirtualenvAlreadyExistsError: If virtualenv with `path` already exists.
        """
        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"Virtualenv with path: {self.path} already exists"
            )
        elif not self.basepath_exists():
            raise TargetDirDoesNotExistError(
                f"The directory: {self.basepath} does not exist."
            )
        else:
            # Create a new virtualenv at `path`
            virtualenv.cli_run([f"{self.path}"])
            # Update the instance executable with the newly created one
            self.executable = self.path.joinpath("bin/python")
