from enum import Enum

from pytoil.environments.abstract import Environment
from pytoil.environments.conda import Conda
from pytoil.environments.virtualenv import Venv

__all__ = [
    "Environment",
    "Venv",
    "Conda",
]


# Choice of virtual environments for a new project
class VirtualEnv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    venv = "venv"
    conda = "conda"
    none = "none"
