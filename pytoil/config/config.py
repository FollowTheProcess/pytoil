"""
Module responsible for handling user config.

Author: Tom Fleet
Created: 05/02/2021
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import TypedDict

import yaml

from pytoil.exceptions import InvalidConfigError

# Default value for projects_dir
DEFAULT_PROJECTS_DIR = pathlib.Path.home().joinpath("Development").resolve()
# Default config path location
CONFIG_PATH = pathlib.Path.home().joinpath(".pytoil.yml").resolve()


class ConfigDict(TypedDict):
    """
    Type checking for the config dictionary.

    Effectively a config schema, same as the dataclass
    with the exception of pathlib.Paths which are here
    represented as a string as this is how they will be
    stored in the config file and thus how they will be brought
    into python by pyyaml.
    """

    username: str
    token: str
    projects_dir: str
    vscode: bool


@dataclass
class Config:
    """
    Representation of the pytoil config.

    Only real usage is the `.get` classmethod.
    Used as the global configuration management class for the
    whole project.


    Args:
        username (str): Users GitHub username.
            Defaults to "UNSET".
        token (str): Users GitHub personal access token.
            Defaults to "UNSET".
        projects_dir (pathlib.Path): Directory in which user stores
            their development projects. Defaults to ~/Development.
        vscode (bool): Whether or not the user uses vscode as their editor.
            Defaults to False.
    """

    username: str = "UNSET"
    token: str = "UNSET"
    projects_dir: pathlib.Path = DEFAULT_PROJECTS_DIR
    vscode: bool = False

    def validate(self) -> None:
        """
        Helper method to validate the config.

        If either `username` or `token` are the fallback value
        "UNSET" this will raise an InvalidConfigError.

        Call before anything where these are required.
        """

        if self.username == "UNSET":
            raise InvalidConfigError(
                """No GitHub username set in ~/.pytoil.yml.
        Please set your GitHub username in the config file with the key: `username`."""
            )
        elif self.token == "UNSET":
            raise InvalidConfigError(
                """No GitHub personal access token set in ~/.pytoil.yml.
        Please set your GitHub personal access token in the config file with
        the key: `token`."""
            )
        else:
            return None

    @classmethod
    def get(cls) -> Config:
        """
        Fetches the configuration from the ~/.pytoil.yml config
        file and returns a Config object with parameters set from
        the file.

        If a key is not present in the file, or if the value associated to
        that key is blank. The default value for that key will be used.

        If the file does not exist, a FileNotFoundError will be raised.

        Raises:
            FileNotFoundError: If config file `~/.pytoil.yml` does not exist.

        Returns:
            Config: Config object with parameters parsed from the file.
        """

        try:
            with open(CONFIG_PATH, mode="r", encoding="utf-8") as f:
                config_dict = yaml.full_load(f)
        except FileNotFoundError:
            raise
        else:
            # Get the config from unpacking the dict
            config = Config(
                username=config_dict.get("username") or "UNSET",
                token=config_dict.get("token") or "UNSET",
                projects_dir=pathlib.Path(config_dict.get("projects_dir"))
                or DEFAULT_PROJECTS_DIR,
                vscode=config_dict.get("vscode") or False,
            )

            return config

    def to_dict(self) -> ConfigDict:
        """
        Generates a properly formatted dictionary of the current
        config.

        Returns:
            ConfigDict: Dictionary showing the current config state.
        """

        config_dict: ConfigDict = {
            "username": self.username,
            "token": self.token,
            "projects_dir": str(self.projects_dir),
            "vscode": self.vscode,
        }

        return config_dict

    def show(self) -> None:
        """
        Pretty prints the current config.
        """

        for key, val in self.to_dict().items():
            print(f"{key}: {val!r}")

    def write(self) -> None:
        """
        Overwrites the config file with the attributes
        from the calling instance.
        """

        config_dict = self.to_dict()

        with open(CONFIG_PATH, mode="w", encoding="utf-8") as f:
            yaml.dump(config_dict, f)
