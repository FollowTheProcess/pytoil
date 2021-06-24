"""
Abstract base class for all starter templates.

These templates are not supposed to be exhaustive, for that
the user is better off using pytoil's cookiecutter functionality.

The templates defined in the `starters` module are exactly that,
a starter. A good reference would be the behaviour of `cargo new`
in rust, which simply set's up a few basic sub directories
and a "hello world" function in main.rs.

Author: Tom Fleet
Created: 23/06/2021
"""


from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class BaseStarter(ABC):
    """
    Abstract base class defining the interface that all
    starter templates musti implement.
    """

    @property
    def path(self) -> Path:
        """
        `path` is the path on the filesystem under which to
        generate the template.

        e.g. config.projects_dir
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        `name` is the name of the project, i.e. the name of the
        directory under `path` in which all the template's files
        and subdirectories should be created.

        e.g. projects_dir/name
        """
        raise NotImplementedError

    @property
    def root(self) -> Path:
        """
        The joined pathlib.Path of the project root.
        """

    @property
    def files(self) -> List[Path]:
        """
        Returns list of joined filepaths
        to be created.

        e.g. self.root.joinpath(filename)
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, username: Optional[str] = None) -> None:
        """
        Implements the generation of the project starter template.

        How it does this is up to the child class, it may directly
        instantiate files and directories using python, or call
        to external tools such as cargo, npm or go.
        """
        raise NotImplementedError
