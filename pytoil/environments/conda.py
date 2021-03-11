"""
Module managing Conda environments.

Author: Tom Fleet
Created: 07/03/2021
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
from typing import Dict, List, Union

import yaml

from pytoil.environments import BaseEnvironment
from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    UnknownCondaInstallationError,
    VirtualenvAlreadyExistsError,
    VirtualenvDoesNotExistError,
)


class CondaEnv(BaseEnvironment):
    def __init__(self, name: str, project_path: pathlib.Path) -> None:
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
        """
        self.name = name
        self._project_path = project_path.resolve()

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(name={self.name!r}, "
            + f"project_path={self._project_path!r})"
        )

    @property
    def project_path(self) -> pathlib.Path:
        return self._project_path

    @property
    def executable(self) -> pathlib.Path:
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
        if not bool(shutil.which("conda")):
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

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.

        Returns:
            bool: True if the environment exists on system, else False.
        """

        self.raise_for_conda()

        return self.executable.exists()

    def create(self) -> None:
        """
        Creates the conda environment described by the instance.

        Only default package is `python=3` which will cause conda to choose
        it's default python3.

        Raises:
            VirtualenvAlreadyExistsError: If the conda environment already exists.
        """

        self.raise_for_conda()

        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"Conda env: {self.name} already exists."
            )

        cmd: List[str] = ["conda", "create", "-y", "--name", f"{self.name}", "python=3"]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise

    @staticmethod
    def create_from_yml(project_path: pathlib.Path) -> CondaEnv:
        """
        Creates a conda environment from the `environment.yml`
        contained in the root `project_path`

        Args:
            fp (pathlib.Path): Filepath of the project root.

        Raises:
            FileNotFoundError: If the `environment.yml` file does not exist.
            BadEnvironmentFileError: If the `environment.yml` file is
                formatted incorrectly.
            VirtualenvAlreadyExistsError: If the conda environment described
                by the `environment.yml` file already exists on system.
        """

        # Ensure we have a resolved project root filepath
        resolved_project_path = project_path.resolve()
        yml_file = resolved_project_path.joinpath("environment.yml")

        try:
            with open(yml_file) as f:
                env_dict: Dict[str, Union[List[str], str]] = yaml.full_load(f)
        except FileNotFoundError:
            raise

        env_name = env_dict.get("name")

        if not isinstance(env_name, str):
            raise BadEnvironmentFileError(
                """The environment yml file has an invalid format.
                Cannot determine the value for key: `name`."""
            )
        else:
            env = CondaEnv(name=env_name, project_path=resolved_project_path)
            env.raise_for_conda()

        if env.exists():
            raise VirtualenvAlreadyExistsError(f"Conda env: {env.name} already exists.")
        else:
            try:
                subprocess.run(
                    [
                        "conda",
                        "env",
                        "create",
                        "-y",
                        "--file",
                        f"{yml_file}",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError:
                raise

        return env

    def export_yml(self) -> None:
        """
        Exports an environment.yml file for the conda environment
        described by the instance.

        Raises:
            VirtualenvDoesNotExistError: If the conda env does not exist,
                an environment file cannot be created.
        """

        self.raise_for_conda()

        if not self.exists():
            raise VirtualenvDoesNotExistError(
                f"""Conda env: {self.name} does not exist.
        Create it first before exporting the environment file."""
            )

        cmd: List[str] = [
            "conda",
            "env",
            "export",
            "--from-history",
            "--name",
            self.name,
        ]

        try:
            yml_out = subprocess.run(
                cmd, check=True, capture_output=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError:
            raise
        else:
            yml_file = self.project_path.joinpath("environment.yml")
            with open(yml_file, "w") as f:
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
            VirtualenvDoesNotExistError: If the conda environment does not exist.
        """

        self.raise_for_conda()

        if not self.exists():
            raise VirtualenvDoesNotExistError(
                f"""Conda env: {self.name} does not exist.
        Create it first before installing packages."""
            )

        # Install into specified env
        cmd: List[str] = ["conda", "install", "--name", f"{self.name}", "-y"]

        # Add specified packages
        cmd.extend(packages)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise

    @staticmethod
    def get_envs_dir() -> pathlib.Path:
        """
        Tries to detect which anaconda/miniconda installation
        the user has by naively checking if the environment
        storage directories exist.

        Raises:
            UnknownCondaInstallationError: If neither ~/anaconda3 or
                ~/miniconda3 exist or are not directories.

        Returns:
            pathlib.Path: The path to the users conda
                environment storage directory.
        """

        # As far as I'm aware, there are only 2 possible locations
        miniconda = pathlib.Path.home().joinpath("miniconda3/envs")
        anaconda = pathlib.Path.home().joinpath("anaconda3/envs")

        if miniconda.exists() and miniconda.is_dir():
            return miniconda
        elif anaconda.exists() and anaconda.is_dir():
            return anaconda
        else:
            raise UnknownCondaInstallationError(
                "Could not autodetect the conda environments directory."
            )
