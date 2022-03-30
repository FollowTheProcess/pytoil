"""
Module responsible for interacting with local/remote projects.


Author: Tom Fleet
Created: 22/12/2021
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os
import humanize
import tomlkit

from pytoil.api import API
from pytoil.config import Config
from pytoil.environments import Conda, Environment, Flit, Poetry, Requirements, Venv
from pytoil.exceptions import RepoNotFoundError


class Repo:
    def __init__(self, owner: str, name: str, local_path: Path) -> None:
        """
        Representation of a local/remote project.

        Args:
            owner (str): The owner (i.e. GitHub username)
            name (str): Project name.
            local_path (Path): The path this repo would have on the
                local filesystem, whether it currently exists or not.
        """
        self.owner = owner
        self.name = name
        self.local_path = local_path

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(owner={self.owner!r}, name={self.name!r},"
            f" local_path={self.local_path!r})"
        )

    __slots__ = ("owner", "name", "local_path")

    @property
    def clone_url(self) -> str:
        """
        The url to feed to `git clone` in order to
        clone this repo.
        """
        return f"https://github.com/{self.owner}/{self.name}.git"

    @property
    def html_url(self) -> str:
        """
        The url to the homepage of this repo.
        """
        return f"https://github.com/{self.owner}/{self.name}"

    @property
    def issues_url(self) -> str:
        """
        The url to the issues page of this repo.
        """
        return f"{self.html_url}/issues"

    @property
    def pulls_url(self) -> str:
        """
        The url to the pull requests page of this repo.
        """
        return f"{self.html_url}/pulls"

    async def exists_local(self) -> bool:
        """
        Determines whether or not a `Repo` exists
        on the local filesystem.

        Returns:
            bool: True if exists locally, else False.
        """
        return await aiofiles.os.path.exists(self.local_path)

    async def exists_remote(self, api: API) -> bool:
        """
        Determines whether or not a `Repo` exists
        on GitHub.

        Args:
            api (API): The API object.

        Returns:
            bool: True if exists remote, else False.
        """
        return await api.check_repo_exists(self.name)

    async def _local_info(self) -> dict[str, Any] | None:  # pragma: no cover
        """
        Return local path information for the repo.
        """
        # Mostly just pathlib stuff here, not much point in us testing it
        # and doing so is a pain because we have to freeze time on the filesystem and in the test
        # if pathlib doesn't work we have bigger problems anyway
        try:
            return {
                "Name": self.local_path.name,
                "Created": humanize.naturaltime(
                    datetime.utcfromtimestamp(self.local_path.stat().st_birthtime)  # type: ignore
                ),
                "Updated": humanize.naturaltime(
                    datetime.utcfromtimestamp(self.local_path.stat().st_mtime)
                ),
                "Local": True,
            }
        except FileNotFoundError:
            return None

    async def _remote_info(self, api: API) -> dict[str, Any] | None:
        """
        Return remote API information for the repo.
        """
        return await api.get_repo_info(self.name)

    async def info(self, api: API) -> dict[str, Any]:
        """
        Return summary info about the repo in question.

        Prefers the API info as it is possible to get
        things like license and description.

        If local only will fall back to path.stat.

        Args:
            api (API): The API dependency.

        Raises:
            RepoNotFoundError: If repo not local or remote.

        Returns:
            Dict[str, Any]: Repository information.
        """
        info: dict[str, Any] = {}
        exists_remote, remote_info, exists_local, local_info = await asyncio.gather(
            self.exists_remote(api=api),
            self._remote_info(api=api),
            self.exists_local(),
            self._local_info(),
        )

        if exists_remote:
            if remote_info:
                info.update(remote_info)
            # Might also exist locally
            info.update({"Local": exists_local})
        elif exists_local:
            if local_info:
                info.update(local_info)
            # We know it doesn't exist on GitHub if we got here
            info.update({"Remote": False})
        else:
            raise RepoNotFoundError(
                f"Repo: {self.name!r} does not exist locally or on GitHub."
            )

        return info

    async def _file_exists(self, file: str) -> bool:
        """
        Convenience method to determine whether or not
        the repo root directory contains `file`.

        Args:
            file (str): Name of the file.

        Returns:
            bool: True if exists, else False.
        """
        return await aiofiles.os.path.exists(self.local_path.joinpath(file))

    async def is_setuptools(self) -> bool:
        """
        Is the project based on setuptools, i.e. does it
        have a `setup.cfg` or `setup.py`

        Returns:
            bool: True if setuptools, else False.
        """
        exists = await asyncio.gather(
            self._file_exists("setup.cfg"), self._file_exists("setup.py")
        )

        return any(exists)

    async def is_requirements(self) -> bool:
        """
        Is the project a python app with a requirements file?

        Returns:
            bool: True if yes, else False.
        """
        exists = await asyncio.gather(
            self._file_exists("requirements.txt"),
            self._file_exists("requirements-dev.txt"),
        )

        return any(exists)

    async def has_pyproject_toml(self) -> bool:
        """
        Does the project have a `pyproject.toml` file.

        Returns:
            bool: True if yes, else False.
        """
        return await self._file_exists("pyproject.toml")

    async def is_conda(self) -> bool:
        """
        Is the project based on conda. The only reliable
        way of detecting this is looking for an `environment.yml`.

        Returns:
            bool: True if conda, else False.
        """
        return await self._file_exists("environment.yml")

    async def _specifies_build_tool(self, build_tool: str) -> bool:
        """
        Generalised method to check for a particular build tool
        in `pyproject.toml`

        Does more than a naive search for `build_tool`, actually checks the
        appropriate toml construction so if this method returns True, caller
        can be confident that `pyproject.toml` is valid.

        Args:
            build_tool (str): The build tool to check for e.g. `flit`, `poetry`.

        Returns:
            bool: True if `pyproject.toml` specifies that build tool, else False.
        """
        # If it doesn't have a pyproject.toml, bail early
        if not await self.has_pyproject_toml():
            return False

        async with aiofiles.open(self.local_path.joinpath("pyproject.toml")) as file:
            content = await file.read()
            toml = tomlkit.parse(content)

        if build_system := toml.get("build-system"):
            if build_backend := build_system.get("build-backend"):
                return build_tool in build_backend.strip().lower()

        return False

    async def is_poetry(self) -> bool:
        """
        Does the project specify a poetry build system

        Returns:
            bool: True if yes, else False.
        """
        return await self._specifies_build_tool("poetry")

    async def is_flit(self) -> bool:
        """
        Does the proeject specify a flit build system.

        Returns:
            bool: True if yes, else False.
        """
        return await self._specifies_build_tool("flit")

    async def dispatch_env(self, config: Config) -> Environment | None:
        """
        Returns the correct environment object for the calling `Repo`,
        or `None` if it cannot detect the environment.

        Therefore all usage should first check for `None`.

        Returns:
            Optional[Environment]: The correct environment object if it was
                able to detect, or `None`.
        """
        # This is where the magic happens for automatic environment detection
        # and installation

        # Each of the environment objects below implements the `Environment` Protocol
        # and has an `install_self` method that does the correct thing for it's environment

        # Check the existence of files concurrently because why not
        exists = await asyncio.gather(
            self.is_conda(),
            self.is_requirements(),
            self.is_setuptools(),
            self.is_poetry(),
            self.is_flit(),
        )

        conda, requirements, setuptools, poetry, flit = exists

        if conda:
            return Conda(
                root=self.local_path, environment_name=self.name, conda=config.conda_bin
            )
        elif requirements:
            return Requirements(root=self.local_path)
        elif setuptools:
            return Venv(root=self.local_path)
        elif poetry:
            return Poetry(root=self.local_path)
        elif flit:
            return Flit(root=self.local_path)
        else:
            # Could not autodetect, this is handled by the CLI
            return None
