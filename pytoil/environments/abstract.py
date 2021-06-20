"""
ABC that all virtual environment classes must
satisfy.

Author: Tom Fleet
Created: 19/06/2021
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class Environment(ABC):
    """
    Abstract Base Class providing an interface that
    all virtual environments must implement.
    """

    @property
    def project_path(self) -> Path:
        """
        `.project_path` represents the root directory of the
        project associated to the virtual environment.
        """
        raise NotImplementedError

    @property
    def executable(self) -> Path:
        """
        `.executable` is the absolute path to the virtual environment's
        python interpreter e.g. "/Users/me/Development/project1/.venv/bin/python"
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self) -> bool:
        """
        `.exists()` checks whether the virtual environment
        exists. How it does this is up to the child class, but a
        good example would be simply checking if `self.executable` exists.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, packages: Optional[List[str]] = None) -> None:
        """
        Method to create the virtual environment. If packages are specified
        these can be installed during environment creation.
        """
        raise NotImplementedError

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
        raise NotImplementedError
