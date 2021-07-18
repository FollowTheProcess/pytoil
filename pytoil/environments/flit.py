"""
Module responsible for creating and managing virtual environments
for flit.

This is done in a very similar way to `virtualenv.py` as flit
does not create it's own environments.

Author: Tom Fleet
Created: 13/07/2021
"""

import shutil
import subprocess
from pathlib import Path
from typing import List

from pytoil.environments.virtualenv import Venv
from pytoil.exceptions import FlitNotInstalledError


class FlitEnv(Venv):
    """
    Flit EnvManager class.
    """

    def __init__(self, project_path: Path) -> None:
        """
        Representation of a flit virtualenv.

        Actually not overtly different from the `Venv` class
        in `virtualenv.py` as flit uses standard python
        virtual environments.

        The main difference is found in install commands. Hence why
        we subclass from the standard `Venv` class here and other
        classes subclass from the `Environment` ABC.

        Args:
            project_path (Path): The root path of the current project.
        """
        super().__init__(project_path=project_path)

    @property
    def info_name(self) -> str:
        return "flit"

    def install_self(self) -> None:
        """
        Installs the current package.

        Raises:
            FlitNotInstalledError: If `flit` not installed.
        """

        if not bool(shutil.which("flit")):
            raise FlitNotInstalledError(
                "Flit not installed, cannot install flit based project."
            )

        # Unlike poetry, conda etc. flit does not make it's own virtual environment
        # we must make one here before installing the project
        if not self.exists():
            self.create()

        cmd: List[str] = [
            "flit",
            "install",
            "--deps",
            "develop",
            "--symlink",
            "--python",
            f"{self.executable}",
        ]

        # Here we must specify the cwd as flit will search for it's pyproject.toml
        subprocess.run(cmd, check=True, cwd=self.project_path, capture_output=True)
