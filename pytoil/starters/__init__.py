from enum import Enum

from pytoil.starters.go import GoStarter
from pytoil.starters.python import PythonStarter
from pytoil.starters.rust import RustStarter

__all__ = [
    "PythonStarter",
    "GoStarter",
    "RustStarter",
]


class Starter(str, Enum):
    """
    Choice of starter templates.
    """

    python = "python"
    go = "go"
    rust = "rust"
    none = "none"
