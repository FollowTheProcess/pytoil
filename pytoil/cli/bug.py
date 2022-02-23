"""
The pytoil bug command.


Author: Tom Fleet
Created: 23/02/2022
"""

from __future__ import annotations

import asyncclick as click

from pytoil.cli.printer import printer
from pytoil.config import defaults


@click.command()
async def bug() -> None:
    """
    Raise an issue about pytoil.

    The bug command let's you easily raise an issue on the pytoil
    repo. This can be a bug report, feature request, or a question!

    Examples:

    $ pytoil bug
    """
    printer.info("Opening pytoil's issues in your browser...")
    click.launch(url=defaults.PYTOIL_ISSUES_URL)
