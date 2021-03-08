"""
Abstract base class for all Virtual Environments

Author: Tom Fleet
Created: 07/03/2021
"""

import pathlib
from abc import ABC, abstractmethod
from typing import List


class BaseEnvironment(ABC):
    """
    Abstract Base Class providing an interface that
    all virtual environments must implement.
    """

    @property
    def project_path(self) -> pathlib.Path:
        """
        `.project_path` represents the root directory of the
        project associated to the virtual environment.
        """
        pass

    @property
    def executable(self) -> pathlib.Path:
        """
        `.executable` is the absolute path to the virtual environment's
        python interpreter e.g. "/Users/me/Development/project1/.venv/bin/python"
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        """
        `.exists()` checks whether the virtual environment
        exists. How it does this is up to the child class, but a
        good example would be simply checking if `self.executable` exists.
        """
        pass

    @abstractmethod
    def create(self) -> None:
        """
        Method to create the virtual environment. Note, no arguments
        are accepted for packages to install. This is the job of
        the `install` method.
        """
        pass

    @abstractmethod
    def install(
        self,
        packages: List[str],
    ) -> None:
        """
        Generic install method.

        Installs `packages` into the correct virtual environment.

        Args:
            packages (List[str]): List of valid packages to install.
        """
        pass
