"""
Main CLI module.

Author: Tom Fleet
Created: 04/02/2021
"""


from enum import Enum
from typing import Tuple

import typer
from cookiecutter.main import cookiecutter

from pytoil.repo import Repo

from . import __version__
from .config import Config
from .env import CondaEnv, VirtualEnv


class Venv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    virtualenv = "virtualenv"
    conda = "conda"
    none = None


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
    Helpful CLI to automate the development workflow.

    Create, and easily resume work on, local or remote
    development projects.

    Build projects from cookiecutter templates.

    Automatically creates the correct virtual environment
    for your project.

    Minimal configuration required.
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
    venv: Venv = typer.Option(
        ...,
        "--venv",
        "-v",
        help="Which type of virtual environment to create for the project.",
        prompt=True,
        case_sensitive=False,
    ),
) -> None:
    """
    Create a new development project.

    If cookiecutter is specified it must be followed by a url to a
    valid cookiecutter template repo from which to construct the project.

    If you have url abbreviations configured for cookiecutter, these
    will work as expected.

    If cookiecutter not specified, pytoil will simply create an empty project
    directory named PROJECT in your configured location.

    If venv is specified, it must be one of "virtualenv" or "conda" and the
    corresponding environment will be created for your project.

    You may also specify venv as "none" in which case, environment creation will be
    skipped. The inputs to venv are not case sensitive so "none" works just as well
    as "None". If you do not specify venv, it will be prompted for.

    You must have the conda package manager installed on your system to create conda
    environments. The conda environment will have the same name as your project. The
    virtualenv environment will be located in the root of your project under the folder
    '.venv'.


    Examples:

    $ pytoil new my_cool_project

    OR

    $ pytoil new my_cool_project -c https://github.com/me/my_cookie_template.git

    OR

    $ pytoil new my_cool_project -v virtualenv -c https://github.com/me/cookie.git
    """

    config = Config.get()
    config.raise_if_unset()

    # Create the project repo object
    repo = Repo(name=project)

    if repo.exists_local():
        typer.secho(
            f"Project: {project!r} already exists locally at {str(repo.path)!r}",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use pytoil resume.")
        typer.echo(f"Example: '$ pytoil resume {project}'.")
        raise typer.Abort()

    if cookie:
        typer.secho(
            f"Creating project: {project!r} with cookiecutter template: {cookie!r}.",
            fg=typer.colors.BLUE,
            bold=True,
        )
        cookiecutter(template=cookie, output_dir=config.projects_dir)
    else:
        typer.secho(
            f"Creating project: {project!r} at {str(repo.path)!r}",
            fg=typer.colors.BLUE,
            bold=True,
        )
        repo.path.mkdir()

    if venv.value == venv.conda:
        typer.secho(
            f"Creating conda environment for {project!r}.",
            fg=typer.colors.BLUE,
            bold=True,
        )
        conda_env = CondaEnv(name=project)
        conda_env.create()

        typer.echo("Exporting 'environment.yml' file.")
        conda_env.export_yml(fp=repo.path)

    elif venv.value == venv.virtualenv:
        typer.secho(
            f"Creating virtualenv environment for {project!r}.",
            fg=typer.colors.BLUE,
            bold=True,
        )

        env = VirtualEnv(basepath=repo.path)
        env.create()

        typer.echo("Ensuring seed packages (pip, setuptools, wheel) are up to date.")
        # env.update_seeds()

    elif venv.value == venv.none:
        typer.secho(
            "Virtual environment not requested. Skipping environment creation.",
            fg=typer.colors.YELLOW,
        )
    else:
        # This should never happen as we're using an Enum
        # But just incase, let's abort
        typer.secho("Unrecognised option for venv.", fg=typer.colors.RED)
        raise typer.Abort()

    typer.secho("Done!", fg=typer.colors.GREEN)


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

    config = Config.get()
    config.raise_if_unset()

    if url:
        typer.secho(
            f"Resuming project from url: {url}", fg=typer.colors.BLUE, bold=True
        )
        repo = Repo.from_url(url=url)
        if repo.owner == config.username:
            typer.echo(f"It looks like you own the repo: '{repo.owner}/{repo.name}'.")
            typer.echo(f"Cloning '{repo.owner}/{repo.name}'")
            repo.clone()
            typer.secho(
                f"Project: {project!r} now available locally at {str(repo.path)!r}.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.echo(
                f"It looks like the repo: '{repo.owner}/{repo.name}' isn't yours."
            )
            typer.secho(
                f"Creating fork: '{config.username}/{repo.name}'",
                fg=typer.colors.BLUE,
                bold=True,
            )
            user_fork = repo.fork()
            typer.secho(
                f"Your fork: {user_fork!r} has been requested.", fg=typer.colors.GREEN
            )
            typer.echo(
                "FYI: Forking happens asynchronously and your fork may not be available"
                + " to clone for a few moments."
            )

    else:
        typer.secho(f"Resuming project: {project!r}\n", fg=typer.colors.BLUE, bold=True)

        repo = Repo(name=project)

        if repo.exists_local():
            typer.secho(
                f"Project: {project!r} is already available locally at"
                f" {str(repo.path)!r}.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(
                f"Project: {project!r} not found locally. Checking user's GitHub...\n",
                fg=typer.colors.YELLOW,
            )
            if repo.exists_remote():
                typer.echo(f"Project: {project!r} found on user's GitHub. Cloning...\n")
                repo.clone()
                typer.secho(
                    f"\nProject: {project!r} now available locally at"
                    f" {str(repo.path)!r}.",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"Project: {project!r} not found on user's GitHub.\n",
                    fg=typer.colors.RED,
                )
                typer.echo(
                    f"Does the project exist? If not, create a new project:"
                    f" '$ pytoil new {project}'."
                    "Or specify a url to a repo directly with the --url option:"
                    " '$pytoil new --url https://github.com/someone/coolproject.git"
                )


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

    Schema:

    username (string): Your GitHub username.
    e.g. 'FollowTheProcess'

    token (string): Your GitHub personal access token.
    e.g. '917hab19asbso181h91y' (totally made up)

    projects_dir (string): The absolute path to where you keep development projects.
    e.g. '/Users/you/projects'

    Usage:

    $ pytoil config --show

    OR

    $ pytoil config --set token "mynewtoken"
    """

    # Get the config but don't raise on UNSET
    config = Config.get()

    if show:
        typer.secho("\nCurrent pytoil config:", fg=typer.colors.BLUE, bold=True)
        config.show()

    elif set:
        old_config_dict = config.to_dict()
        key, val = set

        if key not in old_config_dict.keys():
            typer.secho(
                f"Key: {key!r} is not a valid pytoil config key.", fg=typer.colors.RED
            )
            raise typer.Abort()

        new_config_dict = old_config_dict.copy()
        new_config_dict.update({key: val})

        typer.secho(f"Key: {key!r} not a valid configuration key.", fg=typer.colors.RED)

        new_config = Config(**new_config_dict)
        new_config.write()

        typer.secho(
            f"Configuration updated: {key!r} is now {val!r}.", fg=typer.colors.GREEN
        )
