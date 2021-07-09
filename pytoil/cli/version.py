"""
Keeps the Logo out of the way of any logic in root.py.

Author: Tom Fleet
Created: 02/07/2021
"""


import platform
import sys
from typing import Dict

import typer

from pytoil import __version__

LOGO = r"""
██████╗ ██╗   ██╗████████╗ ██████╗ ██╗██╗
██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔═══██╗██║██║
██████╔╝ ╚████╔╝    ██║   ██║   ██║██║██║
██╔═══╝   ╚██╔╝     ██║   ██║   ██║██║██║
██║        ██║      ██║   ╚██████╔╝██║███████╗
╚═╝        ╚═╝      ╚═╝    ╚═════╝ ╚═╝╚══════╝

"""


def get_pytoil_version() -> str:
    """
    Gets the current pytoil __version__.

    Returns:
        str: v__version__
    """
    return f"v{__version__}"


def get_python_version() -> str:
    """
    Returns the python version used to call pytoil.

    Returns:
        str: Python version.
    """
    return sys.version.replace("\n", "").strip()


def version_callback(value: bool) -> None:
    """
    Callback responsible for printing the version info.
    """

    version_dict: Dict[str, str] = {
        "python version": get_python_version(),
        "pytoil version": get_pytoil_version(),
        "platform": platform.system(),
        "OS": platform.platform(),
        "arch": platform.machine(),
    }

    if value:
        typer.echo(LOGO)

        for key, val in version_dict.items():

            version_start = typer.style(f"{key}: ", fg=typer.colors.CYAN)
            version_msg = version_start + f"{val}"

            typer.echo(version_msg)
        raise typer.Exit(0)
