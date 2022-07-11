"""
Module responsible for handling conda environments.


Author: Tom Fleet
Created: 26/12/2021
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Union

import yaml

from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    EnvironmentAlreadyExistsError,
    EnvironmentDoesNotExistError,
    UnsupportedCondaInstallationError,
)

# Type alias
EnvironmentYml = dict[str, Union[list[str], str]]

CONDA = shutil.which("conda")


class Conda:
    def __init__(
        self,
        root: Path,
        environment_name: str,
        conda: str | None = CONDA,
    ) -> None:
        """
        Representation of a Conda managed virtual environment.

        Conda environments are simpler in a lot of ways because
        it's all managed under the hood by the `conda` command.

        We don't need to worry about interpreters or paths etc.
        Just the environment name is enough to identify it.

        Args:
            root (Path): The root directory of the project.
            environment_name (str): The name of the conda environment
            conda (Optional[str]): The conda binary. Defaults to shutil.which("conda")
        """
        self.root = root
        self.environment_name = environment_name
        self.conda = conda

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(root={self.root!r}, environment_name={self.environment_name!r},"
            f" conda={self.conda!r})"
        )

    __slots__ = ("root", "environment_name", "conda")

    @property
    def project_path(self) -> Path:
        return self.root.resolve()

    @property
    def executable(self) -> Path:
        envs_dir = self.get_envs_dir()
        return envs_dir.joinpath(f"{self.environment_name}/bin/python")

    @property
    def name(self) -> str:
        return "conda"

    @staticmethod
    def get_envs_dir() -> Path:
        """
        Tries to detect which anaconda/miniconda installation
        the user has by naively checking if the environment
        storage directories exist.

        Raises:
            UnsupportedCondaInstallationError: If no matches are found
                for known conda installations.

        Returns:
            Path: The path to the users conda
                environment storage directory.
        """
        # Map of all supported conda installations to their root directories
        supported: dict[str, Path] = {
            "anaconda": Path.home().joinpath("anaconda3"),
            "miniconda": Path.home().joinpath("miniconda3"),
            "miniforge": Path.home().joinpath("miniforge3"),
            "mambaforge": Path.home().joinpath("mambaforge"),
        }

        names = supported.keys()

        for _, directory in supported.items():
            if directory.exists() and directory.is_dir():
                return directory.joinpath("envs")

        raise UnsupportedCondaInstallationError(
            f"""Could not detect the type of conda
        installation present. Checked for: {names}"""
        )

    def exists(self) -> bool:
        """
        Checks whether the environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then the environment musty
        exist.
        """
        return self.executable.exists()

    def create(
        self, packages: Sequence[str] | None = None, silent: bool = False
    ) -> None:
        """
        Creates the conda environment described by the instance.

        Only default package is `python=3` which will cause conda to choose
        it's default python3.

        If packages are specified, these will be inserted into the conda create
        command.

        Args:
            packages (Optional[List[str]]): List of packages to install on creation.
                Defaults to None.

            silent (bool, optional): Whether to discard or display output.
                Defaults to False.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.
            EnvironmentAlreadyExistsError: If the conda environment already exists.
        """
        if not self.conda:
            raise CondaNotInstalledError

        if self.exists():
            raise EnvironmentAlreadyExistsError(
                f"Conda env: {self.environment_name!r} already exists"
            )

        cmd = [self.conda, "create", "-y", "--name", self.environment_name, "python=3"]

        if packages:
            cmd.extend(packages)

        subprocess.run(
            cmd,
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )

    @staticmethod
    def create_from_yml(project_path: Path, conda: str, silent: bool = False) -> None:
        """
        Creates a conda environment from the `environment.yml` contained
        in the root `project_path`

        Args:
            project_path (Path): Filepath to the project root.
            conda (str): The conda binary.
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.

        Raises:
            BadEnvironmentFileError: If `environment.yml` is malformed.
            EnvironmentAlreadyExistsError: If a conda environment of the same name
                exists on the system.
        """

        if not shutil.which(conda):
            raise CondaNotInstalledError

        # Ensure we have a fully resolved project path
        project_path = project_path.resolve()
        yml_file = project_path.joinpath("environment.yml")

        with open(yml_file) as file:
            env_dict: EnvironmentYml = yaml.safe_load(file)

        env_name = env_dict.get("name")
        if not isinstance(env_name, str):
            raise BadEnvironmentFileError(
                "The environment yml file has an invalid format. Cannot determine value"
                " for key: `name`."
            )

        env = Conda(root=project_path, environment_name=env_name)

        if env.exists():
            raise EnvironmentAlreadyExistsError(
                f"Conda env: {env_name!r} already exists."
            )
        # Can't use self.conda here as static method so just rely on $PATH
        subprocess.run(
            [conda, "env", "create", "--file", f"{yml_file}"],
            cwd=project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )

    def export_yml(self) -> None:
        """
        Exports an environment.yml file for the conda environment
        described by the instance.

        Raises:
            CondaNotInstalledError: If conda not installed.
            EnvironmentDoesNotExistError: If the environment does not exist.
        """
        if not self.conda:
            raise CondaNotInstalledError

        if not self.exists():
            raise EnvironmentDoesNotExistError(
                f"Conda env: {self.environment_name!r} does not exist. Create it first"
                " before exporting the environment file."
            )

        process = subprocess.run(
            [
                self.conda,
                "env",
                "export",
                "--from-history",
                "--name",
                self.environment_name,
            ],
            cwd=self.project_path,
            capture_output=True,
            encoding="utf-8",
        )

        yml_file = self.project_path.joinpath("environment.yml")

        with open(yml_file, mode="w", encoding="utf-8") as file:
            file.write(process.stdout)

    def install(self, packages: Sequence[str], silent: bool = False) -> None:
        """
        Installs `packages` into the conda environment described by
        the instance.

        Packages are passed straight through to conda so any versioning
        syntax will work as expected.

        Args:
            packages (List[str]): List of packages to install.
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.

        Raises:
            CondaNotInstalledError: If user does not have conda installed.
            EnvironmentDoesNotExistError: If the conda environment does not exist.
        """
        if not self.conda:
            raise CondaNotInstalledError

        if not self.exists():
            raise EnvironmentDoesNotExistError(
                f"Conda env: {self.environment_name!r} does not exist. Create it first"
                " before installing packages."
            )

        subprocess.run(
            [self.conda, "install", "-y", "--name", self.environment_name, *packages],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )

    def install_self(self, silent: bool = False) -> None:
        """
        Creates a conda environment from an environment.yml.

        This is conda's closest concept to `installing self`.

        Args:
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        if not self.conda:
            raise CondaNotInstalledError

        self.create_from_yml(
            project_path=self.project_path, conda=self.conda, silent=silent
        )
