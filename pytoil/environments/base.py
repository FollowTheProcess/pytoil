"""
Interface that all virtual environment classes must
satisfy.


Author: Tom Fleet
Created: 24/12/2021
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence


class Environment(Protocol):
    @property
    def project_path(self) -> Path:
        """
        `.project_path` represents the root directory of the
        project associated with the virtual environment.
        """
        ...

    @property
    def executable(self) -> Path:
        """
        `.executable` is the absolute path to the virtual environment's
        python interpreter.
        """
        ...

    @property
    def name(self) -> str:
        """
        Returns the type of environment implemented by the concrete instance.
        Used for logging and debugging

        Returns:
            str: E.g. 'conda', 'venv', 'poetry' etc.
        """
        ...

    async def exists(self) -> bool:
        """
        `.exists()` checks whether the virtual environment exists.
        How it does this is up to the concrete implementation, but a good
        example might be simply checking if `self.executable` exists.
        """
        ...

    async def create(
        self, packages: Sequence[str] | None = None, silent: bool = False
    ) -> None:
        """
        Method to create the virtual environment. If packages are specified,
        these can be installed during environment creation.
        """
        ...

    async def install(self, packages: Sequence[str], silent: bool = False) -> None:
        """
        Generic install method.

        Installs `packages` into the correct virtual environment.

        Args:
            packages (List[str]): List of valid packages to install.
            silent (bool, optional): Whether to discard or display output.
        """
        ...

    async def install_self(self, silent: bool = False) -> None:
        """
        Installs the current project.

        For example: `pip install -e .[dev]` or `poetry install`
        """
        ...
