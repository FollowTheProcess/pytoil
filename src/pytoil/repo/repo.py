"""
Module responsible for interacting with local/remote projects.


Author: Tom Fleet
Created: 22/12/2021
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import humanize
import rtoml

from pytoil.environments import Conda, Environment, Flit, Poetry, Requirements, Venv
from pytoil.exceptions import RepoNotFoundError

if TYPE_CHECKING:
    from pathlib import Path

    from pytoil.api import API
    from pytoil.config import Config


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

    def exists_local(self) -> bool:
        """
        Determines whether or not a `Repo` exists
        on the local filesystem.

        Returns:
            bool: True if exists locally, else False.
        """
        return self.local_path.exists()

    def exists_remote(self, api: API) -> bool:
        """
        Determines whether or not a `Repo` exists
        on GitHub.

        Args:
            api (API): The API object.

        Returns:
            bool: True if exists remote, else False.
        """
        return api.check_repo_exists(owner=self.owner, name=self.name)

    def _local_info(self) -> dict[str, Any] | None:  # pragma: no cover
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
                    datetime.utcfromtimestamp(self.local_path.stat().st_ctime),
                    when=datetime.utcnow(),
                ),
                "Updated": humanize.naturaltime(
                    datetime.utcfromtimestamp(self.local_path.stat().st_mtime),
                    when=datetime.utcnow(),
                ),
                "Local": True,
            }
        except FileNotFoundError:
            return None

    def _remote_info(self, api: API) -> dict[str, Any] | None:
        """
        Return remote API information for the repo.
        """
        return api.get_repo_info(self.name)

    def info(self, api: API) -> dict[str, Any]:
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

        exists_remote = self.exists_remote(api=api)
        exists_local = self.exists_local()

        if exists_remote:
            if remote_info := self._remote_info(api=api):
                info.update(remote_info)
            # Might also exist locally
            info.update({"Local": exists_local})
        elif exists_local:
            if local_info := self._local_info():
                info.update(local_info)
            # We know it doesn't exist on GitHub if we got here
            info.update({"Remote": False})
        else:
            raise RepoNotFoundError(
                f"Repo: {self.name!r} does not exist locally or on GitHub."
            )

        return info

    def _file_exists(self, file: str) -> bool:
        """
        Convenience method to determine whether or not
        the repo root directory contains `file`.

        Args:
            file (str): Name of the file.

        Returns:
            bool: True if exists, else False.
        """
        return self.local_path.joinpath(file).exists()

    def is_setuptools(self) -> bool:
        """
        Is the project based on setuptools, i.e. does it
        have a `setup.cfg` or `setup.py`.

        Returns:
            bool: True if setuptools, else False.
        """
        conditions = (
            self._file_exists("setup.cfg"),
            self._file_exists("setup.py"),
            self._specifies_build_tool("setuptools.build_meta"),
        )

        return any(conditions)

    def is_requirements(self) -> bool:
        """
        Is the project a python app with a requirements file?.

        Returns:
            bool: True if yes, else False.
        """
        conditions = (
            self._file_exists("requirements.txt"),
            self._file_exists("requirements-dev.txt"),
        )

        return any(conditions)

    def has_pyproject_toml(self) -> bool:
        """
        Does the project have a `pyproject.toml` file.

        Returns:
            bool: True if yes, else False.
        """
        return self._file_exists("pyproject.toml")

    def is_conda(self) -> bool:
        """
        Is the project based on conda. The only reliable
        way of detecting this is looking for an `environment.yml`.

        Returns:
            bool: True if conda, else False.
        """
        return self._file_exists("environment.yml")

    def _specifies_build_tool(self, build_tool: str) -> bool:
        """
        Generalised method to check for a particular build tool
        in `pyproject.toml`.

        Does more than a naive search for `build_tool`, actually checks the
        appropriate toml construction so if this method returns True, caller
        can be confident that `pyproject.toml` is valid.

        Args:
            build_tool (str): The build tool to check for e.g. `flit`, `poetry`.

        Returns:
            bool: True if `pyproject.toml` specifies that build tool, else False.
        """
        # If it doesn't have a pyproject.toml, bail early
        if not self.has_pyproject_toml():
            return False

        contents = self.local_path.joinpath("pyproject.toml").read_text(
            encoding="utf-8"
        )
        toml = rtoml.loads(contents)

        if (build_system := toml.get("build-system")) and (
            build_backend := build_system.get("build-backend")
        ):
            return build_tool in build_backend.strip().lower()

        return False

    def is_pep621(self) -> bool:
        """
        Does the project comply with PEP 621.
        """
        if not self.has_pyproject_toml():
            return False

        contents = self.local_path.joinpath("pyproject.toml").read_text(
            encoding="utf-8"
        )
        toml = rtoml.loads(contents)

        if not toml.get("build-system"):
            return False

        if not toml.get("project"):
            return False

        return True

    def is_poetry(self) -> bool:
        """
        Does the project specify a poetry build system.

        Returns:
            bool: True if yes, else False.
        """
        return self._specifies_build_tool("poetry")

    def is_flit(self) -> bool:
        """
        Does the project specify a flit build system.

        Returns:
            bool: True if yes, else False.
        """
        return self._specifies_build_tool("flit")

    def is_hatch(self) -> bool:
        """
        Does the project specify a hatch build system.

        Returns:
            bool: True if yes, else False.
        """
        return self._specifies_build_tool("hatchling.build")

    def dispatch_env(self, config: Config) -> Environment | None:
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

        if self.is_conda():
            return Conda(
                root=self.local_path, environment_name=self.name, conda=config.conda_bin
            )

        if self.is_requirements():
            return Requirements(root=self.local_path)

        if self.is_setuptools() or self.is_pep621():
            return Venv(root=self.local_path)

        if self.is_poetry():
            return Poetry(root=self.local_path)

        if self.is_flit():
            return Flit(root=self.local_path)

        # Could not autodetect, this is handled by the CLI
        return None
