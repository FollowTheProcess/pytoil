"""
Module responsible for interacting with local/remote projects.

Author: Tom Fleet
Created: 19/06/2021
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import toml

from pytoil.api import API
from pytoil.environments import Conda, Environment, Venv
from pytoil.exceptions import RepoNotFoundError


class Repo:
    def __init__(self, owner: str, name: str, local_path: Path) -> None:
        """
        Representation of a local/remote project.

        Args:
            owner (str): The owner (i.e. GitHub username)
            name (str): Project name
            local_path (Path): The path this repo would have on the local
                filesystem, whether it currently exists or not.
        """
        self.owner = owner
        self.name = name
        self.local_path = local_path

        self.clone_url = f"https://github.com/{self.owner}/{self.name}.git"
        self.html_url = f"https://github.com/{self.owner}/{self.name}"

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(owner={self.owner!r}, "
            + f"name={self.name!r}, "
            + f"local_path={self.local_path!r})"
        )

    def exists_local(self) -> bool:
        """
        Determines whether or not a Repo exists
        on the local filesystem

        Returns:
            bool: True if exists locally, else False.
        """
        return self.local_path.exists()

    def exists_remote(self, api: API) -> bool:
        """
        Determines whether or not a Repo exists
        on GitHub.

        It does this simply by making a GET request
        for the Repo in question and looking at the response
        code.

        Args:
            api (API): pytoil API object.

        Returns:
            bool: True if exists remote, else False.
        """
        try:
            # Capture any response and throw it away to avoid
            # accidental printing
            _ = api.get_repo(self.name)
        except httpx.HTTPStatusError:
            return False
        else:
            return True

    def info(self, api: API) -> Dict[str, Any]:
        """
        Returns summary information about the repo
        from the API or Path.stat.

        Prefers the API info as it is more detailed.
        Will fall back to Path.stat only if the project
        is not available remotely.

        Args:
            api (API): GitHub API object.

        Returns:

            Dict[str, Union[str, int]]: Summary info.
        """

        info_dict: Dict[str, Any] = {}

        # Path.stat returns a UNIX timestamp for dates/times
        str_time_format: str = r"%Y-%m-%d %H:%M:%S"

        if self.exists_remote(api=api):
            # If remote, the API does all the work
            info_dict.update(api.get_repo_info(repo=self.name))
            info_dict["remote"] = True
            info_dict["local"] = self.exists_local()
        elif self.exists_local():
            # If local, we can get a bit of info from os.stat
            info_dict.update(
                {
                    "name": self.local_path.name,
                    "created_at": datetime.utcfromtimestamp(
                        self.local_path.stat().st_ctime
                    ).strftime(str_time_format),
                    "updated_at": datetime.utcfromtimestamp(
                        self.local_path.stat().st_mtime
                    ).strftime(str_time_format),
                    "size": self.local_path.stat().st_size,
                    "local": True,
                    "remote": self.exists_remote(api=api),
                },
            )
        else:
            raise RepoNotFoundError(
                f"Repo: {self.name!r} does not exist locally or remotely."
            )

        return info_dict

    def file_exists(self, file: str) -> bool:
        """
        Helper method to determine whether or not
        the repo root directory contains `file`.

        Args:
            file (str): Name of the file, relative
                to `self.local_path`.

        Returns:
            bool: True if exists, else False.
        """
        return self.local_path.joinpath(file).exists()

    def is_setuptools(self) -> bool:
        """
        Is the project based on setuptools,
        i.e. does it have a 'setup.cfg' or a 'setup.py'

        Returns:
            bool: True if setuptools, else False.
        """

        return self.file_exists("setup.cfg") or self.file_exists("setup.py")

    def has_pyproject_toml(self) -> bool:
        """
        Does the project have a 'pyproject.toml' file.

        Returns:
            bool: True if yes, else False.
        """

        return self.file_exists("pyproject.toml")

    def is_conda(self) -> bool:
        """
        Is the project based on conda,
        the only way really of detecting this automatically
        is to look for an 'environment.yml'

        Returns:
            bool: True if conda, else False.
        """
        return self.file_exists("environment.yml")

    def _specifies_build_tool(self, build_tool: str) -> bool:
        """
        Generalised method to check for a particular
        build tool specification in pyproject.toml.

        Does more than a naive search for `build_tool`, actually
        checks the appropriate toml construction so if this
        method returns True, caller can be confident that
        the pyproject.toml is valid.

        Args:
            build_tool (str): The build tool to check for
                e.g. 'flit', 'poetry'

        Returns:
            bool: True if pyproject.toml specifies
                that build tool, else False.
        """

        # First check if it even has a pyproject.toml
        if not self.has_pyproject_toml():
            return False

        toml_dict = toml.load(self.local_path.joinpath("pyproject.toml"))
        build_system = toml_dict.get("build-system")
        # No build system means no PEP517
        if not build_system:
            return False

        build_backend: str = build_system.get("build-backend")
        # No build backend means a bad toml file
        # also no PEP517
        if not build_backend:
            return False

        # Now we know the toml file is valid
        # check if it specifies the build tool in question
        return build_tool in build_backend.strip().lower()

    def is_poetry(self) -> bool:
        """
        Does the project specify a poetry build_system.

        Returns:
            bool: True if yes, else False
        """

        return self._specifies_build_tool("poetry")

    def is_flit(self) -> bool:
        """
        Does the project specify a flit build_system.

        Returns:
            bool: True if yes, else False
        """

        return self._specifies_build_tool("flit")

    def dispatch_env(self) -> Optional[Environment]:
        """
        Returns the correct environment
        object for the calling `Repo` instance. Or `None` if it cannot
        detect the environment.

        Therefore all usage should first check for `None`.

        Returns:
            Optional[BaseEnvironment]: Either the correct environment
                object if it was able to detect. Or None.
        """

        if self.is_conda():
            return Conda(name=self.name, project_path=self.local_path)
        elif self.is_setuptools():
            return Venv(project_path=self.local_path)
        else:
            return None
