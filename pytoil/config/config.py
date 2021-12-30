"""
Module responsible for handling pytoil's programmatic
interaction with its config file.

Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

from dataclasses import field
from pathlib import Path
from typing import List, TypedDict

import aiofiles
import yaml
from pydantic.dataclasses import dataclass

from pytoil.config import defaults


class ConfigDict(TypedDict):
    """
    TypedDict for config.

    Exactly the same as the dataclass except projects_dir
    is a str here because that's how it will be brought in
    when deserialising the yaml file.
    """

    projects_dir: str
    token: str
    username: str
    vscode: bool
    code_bin: str
    common_packages: List[str]
    init_on_new: bool


@dataclass
class Config:
    """
    Pydantic dataclass representing pytoil's config.

    Args:
        projects_dir (Path): Where the user keeps their development
            projects.

        token (str): The user's GitHub OAUTH personal access token.

        username (str): User's GitHub username.

        vscode (bool): Whether or not the user wants pytoil to use VSCode
            to auto-open projects.

        code_bin (str): The name of the VSCode binary ("code" | "code-insiders")

        common_packages (List[str]): List of common packages the user wants to
            inject into every python environment pytoil creates. Typically
            used for linters, formatters etc.

        init_on_new (bool): Whether or not the user wants pytoil to
            initialise a new git repo when creating a new local project.
    """

    projects_dir: Path = defaults.PROJECTS_DIR
    token: str = defaults.TOKEN
    username: str = defaults.USERNAME
    vscode: bool = defaults.VSCODE
    code_bin: str = defaults.CODE_BIN
    common_packages: List[str] = field(default_factory=list)
    init_on_new: bool = defaults.INIT_ON_NEW

    @classmethod
    async def from_file(cls, path: Path = defaults.CONFIG_FILE) -> Config:
        """
        Reads in the .pytoil.yml config file and returns
        a populated `Config` object.

        Args:
            path (Path, optional): Path to the config file.
                Defaults to defaults.CONFIG_FILE.

        Returns:
            Config: Populated `Config` object.

        Raises:
            FileNotFoundError: If config file not found.
        """
        try:
            async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                config_dict: ConfigDict = yaml.full_load(content)
        except FileNotFoundError:
            raise
        else:
            return Config.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: ConfigDict) -> Config:
        """
        Takes in a `ConfigDict` and returns a populated
        `Config` object.

        Args:
            config_dict (ConfigDict): Populated `ConfigDict` object.

        Returns:
            Config: Returned `Config`.
        """
        # We can do this here because pydantic will handle
        # all the conversion between types under the hood
        return Config(**config_dict)  # type: ignore

    @classmethod
    def helper(cls) -> Config:
        """
        Returns a friendly placeholder object designed to be
        written to a config file as a guide to the user on what
        to fill in.

        Most of the fields will be the default but some will have
        helpful instructions.

        Returns:
            Config: Helper config object.
        """
        # Typed ignored here because we know we're correct, mypy doesn't like this
        # probably something to do with Config being a pydantic model
        # not a pure python class
        return Config(
            token="Put your GitHub personal access token here",
            username="This your GitHub username",
        )

    def to_dict(self) -> ConfigDict:
        """
        Writes out the attributes from the calling instance
        to a dictionary.
        """
        return {
            "projects_dir": str(self.projects_dir),
            "token": self.token,
            "username": self.username,
            "vscode": self.vscode,
            "code_bin": self.code_bin,
            "common_packages": self.common_packages,
            "init_on_new": self.init_on_new,
        }

    async def write(self, path: Path = defaults.CONFIG_FILE) -> None:
        """
        Overwrites the config file at `path` with the attributes from
        the calling instance.

        Args:
            path (Path, optional): Config file to overwrite.
                Defaults to defaults.CONFIG_FILE.
        """
        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            content = yaml.dump(self.to_dict())
            await f.write(content)

    def can_use_api(self) -> bool:
        """
        Helper method to easily determine whether or not
        the config instance has the required elements
        to use the GitHub API.

        Returns:
            bool: True if can use API, else False.
        """
        conditions = [
            self.username == "",
            self.username == "This your GitHub username",
            self.token == "",
            self.token == "Put your GitHub personal access token here",
        ]

        return not any(conditions)
