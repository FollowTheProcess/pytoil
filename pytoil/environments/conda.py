"""
Module managing Conda environments.

Author: Tom Fleet
Created: 07/03/2021
"""

import pathlib
import shutil
import subprocess
from typing import Dict, List, Optional, Union

import yaml

from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    UnknownCondaInstallationError,
    VirtualenvAlreadyExistsError,
    VirtualenvDoesNotExistError,
)


class CondaEnv:
    def __init__(self, name: str) -> None:
        """
        Representation of a conda virtual environment.

        Conda environments are simpler in a lot of ways because
        it's all managed under the hood by the `conda` command.

        We don't need to worry about interpreters or paths etc.
        Just the environment name is enough to identify it.

        Args:
            name (str): The name of the conda environment.
        """
        self.name = name

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(name={self.name!r})"

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
        exists on the current system by parsing the stdout of the
        `conda env list` command.

        Raises:
            CondaNotInstalledError: If `conda` not found on $PATH.
            CalledProcessError: If an unknown error occurs in the
                `conda env list` command.

        Returns:
            bool: True if the environment exists on system, else False.
        """

        self.raise_for_conda()

        try:
            envs = subprocess.run(
                ["conda", "env", "list"],
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
        except subprocess.CalledProcessError:
            raise
        else:
            return self.name.strip().lower() in envs.stdout.strip().lower()

    def create(self, packages: Optional[List[str]] = None) -> None:
        """
        Creates the conda environment described by the instance.

        If `packages` are specified, these will be included at creation.

        Only default package is `python=3` which will cause conda to choose
        it's default python3.

        Args:
            packages (Optional[List[str]], optional): List of valid packages
                for conda to install on environment creation. Passed through to
                conda so any versioning syntax will work as expected.
                Defaults to None.

        Raises:
            VirtualenvAlreadyExistsError: If the conda environment already exists.
        """

        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"Conda env: {self.name} already exists."
            )

        cmd: List[str] = ["conda", "create", "-y", "--name", f"{self.name}", "python=3"]

        if packages:
            cmd.extend(packages)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise

    @staticmethod
    def create_from_yml(fp: pathlib.Path) -> None:
        """
        Creates a conda environment from the `environment.yml`
        file passed as a pathlib.Path in `fp`.

        Args:
            fp (pathlib.Path): Filepath of the `environment.yml` file.

        Raises:
            FileNotFoundError: If the `environment.yml` file does not exist.
            BadEnvironmentFileError: If the `environment.yml` file is
                formatted incorrectly.
            VirtualenvAlreadyExistsError: If the conda environment described
                by the `environment.yml` file already exists on system.
        """

        # Ensure we have a resolved yml filepath
        resolved_fp = fp.resolve()

        try:
            with open(resolved_fp) as f:
                env_dict: Dict[str, Union[List[str], str]] = yaml.full_load(f)
        except FileNotFoundError:
            raise

        env_name = env_dict["name"]

        if not isinstance(env_name, str):
            raise BadEnvironmentFileError(
                """The environment yml file has an invalid format.
                Cannot determine the value for key: `name`."""
            )
        else:
            env = CondaEnv(name=env_name)

        if env.exists():
            raise VirtualenvAlreadyExistsError(f"Conda env: {env.name} already exists.")
        else:
            try:
                subprocess.run(
                    ["conda", "env", "create", "-y", "--file", f"{resolved_fp}"],
                    check=True,
                )
            except subprocess.CalledProcessError:
                raise

    def export_yml(self, fp: pathlib.Path) -> None:
        """
        Exports an environment.yml file for the conda environment
        described by the instance.

        Args:
            fp (pathlib.Path): Path to desired export location
                (excluding the filename).
                i.e. to get `/Users/me/projects/myproject/environment.yml`
                `fp` would be `/Users/me/projects/myproject`.

        Raises:
            VirtualenvDoesNotExistError: If the conda env does not exist,
                an environment file cannot be created.
        """

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
            yml_file = fp.joinpath("environment.yml")
            with open(yml_file, "w") as f:
                f.write(yml_out.stdout)

    def install(self, packages: List[str]) -> None:
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
