"""
Module responsible for handling python virtual environments
in a project with a requirements.txt (or requirements_dev.txt)

Author: Tom Fleet
Created: 15/07/2021
"""

import subprocess
from pathlib import Path
from typing import List

from pytoil.environments.virtualenv import Venv


class ReqTxtEnv(Venv):
    """
    requirements.txt | requirements_dev.txt EnvManager class.
    """

    def __init__(self, project_path: Path) -> None:
        """
        Representation of a virtual environment in a python
        project with only a requirements.txt
        (or requirements_dev.txt).

        Because this is all standard python virtual environment stuff
        here we subclass from the `Venv` class so that all we have to
        tweak are the install methods.

        Args:
            project_path (Path): The root path of the current project.
        """
        super().__init__(project_path=project_path)

    @property
    def info_name(self) -> str:
        return "requirements file"

    def install_self(self) -> None:
        """
        Installs everything in the requirements file
        into the virtual environment.
        """
        # Before installing from a requirements file
        # ensure the virtual env exists
        if not self.exists():
            self.create()

        # Prefer requirements_dev if present because it will have everything
        if self.project_path.joinpath("requirements_dev.txt").exists():
            requirements_file = "requirements_dev.txt"
        elif self.project_path.joinpath(
            "requirements.txt"
        ).exists():  # pragma: no cover
            # Coverage isn't picking this up but it's definitely tested
            requirements_file = "requirements.txt"

        cmd: List[str] = [
            f"{self.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            f"{requirements_file}",
            "--quiet",
        ]

        subprocess.run(cmd, check=True, cwd=self.project_path)
