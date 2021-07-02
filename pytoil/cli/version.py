"""
Keeps the Logo out of the way of any logic in root.py.

Author: Tom Fleet
Created: 02/07/2021
"""

import subprocess
from pathlib import Path

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


def get_git_revision() -> str:
    """
    Invokes git in a subprocess to get the revision SHA
    to display as part of the version string.

    Returns:
        str: Git rev SHA.
    """

    here = Path(__file__).parent.resolve()

    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, cwd=here
    )

    return out.stdout.decode("utf-8").strip()


def get_pytoil_version() -> str:
    """
    Gets the current pytoil __version__.

    Returns:
        str: __version__
    """
    return f"v{__version__}"


def version_callback(value: bool) -> None:
    """
    Callback responsible for printing the version info.
    """

    version_start = typer.style("version:\t", fg=typer.colors.CYAN)
    commit_start = typer.style("git commit:\t", fg=typer.colors.CYAN)

    version_msg = version_start + f"{get_pytoil_version()}"
    commit_msg = commit_start + f"{get_git_revision()}"

    if value:
        typer.echo(LOGO)
        typer.echo(version_msg)
        typer.echo(commit_msg)
        raise typer.Exit(0)
