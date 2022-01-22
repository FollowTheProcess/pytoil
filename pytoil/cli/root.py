"""
The root CLI command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import aiofiles.os
import asyncclick as click
import questionary
from wasabi import msg

from pytoil import __version__
from pytoil.cli import (
    cache,
    checkout,
    config,
    docs,
    find,
    gh,
    info,
    new,
    pull,
    remove,
    show,
)
from pytoil.config import Config, defaults


@click.group(
    commands=(
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
        cache.cache,
    )
)
@click.version_option(version=__version__, package_name="pytoil", prog_name="pytoil")
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
        interactive: bool = await questionary.confirm(
            "Interactively configure pytoil?", default=False, auto_enter=False
        ).ask_async()

        if not interactive:
            # User doesn't want to interactively walk through a config file
            # so just make a default and exit cleanly
            await Config.helper().write()
            msg.good(
                title="I made a default file for you",
                text=f"It's here: {defaults.CONFIG_FILE}",
                spaced=True,
            )
            msg.text("Tip: You can edit it with `pytoil config edit`.", exits=0)
            return

        # If we get here, the user wants to interactively make the config
        projects_dir: str = await questionary.path(
            "Where do you keep your projects?",
            default=str(defaults.PROJECTS_DIR),
            only_directories=True,
        ).ask_async()

        token: str = await questionary.text("GitHub personal access token?").ask_async()

        username: str = await questionary.text(
            "What's your GitHub username?"
        ).ask_async()

        vscode: bool = await questionary.confirm(
            "Do you use VSCode?",
            default=False,
            auto_enter=False,
        ).ask_async()

        code_bin = defaults.CODE_BIN

        if vscode:

            which_vscode: str = await questionary.select(
                "Which version of VSCode do you use?",
                choices=["stable", "insiders"],
                default="stable",
            ).ask_async()

            code_bin = (
                "code-insiders" if which_vscode == "insiders" else defaults.CODE_BIN
            )

        git: bool = await questionary.confirm(
            "Make git repos when creating new projects?", default=True, auto_enter=False
        ).ask_async()

        config = Config(
            projects_dir=Path(projects_dir),
            token=token,
            username=username,
            vscode=vscode,
            code_bin=code_bin,
            git=git,
        )

        await config.write()

        msg.good(
            "Config created", text=f"It's available at {defaults.CONFIG_FILE}.", exits=0
        )
        return

    else:
        # We have a valid config file at the right place so load it into click's
        # context and pass it down to all subcommands
        ctx.obj = config

        # Ensure the API cache dir exists
        if not await aiofiles.os.path.exists(defaults.CACHE_DIR):
            # List of all cache sub directories to also create
            children = [
                defaults.CACHE_DIR.joinpath("get_repos"),
                defaults.CACHE_DIR.joinpath("get_repo_names"),
                defaults.CACHE_DIR.joinpath("get_forks"),
                defaults.CACHE_DIR.joinpath("get_repo_info"),
            ]

            # Make them all
            await asyncio.gather(
                *[aiofiles.os.makedirs(child, exist_ok=True) for child in children]
            )
