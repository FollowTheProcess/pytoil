"""
Main CLI module.

Author: Tom Fleet
Created: 24/02/2021
"""


import shutil
from enum import Enum
from typing import List, Set

import typer
from cookiecutter.main import cookiecutter

from pytoil import __version__
from pytoil.cli import show, sync
from pytoil.cli.utils import env_dispatcher, get_local_project_set
from pytoil.config import Config
from pytoil.environments import CondaEnv, VirtualEnv
from pytoil.exceptions import RepoNotFoundError, VirtualenvAlreadyExistsError
from pytoil.repo import Repo
from pytoil.vscode import VSCode


class Venv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    virtualenv = "virtualenv"
    conda = "conda"


# Add all the subcommands
app = typer.Typer(name="pytoil", no_args_is_help=True)
app.add_typer(sync.app, name="sync")
app.add_typer(show.app, name="show")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


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


@app.command()
def new(
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookie: str = typer.Option(
        None,
        "--cookie",
        "-c",
        help="URL to a cookiecutter template repo from which to create the project.",
    ),
    venv: Venv = typer.Option(
        None,
        "--venv",
        "-v",
        help="Which type of virtual environment to create for the project.",
        case_sensitive=False,
        show_default=True,
    ),
) -> None:
    """
    Create a new development project locally.

    If cookiecutter is specified it must be followed by a url to a
    valid cookiecutter template repo from which to construct the project.

    If you have url abbreviations configured for cookiecutter, these
    will work as expected.

    If cookiecutter not specified, pytoil will simply create an empty project
    directory named PROJECT in your configured location.

    If venv is specified, it must be one of "virtualenv" or "conda" and the
    corresponding environment will be created for your project. If venv is not
    specified, environment creation will be skipped.

    You must have the conda package manager installed on your system to create conda
    environments. The conda environment will have the same name as your project. The
    virtualenv environment will be located in the root of your project under the folder
    '.venv'.

    Examples:

    $ pytoil new my_project

    $ pytoil new my_project -c https://github.com/me/my_cookie_template.git

    $ pytoil new my_project -v conda -c https://github.com/me/cookie.git
    """

    # Everything below requires a valid config
    config = Config.get()
    config.validate()

    # Create the project repo object
    # And the VSCode object
    repo = Repo(name=project)
    if config.vscode:
        vscode = VSCode(root=repo.path)

    if repo.exists_local():
        typer.secho(
            f"Project: {project!r} already exists locally at '{repo.path}'.",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use 'checkout'.")
        typer.echo(f"Example: '$ pytoil checkout {project}'.")
        raise typer.Abort()
    elif repo.exists_remote():
        typer.secho(
            f"Project: {project!r} already exists on GitHub.",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use 'checkout'.")
        typer.echo(f"Example: '$ pytoil checkout {project}'.")
        raise typer.Abort()

    # If we get here, project is okay to create

    if cookie:
        typer.secho(
            f"Creating project: {project!r} with cookiecutter template:"
            + f" {cookie!r}.",
            fg=typer.colors.BLUE,
            bold=True,
        )
        cookiecutter(template=cookie, output_dir=config.projects_dir)
        # NOTE: no repo init here a some cookiecutters do this with a hook
        # Most of mine do
    else:
        typer.secho(
            f"Creating project: {project!r} at '{repo.path}'.",
            fg=typer.colors.BLUE,
            bold=True,
        )
        # Create an empty project dir & git repo
        repo.path.mkdir()
        repo.init()

    if venv:
        if venv.value == venv.conda:
            typer.secho(
                f"Creating conda environment for {project!r}.",
                fg=typer.colors.BLUE,
                bold=True,
            )
            conda_env = CondaEnv(name=project, project_path=repo.path)
            try:
                conda_env.create(packages=config.common_packages)
            except VirtualenvAlreadyExistsError:
                typer.echo(f"Conda environment: {conda_env.name!r} already exists!")
                typer.echo(f"Using {conda_env.name!r} as the environment.")
            finally:
                if config.vscode:
                    typer.echo("Setting 'python.pythonPath' in VSCode workspace...")
                    vscode.set_python_path(conda_env.executable)
                    typer.echo(f"Opening {project!r} in VSCode...")
                    vscode.open()

        elif venv.value == venv.virtualenv:  # pragma: no cover
            # For some reason coverage isn't picking this up as tested
            # but it is: tests/cli/test_create.py
            # in several tests
            typer.secho(
                f"Creating virtualenv for {project!r}.",
                fg=typer.colors.BLUE,
                bold=True,
            )

            env = VirtualEnv(project_path=repo.path)
            env.create(packages=config.common_packages)

            typer.echo(
                "Ensuring seed packages (pip, setuptools, wheel) are up to date."
            )
            env.update_seeds()

            if config.vscode:
                typer.echo("Setting 'python.pythonPath' in VSCode workspace...")
                vscode.set_python_path(env.executable)
                typer.echo(f"Opening {project!r} in VSCode...")
                vscode.open()
    else:
        typer.echo("Virtual environment not requested. Skipping environment creation.")
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    typer.secho("Done!", fg=typer.colors.GREEN)


@app.command()
def checkout(
    project: str = typer.Argument(..., help="Name of the project to checkout.")
) -> None:
    """
    Checkout a development project, either locally or from GitHub.

    pytoil will first check your configured projects directory
    for a matching name, falling back to searching your GitHub repositories.

    If checkout finds the project locally, it will ensure any virtual environments
    are configured properly if required (e.g. a python project) and open the
    root of the project in your chosen editor.

    If checkout finds a match, not locally but in your GitHub repos, it will
    first clone the repo to your projects directory before proceeding as if
    it existed locally.

    If neither of these finds a match, an error message will be shown.

    Examples:

    $ pytoil checkout my_cool_project
    """

    # Everything below requires a valid config
    config = Config.get()
    config.validate()

    # Project exists either locally or on users GitHub
    # and is to be grabbed by name only
    repo = Repo(name=project)
    if config.vscode:
        vscode = VSCode(root=repo.path)

    if repo.exists_local():
        # Note we don't do any environment stuff here
        # chances are if it exists locally, this has already been done
        typer.secho(
            f"Project: {project!r} is available locally at" f" '{repo.path}'.",
            fg=typer.colors.BLUE,
            bold=True,
        )
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    elif repo.exists_remote():
        typer.secho(
            f"Project: {project!r} found on your GitHub. Cloning...",
            fg=typer.colors.BLUE,
            bold=True,
        )
        repo.clone()
        env = env_dispatcher(repo)
        if not env:
            typer.secho(
                "Unable to auto-detect virtual environment. Skipping.",
                fg=typer.colors.YELLOW,
            )
        else:
            typer.echo("Auto-creating correct virtual environment...")
            try:
                env.create(packages=config.common_packages)
            except VirtualenvAlreadyExistsError:
                typer.echo(
                    "Matching environment already exists. No need to create a new one!"
                )
            finally:
                if config.vscode:
                    typer.echo("Setting 'python.pythonPath' in VSCode workspace...")
                    vscode.set_python_path(env.executable)

        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    else:
        typer.secho(
            f"Project: {project!r} not found locally or on your GitHub.",
            fg=typer.colors.RED,
        )
        typer.echo(
            "Does the project exist? If not, create a new project:"
            + f" '$ pytoil new {project}'."
        )
        raise typer.Abort()


@app.command()
def remove(
    projects: List[str] = typer.Argument(..., help="Name of the project(s) to remove."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove project without prompting for confirmation.",
        show_default=False,
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Remove all projects from local directory.",
        show_default=False,
    ),
) -> None:
    """
    Deletes projects from your local filesystem.

    Deletion is done recursively, roughly equivalent to '$ rm -r {project}'.

    User will be prompted for confirmation unless "--force/-f" flag is used.

    Examples:

    $ pytoil remove my_project

    $ pytoil remove project1 project2 project3

    $ pytoil remove --force my_project
    """

    # Everything below needs a valid config
    config = Config.get()
    config.validate()

    # Set because we don't care about sorting
    # but we want fast membership checking
    local_projects: Set[str] = get_local_project_set(config.projects_dir)

    if all_:

        to_delete: Set[str] = local_projects

        if not force:
            typer.confirm(
                "This will remove all of your projects. Are you okay?", abort=True
            )

    else:

        for project in projects:
            if project not in local_projects:
                typer.secho(
                    f"Project: {project!r} not found in local filesystem.",
                    fg=typer.colors.RED,
                )
                raise typer.Abort()

        to_delete = {project for project in projects}

        if not force:
            # Confirm with user and abort if they say no
            typer.confirm(
                f"This will remove {to_delete} from your local filesystem."
                + " Are you sure?",
                abort=True,
            )

    # If user specifies force flag, just go ahead and remove
    for project in to_delete:
        typer.secho(f"Removing project: {project!r}.", fg=typer.colors.YELLOW)
        shutil.rmtree(config.projects_dir.joinpath(project))

    typer.secho("Done!", fg=typer.colors.GREEN)


@app.command()
def info(
    project: str = typer.Argument(..., help="Name of the project to fetch info for.")
) -> None:
    """
    Show useful information about a project.

    If the requested project is local only, a
    small subset of info will be shown to do with
    the local directory.

    However if the project is available on GitHub
    a more comprehensive info set is shown.

    Examples:

    $ pytoil info my_project
    """

    config = Config.get()
    config.validate()

    repo = Repo(name=project)

    try:
        info_dict = repo.info()
    except RepoNotFoundError:
        typer.secho(
            f"Project: {project!r} not found locally or on GitHub.", fg=typer.colors.RED
        )
        raise typer.Abort()
    else:
        typer.secho(f"\nInfo for: {project!r}\n", fg=typer.colors.BLUE, bold=True)
        for key, val in info_dict.items():
            typer.echo(f"{key}: {val}")


@app.command()
def config() -> None:
    """
    Display pytoil's configuration.

    pytoil's config file is ~/.pytoil.yml.
    """
    # Get config but don't raise on UNSET
    try:
        config = Config.get()
    except FileNotFoundError:
        typer.secho("No config file yet!", fg=typer.colors.YELLOW)
        typer.echo("Making you a default one...")
        config = Config()
        config.write()
    else:
        typer.secho("\nCurrent pytoil config:", fg=typer.colors.BLUE, bold=True)
        typer.echo("")
        config.show()


# All typer/click internal stuff here, no point in us testing this really
@app.command()
def docs() -> None:  # pragma: no cover
    """
    Open pytoil's documentation in your browser.
    """

    docs_url: str = "https://FollowTheProcess.github.io/pytoil/"

    typer.echo("Opening pytoil's documentation in your browser...")
    typer.launch(url=docs_url)


# No cover for same reason as above
@app.command()
def gh(
    project: str = typer.Argument(
        ..., help="The name of the project to open on GitHub."
    )
) -> None:  # pragma: no cover
    """
    Opens a specified project on GitHub in your browser.
    """
    config = Config.get()
    config.validate()

    project_url: str = f"https://github.com/{config.username}/{project}"

    typer.echo(f"Opening {project!r} in your browser...")
    typer.launch(url=project_url)
