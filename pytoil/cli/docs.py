"""
The pytoil docs command.

Author: Tom Fleet
Created: 25/06/2021
"""

import typer
from wasabi import msg

from pytoil.config import defaults

app = typer.Typer()


@app.command()
def docs() -> None:  # pragma: no cover
    """
    Open pytoil's documentation in your browser.

    Examples:

    $ pytoil docs
    """
    msg.info("Opening pytoil's docs in your browser...", spaced=True)
    typer.launch(url=defaults.PYTOIL_DOCS_URL)
