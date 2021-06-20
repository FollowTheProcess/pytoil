"""
ABC around the `Git` class.

Particularly useful for testing where we can just create a `FakeGit` object
that satisfies this ABC and python will treat it the same way.

This way we don't have to mock the crap out of everything.

Author: Tom Fleet
Created: 19/06/2021
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseGit(ABC):
    @abstractmethod
    def raise_for_git(self) -> None:
        """
        Raises if `git` not installed.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, *args: str, check: bool, cwd: Path) -> Optional[str]:
        """
        Method to run git in a subprocess.
        """
        raise NotImplementedError

    @abstractmethod
    def clone(self, url: str, check: bool, cwd: Path) -> Optional[str]:
        """
        Wrapper around run to clone a repo.
        """
        raise NotImplementedError

    @abstractmethod
    def init(self, path: Path, check: bool) -> Optional[str]:
        """
        Wrapper around run to initialise an empty
        git repo.
        """
        raise NotImplementedError
