"""
Module responsible for handling pytoil's programmatic
interaction with its config file.

Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import aiofiles
import tomlkit
from pydantic import BaseModel

from pytoil.config import defaults


class ConfigDict(TypedDict):
    """
    TypedDict for config.

    Exactly the same as the dataclass except projects_dir
    is a str here because that's how it will be brought in
    when deserialising the toml file.
    """

    projects_dir: str
    token: str
    username: str
    editor: str
    conda_bin: str
    common_packages: list[str]
    cache_timeout: int
    git: bool


class Config(BaseModel):
    projects_dir: Path = defaults.PROJECTS_DIR
    token: str = defaults.TOKEN
    username: str = defaults.USERNAME
    editor: str = defaults.EDITOR
    conda_bin: str = defaults.CONDA_BIN
    common_packages: list[str] = defaults.COMMON_PACKAGES
    cache_timeout: int = defaults.CACHE_TIMEOUT_SECS
    git: bool = defaults.GIT

    @classmethod
    async def load(cls, path: Path = defaults.CONFIG_FILE) -> Config:
        """
        Reads in the ~/.pytoil.toml config file and returns
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
                config_dict: ConfigDict = tomlkit.parse(content).get("pytoil", "")
        except FileNotFoundError:
            raise
        else:
            return Config(**config_dict)

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
            "editor": self.editor,
            "conda_bin": self.conda_bin,
            "common_packages": self.common_packages,
            "cache_timeout": self.cache_timeout,
            "git": self.git,
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
            content = tomlkit.dumps({"pytoil": self.to_dict()}, sort_keys=True)
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

    def specifies_editor(self) -> bool:
        """
        Returns whether the user has set an editor, either directly
        or through the $EDITOR env var.

        If a user has no `editor` key in the config file, pytoil will
        use $EDITOR.

        If the key is present but is set to the literal "None", pytoil
        will not try to open projects.

        Otherwise the value of the key `editor` will be used as the name
        of the binary.

        Returns:
            bool: True if editor is not literal "None" else False.
        """
        return self.editor.lower() != "none"
