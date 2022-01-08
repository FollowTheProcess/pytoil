"""
The root CLI command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click

from pytoil import __version__
from pytoil.cli import checkout, config, docs, find, gh, info, new, pull, remove, show


@click.group(
    commands=[
        checkout.checkout,
        config.config,
        docs.docs,
        find.find,
        gh.gh,
        info.info,
        new.new,
        pull.pull,
        remove.remove,
        show.show,
    ]
)
@click.version_option(version=__version__)
async def main() -> None:
    """
    Helpful CLI to automate the development workflow.

    - Create and manage your local and remote projects

    - Build projects from cookiecutter templates.

    - Easily create/manage virtual environments.

    - Minimal configuration required.
    """
