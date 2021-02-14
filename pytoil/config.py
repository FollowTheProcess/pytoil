"""
Module responsible for handling user config.

Author: Tom Fleet
Created: 05/02/2021
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Dict

import yaml

# Default value for projects_dir
DEFAULT_PROJECTS_DIR = pathlib.Path.home().joinpath("Development")
# Default config path location
CONFIG_PATH = pathlib.Path.home().joinpath(".pytoil.yml")


class Config:
    def __init__(
        self,
        username: str = "UNSET",
        token: str = "UNSET",
        projects_dir: str = "UNSET",
    ) -> None:
        """
        Representation of the pytoil config.

        Only real usage is the `.get` classmethod.
        Used as the global configuration management class for the
        whole project.

        Arguments are passed in as str and every parameter
        other than `projects_dir` retains this type.

        `projects_dir` however will return a pathlib.Path instance of the str
        path passed in. This is accessible through the `.projects_dir` property.

        This is so that the class can be instantiated by parsing the config file
        but then what the `projects_dir` attribute is accessed, it is converted
        to a pathlib.Path for OS independent pathing.

        This means that so long as the user enters the absolute path as a string
        in the config file, this will all work regardless of OS.

        Args:
            username (str): Users GitHub username.
                Defaults to "UNSET".
            token (str): Users GitHub personal access token.
                Defaults to "UNSET".
            projects_dir (str): Directory in which user stores
                their development projects. Defaults to "UNSET".
        """
        self._username = username
        self._token = token
        self._projects_dir = projects_dir

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(username={self._username!r}, "
            + f"token={self._token!r}, "
            + f"projects_dir={self._projects_dir!r})"
        )

    # Ref: https://github.com/python/mypy/issues/6523
    if TYPE_CHECKING:  # pragma: no cover
        __dict__ = {}  # type: Dict[str, str]
    else:

        @property
        def __dict__(self) -> Dict[str, str]:

            return {
                "username": self.username,
                "token": self.token,
                "projects_dir": str(self.projects_dir),
            }

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    @property
    def projects_dir(self) -> pathlib.Path:
        """
        Primary accessor for the `projects_dir` property.
        If the key is populated in the config file, this will
        return the pathlib.Path instance generated from that str
        for OS-independent pathing.

        Returns:
            (pathlib.Path): Path to the projects directory if passed,
                else ~/Development.
        """
        if self._projects_dir == "UNSET":
            return DEFAULT_PROJECTS_DIR
        else:
            return pathlib.Path(self._projects_dir)

    @projects_dir.setter
    def projects_dir(self, value: str) -> None:
        """
        Setter for the `projects_dir` property.

        Pass a string just as you would for the instantiation of
        the class.

        It is converted to a pathlib.Path on retrieval using the
        `.projects_dir` property.

        Args:
            value (str): String representation of the path to change to.
        """
        self._projects_dir = value

    @classmethod
    def get(cls) -> Config:
        """
        Fetches the configuration from the ~/.pytoil.yml config
        file and returns a Config object with parameters set from
        the file.

        If a key is not present in the file, or if the value associated to
        that key is blank. The default value for that key will be used.

        If the file does not exist, a FileNotFoundError will be raised.

        If a key is misspelled in the file a TypeError will be raised
        pointing to the bad parameter.

        Raises:
            FileNotFoundError: If config file `~/.pytoil.yml` does not exist.
            TypeError: If any of the keys in the config file are misspelled
                or there are additional keys.

        Returns:
            Config: Config object with parameters parsed from the file.
        """
        # Doing it this way makes CONFIG_PATH easily patched out during tests
        fp = CONFIG_PATH

        try:
            with open(fp) as f:
                config_dict: Dict[str, str] = yaml.full_load(f)
        except FileNotFoundError:
            raise
        else:
            try:
                # Get the config from unpacking the dict
                config = Config(**config_dict)
            except TypeError:
                # If one of the keys is wrong
                raise
            else:
                return config

    def to_dict(self) -> Dict[str, str]:
        """
        Generates a properly formatted dictionary of the current
        config.

        Returns:
            Dict[str, Optional[str]]: Dictionary showing the current config state.
        """

        return self.__dict__
