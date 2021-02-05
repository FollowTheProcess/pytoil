"""
Module responsible for managing local and remote
repos (projects).

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib
from typing import Optional, Union


class Repo:
    def __init__(
        self,
        owner: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Representation of a Git/GitHub repo.

        The GitHub url is constructed from `owner` and `name` and is accesible
        through the `.url` read-only property.

        If the repo has been cloned and exists locally, the `.path` property
        will be set to a pathlib.Path pointing to the root of the cloned repo.

        If repo does not exist locally, `.path` is None.

        Args:
            owner (Optional[str], optional): The owner of the GitHub repo.
                Defaults to None.
            name (Optional[str], optional): The name of the GitHub repo.
                Defaults to None.
        """
        self.owner = owner
        self.name = name

        self._url: str = f"https://github.com/{owner}/{name}.git"
        self._path: Union[pathlib.Path, None] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__ + f"(owner={self.owner!r}, name={self.name!r})"
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def path(self) -> Union[pathlib.Path, None]:
        return self._path

    @path.setter
    def path(self, value: pathlib.Path) -> None:
        self._path = value

    def exists_local(self) -> bool:
        """
        Determines whether or not the repo exists
        locally in configured projects folder.

        Returns:
            bool: True if repo exists locally, else False.
        """
        if self.path:
            return self.path.exists()
        else:
            return False

    def exists_remote(self) -> bool:
        """
        Determines whether or not the repo exists
        in the owner's list of GitHub repos.

        Returns:
            bool: True if repo exists on GitHub, else False.
        """
        # Get token from config file
        pass
