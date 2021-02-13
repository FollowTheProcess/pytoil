"""
Main CLI module.

Author: Tom Fleet
Created: 04/02/2021
"""


from pprint import pprint
from typing import Tuple

import typer

from . import __version__

app = typer.Typer(name="pytoil", no_args_is_help=True)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


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
) -> None:  # pragma: no cover
    """
    Helpful CLI to automate the development workflow!
    """
    if version:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


@app.command()
def new(
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookie: str = typer.Option(
        None,
        "--cookiecutter",
        "-c",
        help="URL to a cookiecutter template repo from which to create the project.",
    ),
) -> None:
    """
    Create a new development project.

    If cookiecutter is specified it must be followed by a url to a
    valid cookiecutter template repo from which to construct the project.

    If not, it will simply create an empty project directory named
    PROJECT in your configured location.

    Examples:

    $ pytoil new my_cool_project

    OR

    $ pytoil new my_cool_project -c https://github.com/me/my_cookie_template.git
    """

    if cookie:
        typer.echo(f"Creating project: {project} with cookiecutter url: {cookie}")
        # cookiecutter(template=cookie, output_dir=PROJECTS_DIR)
    else:
        typer.echo(f"Creating project: {project}")


@app.command()
def resume(
    project: str = typer.Argument(default=None, help="Name of the project to resume."),
    url: str = typer.Option(
        None,
        "--url",
        "-u",
        help="URL of a project to resume work on (skips searching locally and GitHub).",
    ),
) -> None:
    """
    Resume a development project, either locally or from GitHub.

    pytoil will first check your configured projects directory
    for a matching name, falling back to searching your GitHub repositories,
    and finally asking you to specify what project you want to resume work on.
    e.g. if you want to work on a new repo owned by someone else.

    If resume finds the project locally, it will ensure any virtual environments
    are configured properly if required (e.g. a python project) and open the
    root of the project in your chosen editor.

    If resume finds a match, not locally but in your GitHub repos, it will
    first clone the repo to your projects directory before proceeding as if
    it existed locally.

    If neither of these finds a match, you will be asked to specify a url
    to a GitHub repo of the project you want to work on.

    You can also specify this at the beginning with the "-u/--url" option.
    If this is specified, the local and remote repo searching is skipped
    and the specified repo will be forked and cloned.

    Examples:

    $ pytoil resume my_cool_project

    OR

    $ pytoil resume --url https://github.com/someoneelse/their_cool_project.git
    """
    if url:
        typer.echo(f"Resuming project: {url}")
    else:
        typer.echo(f"Resuming project: {project}")


@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show currently set configuration.",
        show_default=False,
    ),
    set: Tuple[str, str] = typer.Option(
        [None, None],
        "--set",
        help="Set a configuration key: value pair.",
        show_default=False,
    ),
) -> None:
    """
    Interact with pytoil's configuration.

    "--show" will display the currently set configuration from your
    config file.

    "--set" accepts a valid key, value pair to set a configuration parameter.

    Examples:

    $ pytoil config --show

    OR

    $ pytoil config --set token "mynewtoken"
    """

    if show:
        # config = Config.get().to_dict()
        config = {"made up": "config", "is it made up": "yes", "really": "definitely"}
        typer.echo("Current pytoil config...\n")
        pprint(config)

    elif set:
        typer.echo(f"setting {set[0]} to {set[1]}")
