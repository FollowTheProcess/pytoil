"""
The pytoil docs command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click

from pytoil.cli.printer import printer
from pytoil.config import defaults


@click.command()
async def docs() -> None:
    """
    Open pytoil's documentation in your browser.

    Examples:

    $ pytoil docs
    """
    printer.info("Opening pytoil's docs in your browser...")
    click.launch(url=defaults.PYTOIL_DOCS_URL)
