"""
The pytoil root CLI command.

This module simply instantiates the base pytoil CLI command
and attaches it's direct subcommands and it's subcommand
groups.

Author: Tom Fleet
Created: 18/06/2021
"""


import typer

from pytoil.cli import checkout, config, docs, gh, info, new, pull, remove, show
from pytoil.cli.version import version_callback

# Create the root app
app = typer.Typer(name="pytoil", no_args_is_help=True)

# Attach immediate child commands
# this is a bit hacky but it lets us have one command per file
# which is a nicer design
app.registered_commands += (
    checkout.app.registered_commands
    + new.app.registered_commands
    + docs.app.registered_commands
    + gh.app.registered_commands
    + info.app.registered_commands
    + remove.app.registered_commands
    + pull.app.registered_commands
)

# Add the sub command groups
# these are commands with their own subcommands
app.add_typer(show.app, name="show")
app.add_typer(config.app, name="config")


# Callback for documentation only
@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Display pytoil version.",
        callback=version_callback,
        is_eager=True,
        show_default=False,
    )
) -> None:
    """
    Helpful CLI to automate the development workflow.

    - Create and manage your local and remote projects

    - Build projects from cookiecutter templates.

    - Easily create/manage virtual environments.

    - Minimal configuration required.
    """
