"""
The root CLI command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

from pathlib import Path

import click
import questionary
import rich.traceback

from pytoil import __version__
from pytoil.cli.bug import bug
from pytoil.cli.checkout import checkout
from pytoil.cli.config import config
from pytoil.cli.docs import docs
from pytoil.cli.find import find
from pytoil.cli.gh import gh
from pytoil.cli.info import info
from pytoil.cli.keep import keep
from pytoil.cli.new import new
from pytoil.cli.printer import printer
from pytoil.cli.pull import pull
from pytoil.cli.remove import remove
from pytoil.cli.show import show
from pytoil.config import Config, defaults

# So that if we do ever get a traceback, it uses rich to show it nicely
rich.traceback.install()


@click.group(
    commands={
        "checkout": checkout,
        "config": config,
        "docs": docs,
        "find": find,
        "gh": gh,
        "info": info,
        "new": new,
        "pull": pull,
        "remove": remove,
        "show": show,
        "keep": keep,
        "bug": bug,
    }
)
@click.version_option(version=__version__, prog_name="pytoil")
@click.pass_context
def main(ctx: click.Context) -> None:
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
        config = Config.load()
    except FileNotFoundError:
        interactive_config()
    else:
        if not config.can_use_api():
            printer.error(
                "You must set your GitHub username and personal access token to use API"
                " features.",
                exits=1,
            )
        # We have a valid config file at the right place so load it into click's
        # context and pass it down to all subcommands
        ctx.obj = config


def interactive_config() -> None:
    """
    Prompt the user with a series of questions
    to configure pytoil interactively.
    """
    printer.warn("No pytoil config file detected!")
    interactive: bool = questionary.confirm(
        "Interactively configure pytoil?", default=False, auto_enter=False
    ).ask()

    if not interactive:
        # User doesn't want to interactively walk through a config file
        # so just make a default and exit cleanly
        Config.helper().write()
        printer.good("I made a default file for you.")
        printer.note(
            f"It's here: {defaults.CONFIG_FILE}, you can edit it with `pytoil"
            " config edit``",
            exits=0,
        )
        return

    # If we get here, the user wants to interactively make the config
    projects_dir: str = questionary.path(
        "Where do you keep your projects?",
        default=str(defaults.PROJECTS_DIR),
        only_directories=True,
    ).ask()

    token: str = questionary.text("GitHub personal access token?").ask()

    username: str = questionary.text("What's your GitHub username?").ask()

    use_editor: bool = questionary.confirm(
        "Auto open projects in an editor?", default=False, auto_enter=False
    ).ask()

    if use_editor:
        editor: str = questionary.text("Name of the editor binary to use?").ask()
    else:
        editor = "None"

    git: bool = questionary.confirm(
        "Make git repos when creating new projects?", default=True, auto_enter=False
    ).ask()

    conda_bin: str = questionary.select(
        "Use conda or mamba for conda environments?",
        choices=("conda", "mamba"),
        default="conda",
    ).ask()

    config = Config(
        projects_dir=Path(projects_dir).resolve(),
        token=token,
        username=username,
        editor=editor,
        conda_bin=conda_bin,
        git=git,
    )

    config.write()

    printer.good("Config created")
    printer.note(f"It's available at {defaults.CONFIG_FILE}.", exits=0)
