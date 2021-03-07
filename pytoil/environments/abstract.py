"""
Abstract base class for all Virtual Environments

Author: Tom Fleet
Created: 07/03/2021
"""

import pathlib
from abc import ABC, abstractmethod
from typing import List, Optional


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

    @project_path.setter
    def project_path(self, value: pathlib.Path) -> None:
        pass

    @property
    def executable(self) -> pathlib.Path:
        """
        `.executable` is the absolute path to the virtual environment's
        python interpreter e.g. "/Users/me/Development/project1/.venv/bin/python"
        """
        pass

    @executable.setter
    def executable(self, value: pathlib.Path) -> None:
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
        packages: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        file: Optional[str] = None,
        editable: bool = False,
    ) -> None:
        """
        Generic install method.

        In general, `CondaEnvs` will only require the `packages` argument.

        The others are for `VirtualEnv` and are mutually exclusive.

        If a list of packages is specified, the method is
        analagous to calling `pip install *packages` or `conda install *packages`
        from within the virtual environment. The packages are effectively passed
        straight through so any versioning syntax e.g. `>=3.2.6` will work as
        expected.

        If `packages` is specified, `prefix`, `editable` and `file`
        must be `None`.

        A prefix is the syntax used if a project has declared clusters of
        optionall dependencies as labelled groups e.g. `.[all]` or `.[dev]`
        in files like setup.py, pyproject.toml etc.

        If `prefix` is specified, `packages` and `file` must be `None` but editable
        may be specified.

        `file` is the string path of a valid requirements file relative
        to the project root.
        e.g. `requirements.txt` or `environment.yml`. The implementation
        of how to do this is of course, left to the child class.

        If `file` is specified, `packages`, `prefix` and `editable`
        must all be `None`.

        If `editable` is specified (only applicable on installs like `.[dev]`)
        this is analogous to calling `pip install -e {something}`.

        If `editable` is specified, `packages` and `file` must all be `None`.

        Args:
            packages (List[str], optional): List of valid packages to install.
                Defaults to None.

            prefix (str, optional): Valid prefix for a dependency cluster
                e.g. `.[dev]`. Defaults to None.

            file (str, optional): String path to a requirements file.
                Defaults to None.

            editable (bool, optional): Whether or not the project
                supports being installed in editable mode.
                Defaults to False.
        """
        pass
