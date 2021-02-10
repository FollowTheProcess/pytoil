"""
Module responsible for the creation and management
of virtualenvs.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib
import shutil
import subprocess
from typing import List, Optional, Union

import virtualenv

from .exceptions import (
    CondaNotInstalledError,
    MissingInterpreterError,
    TargetDirDoesNotExistError,
    VirtualenvAlreadyExistsError,
)


class VirtualEnv:
    def __init__(self, basepath: pathlib.Path, name: str = ".venv") -> None:
        """
        Representation of a virtualenv.

        The path to the virtualenv directory is accessible through the
        `.path` property which returns a pathlib.Path pointing to the
        virtualenv directory.

        Once the instantiated virtualenv has been created, its `.executable`
        property (also a pathlib.Path) will point to the python executable
        of the newly created virtualenv.

        Until creation, the instantiated virtualenv's `.executable` is None.

        Args:
            basepath (pathlib.Path): The root path of the current project.
            name (str, optional): The name of the virtualenv directory.
                Defaults to ".venv".
        """
        self.basepath = basepath
        self.name = name
        self._path: pathlib.Path = self.basepath.joinpath(self.name)
        self._executable: Optional[pathlib.Path] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(basepath={self.basepath!r}, name={self.name!r})"
        )

    @property
    def path(self) -> pathlib.Path:
        """
        The path of the virtualenv folder.
        i.e the joined rootdir and name.
        """
        return self._path

    @property
    def executable(self) -> Union[pathlib.Path, None]:
        """
        The path to the virtualenv's python executable.
        """
        return self._executable

    @executable.setter
    def executable(self, value: pathlib.Path) -> None:
        self._executable = value

    def basepath_exists(self) -> bool:
        return self.basepath.exists()

    def exists(self) -> bool:
        return self.path.exists()

    def raise_for_executable(self) -> None:
        """
        Helper method analagous to requests `raise_for_status`.

        Should be called before any method that is supposed to act
        from within a virtual environment.

        A virtualenvs executable is only created if all the checks in
        `.create()` pass.

        This method is a convenient way of checking all those conditions
        by proxy in one step. If the property `self.executable` is not None,
        then the executable is valid.

        Raises:
            MissingInterpreterError: If `self.executable` is not found.
        """

        if not self.executable:
            raise MissingInterpreterError(
                f"""Virtualenv: {self.path!r} does not exist. Cannot install
                until it has been created. Create by using the `.create()` method."""
            )
        else:
            return None

    def create(self) -> None:
        """
        Create a new virtualenv in `basepath` with `name`
        and update the `executable` property with the newly
        created virtualenv's python.

        Raises:
            VirtualenvAlreadyExistsError: If virtualenv with `path` already exists.
            TargetDirDoesNotExistError: If basepath does not exist.
        """
        if self.exists():
            raise VirtualenvAlreadyExistsError(
                f"Virtualenv with path: {self.path!r} already exists"
            )
        elif not self.basepath_exists():
            raise TargetDirDoesNotExistError(
                f"The directory: {self.basepath!r} does not exist."
            )
        else:
            # Create a new virtualenv at `path`
            virtualenv.cli_run([f"{self.path}"])
            # Update the instance executable with the newly created one
            # resolve so can be safely invoked later
            self.executable = self.path.joinpath("bin/python").resolve()

    def update_seeds(self) -> None:
        """
        VirtualEnv will install 'seed' packages to a new
        environment: `pip`, `setuptools` and `wheel`.

        It is good practice to keep these packages fully up to date
        this method does exactly that by invoking pip from
        the virtualenvs executable.

        This is equivalent to running:
        `python -m pip install --upgrade pip setuptools wheel`
        from the command line with the virtualenv activated.
        """

        # Validate the executable
        self.raise_for_executable()

        try:
            # Don't need to specify a 'cwd' because we have a resolved interpreter
            subprocess.run(
                [
                    f"{str(self.executable)}",
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "pip",
                    "setuptools",
                    "wheel",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            raise

    def install(
        self,
        packages: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        editable: bool = False,
    ) -> List[str]:
        """
        Generic `pip install` method.

        If a list of packages is specified, the method is
        analagous to calling `pip install *packages` from within
        the virtual environment. The packages are effectively passed straight
        through to pip so any versioning syntax e.g. `>=3.2.6` will work as
        expected. If `packages` is specified, `prefix` and `editable` must not be.

        A prefix is the syntax used if a project has declared groups of dependencies
        as labelled groups e.g. `.[all]` or `.[dev]` in files like setup.py,
        pyproject.toml etc. If a prefix is specified, this is used for the install.
        If `prefix` is specified, packages must not but editable can be.

        If editable is specified (only applicable on installs like `.[dev]`)
        this is analogous to calling `pip install -e {something}`.
        If `editable` is specified, packages must not be.

        Args:
            packages (Optional[List[str]], optional): A list of valid packages
                to install. Analogous to simply calling `pip install *packages`.
                `packages` cannot be used in tandem with `prefix` or `editable`.
                If only 1 package, still must be in a list e.g. `["black"]`.
                Defaults to None.

            prefix (Optional[str], optional): A valid shorthand prefix e.g. `.[dev]`.
                `prefix` cannot be used in tandem with `packages` but may be used
                with `editable` for example like `pip install -e .[dev]` for installing
                the current project and its specified `dev` dependencies.
                Defaults to None.

            editable (bool, optional): Whether to install `prefix` in editable mode
                `pip install -e`. Cannot be used in tandem with `packages`.
                Defaults to False.

        Raises:
            ValueError: If mutually exclusive arguments are used together,
                or if no arguments are used at all.

        Returns:
            List[str]: The command sent to pip. Side effect, primarily only used
                for testing.
        """

        if packages and (prefix or editable):
            # If packages, prefix and editable must be default
            raise ValueError(
                "Argument `packages` may not be used with `prefix` or `editable`."
            )

        if not packages and not prefix and not editable:
            # Must pass at least one
            raise ValueError(
                "At least one of `packages`, `prefix` or `editable` must be specified."
            )

        # Ensure seed packages are updated, also checks interpreter
        self.update_seeds()

        cmd: List[str] = [f"{str(self.executable)}", "-m", "pip", "install"]

        if packages:
            # i.e. `python -m pip install requests pandas numpy` etc.
            cmd.extend(packages)
        elif prefix:  # pragma: no cover
            # We specify no cover here because this logic is actually
            # tested in the call to subprocess.run below in
            # test_env.py::test_virtualenv_install_passes_correct_command
            # but coverage does not recognise a call by proxy.
            # i.e. `python -m pip install .[dev]`
            cmd.append(prefix)
            if editable:
                # i.e. `python -m pip install -e .[dev]`
                cmd.insert(4, "-e")

        # Run the constructed pip command
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            raise
        else:
            return cmd


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
