"""
The root CLI command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
from wasabi import msg

from pytoil import __version__
from pytoil.cli import checkout, config, docs, find, gh, info, new, pull, remove, show
from pytoil.config import Config, defaults


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
@click.pass_context
async def main(ctx: click.Context) -> None:
    """
    Helpful CLI to automate the development workflow.

    - Create and manage your local and remote projects

    - Build projects from cookiecutter templates.

    - Easily create/manage virtual environments.

    - Minimal configuration required.
    """
    # Load the config once on launch of the app and pass it down to the child commands
    # through click's context
    try:
        config = await Config.load()
    except FileNotFoundError:
        msg.warn("No pytoil config file detected!")
        await Config.helper().write()
        msg.good(
            f"I made one for you, its here: {defaults.CONFIG_FILE}",
            spaced=True,
            exits=0,
        )
    else:
        ctx.obj = config
