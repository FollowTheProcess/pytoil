"""
The pytoil docs command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
from wasabi import msg

from pytoil.config import defaults


@click.command()
async def docs() -> None:
    """
    Open pytoil's documentation in your browser.

    Examples:

    $ pytoil docs
    """
    msg.info("Opening pytoil's docs in your browser...")
    click.launch(url=defaults.PYTOIL_DOCS_URL)
