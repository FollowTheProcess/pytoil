"""
Module responsible for creating and managing conda environments.

Author: Tom Fleet
Created: 20/06/2021
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml

from pytoil.environments import Environment
from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    EnvironmentAlreadyExistsError,
    EnvironmentDoesNotExistError,
    UnsupportedCondaInstallationError,
)

# Type alias
EnvironmentYml = Dict[str, Union[List[str], str]]


class Conda(Environment):
    def __init__(
        self,
        name: str,
        project_path: Path,
        conda: Optional[str] = shutil.which("conda"),
    ) -> None:
        """
        Representation of a conda virtual environment.

        Conda environments are simpler in a lot of ways because
        it's all managed under the hood by the `conda` command.

        We don't need to worry about interpreters or paths etc.
        Just the environment name is enough to identify it.

        Args:
            name (str): The name of the conda environment.

            project_path (pathlib.Path): Path to the root dir
                of the associated project.

            conda (str, optional): The path to the conda executable.
                defaults to whatever `conda` is on $PATH.
        """
        self.name = name
        self._project_path = project_path
        self.conda = conda

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(name={self.name!r}, "
            + f"project_path={self.project_path!r}, "
            + f"conda={self.conda!r})"
        )

    @property
    def project_path(self) -> Path:
        return self._project_path

    @property
    def executable(self) -> Path:
        envs_dir = self.get_envs_dir()
        return envs_dir.joinpath(f"{self.name}/bin/python")

    def raise_for_conda(self) -> None:
        """
        Helper method which either raises if no `conda` found.
        Or does nothing if it is found.

        Because we end up relying on `conda` for most of the logic
        it makes sense to abstract this step.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH
        """
        if not self.conda:
            raise CondaNotInstalledError(
                """`conda` executable not installed or not found on $PATH.
            Check your installation."""
            )

    def exists(self) -> bool:
        """
        Determines whether a conda environment called `name`
        exists on the current system by checking if a valid
        interpreter exists inside the environments directory
        under that name.

        Returns:
            bool: True if the environment exists on system, else False.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.
        """

        self.raise_for_conda()

        return self.executable.exists()

    def create(self, packages: Optional[List[str]] = None) -> None:
        """
        Creates the conda environment described by the instance.

        Only default package is `python=3` which will cause conda to choose
        it's default python3.

        If packages are specified, these will be inserted into the conda create
        command.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.

            EnvironmentAlreadyExistsError: If the conda environment already exists.
        """

        self.raise_for_conda()

        if self.exists():
            raise EnvironmentAlreadyExistsError(
                f"Conda env: {self.name!r} already exists."
            )

        cmd: List[str] = [
            f"{self.conda}",
            "create",
            "-y",
            "--name",
            f"{self.name}",
            "python=3",
        ]

        if packages:
            cmd.extend(packages)

        try:
            _ = subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise

    @staticmethod
    def create_from_yml(project_path: Path) -> Conda:
        """
        Creates a conda environment from the `environment.yml`
        contained in the root `project_path`

        Args:
            fp (pathlib.Path): Filepath of the project root.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.

            FileNotFoundError: If the `environment.yml` file does not exist.

            BadEnvironmentFileError: If the `environment.yml` file is
                formatted incorrectly.

            EnvironmentAlreadyExistsError: If the conda environment described
                by the `environment.yml` file already exists on system.

        Returns:
            Conda: The returned Conda environment object for later use.
        """

        # Ensure we have a resolved project root filepath
        resolved_project_path = project_path.resolve()
        yml_file = resolved_project_path.joinpath("environment.yml")

        try:
            with open(yml_file) as f:
                env_dict: EnvironmentYml = yaml.full_load(f)
        except FileNotFoundError:
            raise

        env_name = env_dict.get("name")

        if not isinstance(env_name, str):
            raise BadEnvironmentFileError(
                """The environment yml file has an invalid format.
                Cannot determine the value for key: `name`."""
            )
        env = Conda(name=env_name, project_path=resolved_project_path)
        env.raise_for_conda()

        if env.exists():
            raise EnvironmentAlreadyExistsError(
                f"Conda env: {env.name!r} already exists."
            )
        try:
            # Can't use self.conda here as classmethod
            # so just rely on $PATH
            _ = subprocess.run(
                [
                    "conda",
                    "env",
                    "create",
                    "-y",
                    "--file",
                    f"{yml_file}",
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            raise

        return env

    def export_yml(self) -> None:
        """
        Exports an environment.yml file for the conda environment
        described by the instance.

        Raises:
            EnvironmentDoesNotExistError: If the conda env does not exist,
                an environment file cannot be created.
        """

        self.raise_for_conda()

        if not self.exists():
            raise EnvironmentDoesNotExistError(
                f"""Conda env: {self.name!r} does not exist.
        Create it first before exporting the environment file."""
            )

        cmd: List[str] = [
            f"{self.conda}",
            "env",
            "export",
            "--from-history",
            "--name",
            self.name,
        ]

        try:
            # Capture the output and redirect to the yml file
            # basically the python version of the shell's '>'
            yml_out = subprocess.run(
                cmd, check=True, capture_output=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError:
            raise
        else:
            yml_file = self.project_path.joinpath("environment.yml")
            with open(yml_file, mode="w", encoding="utf-8") as f:
                f.write(yml_out.stdout)

    def install(
        self,
        packages: List[str],
    ) -> None:
        """
        Installs `packages` into the conda environment
        described by `name`.

        Packages are passed straight through to conda so any versioning
        syntax will work as expected.

        Args:
            packages (List[str]): List of packages to install.
                If only one package, still must be a list
                e.g. ["numpy"],
        Raises:
            EnvironmentDoesNotExistError: If the conda environment does not exist.
        """

        self.raise_for_conda()

        if not self.exists():
            raise EnvironmentDoesNotExistError(
                f"""Conda env: {self.name} does not exist.
        Create it first before installing packages."""
            )

        # Install into specified env
        cmd: List[str] = [
            f"{self.conda}",
            "install",
            "-y",
            "--name",
            f"{self.name}",
        ]

        # Add specified packages
        cmd.extend(packages)

        try:
            _ = subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise

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
        supported: Dict[str, Path] = {
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
