"""
Keeps the Logo out of the way of any logic in root.py.

Author: Tom Fleet
Created: 02/07/2021
"""


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
        str: __version__
    """
    return f"v{__version__}"


def version_callback(value: bool) -> None:
    """
    Callback responsible for printing the version info.
    """

    version_start = typer.style("pytoil version:\t", fg=typer.colors.CYAN)

    version_msg = version_start + f"{get_pytoil_version()}"

    if value:
        typer.echo(LOGO)
        typer.echo(version_msg)
        raise typer.Exit(0)
